# Checkpoint Schema

## Overview

Checkpoints are durable snapshots of workflow execution state written by `checkpoint-management`
and read by `runtime-recovery` and `workflow-replay`. Every checkpoint is self-describing
and integrity-protected.

---

## Checkpoint Payload Schema

```yaml
checkpoint:
  # Identity
  checkpoint_id: "CHK-YYYYMMDD-NNN"
  workflow_id: "WF-YYYYMMDD-NNN"
  step_index: N                        # step number completed before this checkpoint
  step_id: "<step identifier>"         # human-readable step name
  version: "1"                         # incremented on each checkpoint for same workflow

  # Timing
  created_at: "ISO8601 UTC"
  workflow_started_at: "ISO8601 UTC"
  elapsed_ms: N

  # State
  status: "step_completed | pre_step | manual"
  variables:                           # all workflow context variables at checkpoint time
    key: value
    ...
  pending_tasks: []                    # tasks queued but not yet started
  completed_steps: ["step-1", "step-2"]
  failed_steps: []

  # Actor context
  actor:
    type: "skill | agent | system"
    id: "<actor identifier>"
  correlation_id: "<parent workflow or request id>"

  # Integrity
  state_hash: "<SHA-256 of serialized variables>"
  payload_hash: "<SHA-256 of full checkpoint payload>"
  signing_key_id: "<key used for HMAC if enabled>"

  # Storage metadata
  storage_backend: "redis | s3 | postgres | filesystem"
  storage_key: "<backend-specific key>"
  compressed: true
  compression_algorithm: "zstd"
  payload_size_bytes: N
```

---

## Checkpoint Event Log Format

Each step in the checkpoint event log records what happened between checkpoints:

```yaml
checkpoint_event:
  checkpoint_id: "CHK-YYYYMMDD-NNN"
  event_sequence: N
  events:
    - event_id: "uuid4"
      event_type: "workflow.step_completed"
      step_id: "<step>"
      timestamp: "ISO8601"
      inputs_hash: "<sha256>"
      outputs_hash: "<sha256>"
      actor: "<actor id>"
      side_effects:
        - type: "api_call | db_write | file_write | message_sent"
          target: "<target identifier>"
          idempotency_key: "<key for replay deduplication>"
```

Side effects are recorded to enable idempotent replay (the `workflow-replay` skill skips
re-executing side effects that already have a recorded idempotency key).

---

## Storage Backends

| Backend | Use Case | Retention | Performance |
|---|---|---|---|
| Redis | Active workflows (hot) | TTL: 7 days | <5ms read/write |
| PostgreSQL | Completed workflows (warm) | 90 days | <50ms read |
| S3-compatible | Long-term archive (cold) | 1 year+ | <500ms read |
| Filesystem | Local dev and testing | Manual | varies |

**Tiering policy:**
- Active workflow: Redis
- Completed within 24h: Redis → PostgreSQL migration
- Completed >24h: PostgreSQL → S3 archive after 90 days

---

## Checkpoint Retention Policy

| Workflow Status | Checkpoints Retained |
|---|---|
| Active | All checkpoints |
| Completed | Last 3 checkpoints |
| Failed (unresolved) | All checkpoints (pending post-mortem) |
| Failed (resolved) | Last checkpoint only |
| Archived | Final checkpoint only |

---

## Recovery Checkpoint Selection

When selecting a checkpoint to recover from:

1. Load checkpoint registry for workflow-id
2. Filter to checkpoints with `status: step_completed` (exclude mid-step checkpoints)
3. Verify `payload_hash` integrity
4. Select most recent valid checkpoint
5. If most recent checkpoint is corrupt: try N-1, N-2, … until valid checkpoint found
6. If no valid checkpoint exists: report `runtime-recovery` that full restart is required

---

## Idempotency Guarantee

Checkpoints support exactly-once execution semantics via idempotency keys:

- Each side effect (API call, DB write, message) records an `idempotency_key`
- During replay, the replay engine checks if each side effect's key already exists in the log
- If found: skip re-execution; use recorded result
- If not found: execute and record

This prevents duplicate API calls, double-sends, and duplicate writes during recovery.