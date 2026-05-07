# Checkpoint Schema Reference

## Overview

Defines the complete checkpoint payload format, storage backend configurations, retention
policy, and idempotency protocol for the checkpoint-management skill.

---

## Checkpoint Payload Schema

```yaml
checkpoint:
  # Identity
  checkpoint_id: "CHK-20260507-001234"    # CHK-YYYYMMDD-NNN monotonic
  workflow_id: "WF-20260507-042"
  step_index: 7                             # Index of last completed step
  parent_checkpoint_id: "CHK-20260507-001233"  # Previous checkpoint for chain

  # Integrity
  state_hash: "sha256:abc123..."            # SHA-256 of variables_payload only
  payload_hash: "sha256:def456..."          # SHA-256 of full serialized payload
  compression_algorithm: "zstd"            # none | gzip | zstd

  # Storage
  storage_backend: "redis"                  # redis | postgres | s3
  storage_key: "ckpt/WF-20260507-042/CHK-20260507-001234.zstd"
  size_bytes: 24576

  # Timestamps
  created_at: "2026-05-07T14:23:00.123Z"
  expires_at: "2026-05-14T14:23:00.123Z"   # null for archival checkpoints

  # Execution context
  workflow_context:
    step_completion_map:                    # Boolean map of completed steps
      0: true
      1: true
      2: true
      3: true
      4: true
      5: true
      6: true
      7: true
    variable_bindings:                      # Current workflow variable state
      result_a: "..."
      intermediate_data: "..."
    pending_task_queue:                     # Tasks not yet dispatched
      - task_id: "TASK-008"
        step_index: 8
        skill: "code-review"
        inputs: {}
    actor_session_state:                    # Per-actor session data
      "agent-id-001":
        session_token: "..."
        context_window_tokens: 4096
    idempotency_keys:                       # Keys for completed external actions
      "STEP-005-COMMIT": "confirmed"
      "STEP-006-NOTIFY": "confirmed"
```

---

## Storage Backends

### Redis (Active Tier)

- **Purpose:** Hot checkpoints for actively executing workflows
- **TTL:** 7 days
- **Max payload size:** 10 MB (use S3 for larger)
- **Key pattern:** `ckpt:{workflow_id}:{checkpoint_id}`
- **Replication:** Redis Cluster with 3 replicas minimum

```yaml
backend_config:
  type: redis
  cluster_url: "redis-cluster.internal:6379"
  ttl_seconds: 604800    # 7 days
  serialization: "msgpack+zstd"
  max_size_bytes: 10485760
```

### PostgreSQL (Warm Tier)

- **Purpose:** Checkpoints for long-running or recently completed workflows
- **Retention:** 90 days
- **Max payload size:** 50 MB (BYTEA column with compression)
- **Promoted from:** Redis when workflow is suspended > 24h

```yaml
backend_config:
  type: postgres
  connection_string: "postgresql://ckpt-rw@pg-primary.internal:5432/checkpoints"
  table: "workflow_checkpoints"
  retention_days: 90
  compression: true
```

### S3 (Archival Tier)

- **Purpose:** Long-term archival, compliance, replay source for historical workflows
- **Retention:** 1 year minimum (governed by data retention policy)
- **Max payload size:** Unlimited
- **Promoted from:** PostgreSQL when workflow age > 90 days

```yaml
backend_config:
  type: s3
  bucket: "apotheon-checkpoints-archive"
  prefix: "checkpoints/{year}/{month}/{workflow_id}/"
  storage_class: "STANDARD_IA"
  retention_years: 1
  encryption: "aws:kms"
```

---

## Retention Policy

| Workflow Status | Retention Rule |
|---|---|
| Active (running) | All checkpoints retained |
| Suspended | Last 5 checkpoints retained; older pruned |
| Completed successfully | Last 1 checkpoint retained for 30 days |
| Failed (resolved) | All checkpoints retained for 90 days |
| Failed (unresolved) | All checkpoints retained indefinitely |
| Audit hold | All checkpoints retained per legal hold duration |

**Pruning frequency:** Retention check runs every 6 hours. Pruning is deferred for
checkpoints that are referenced by an active replay operation.

---

## Idempotency Protocol

Idempotency keys prevent duplicate execution of side-effecting steps on retry or replay.

**Key format:** `{workflow_id}:{step_index}:{action_type}:{content_hash[:8]}`

**Example:** `WF-20260507-042:5:send_notification:a1b2c3d4`

**Key lifecycle:**
1. Key is generated before the external action is attempted
2. Key is stored in the `idempotency_keys` map in the checkpoint payload
3. On retry or replay: if key exists with status `confirmed`, skip the action
4. If key exists with status `pending`, check the external system before retrying
5. Keys are retained for the full checkpoint lifetime

**Status values:**
- `pending` — action was initiated but confirmation not yet received
- `confirmed` — action completed and confirmed by the external system
- `failed` — action failed; safe to retry with a new key

---

## Integrity Verification

Two separate hashes are maintained:

| Hash | Covers | Purpose |
|---|---|---|
| `state_hash` | `variable_bindings` only | Detect state corruption without re-reading full payload |
| `payload_hash` | Full serialized checkpoint | Full integrity verification for storage corruption detection |

Verification procedure on load:
1. Compute SHA-256 of the retrieved payload bytes
2. Compare to stored `payload_hash` — mismatch indicates storage corruption
3. Deserialize and compute SHA-256 of `variable_bindings` section
4. Compare to stored `state_hash` — mismatch indicates partial write corruption
5. If either check fails: mark checkpoint as CORRUPT, try N-1 checkpoint