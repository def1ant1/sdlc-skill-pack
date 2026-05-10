---
name: audit-trail
description: Immutable, tamper-evident audit log of all platform actions, decisions, and data-access events for compliance evidence and forensic investigation.
metadata:
  version: "0.1.0"
  category: governance
  owner: platform
  maturity: alpha
  dependencies: []

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Append-only, cryptographically verifiable audit log for the Apotheon platform.
Every system action, human decision, data access, configuration change, and
workflow event is recorded as a structured audit entry. Entries are hash-chained
(each entry includes the SHA-256 of the previous entry) so any tampering is
immediately detectable. The audit trail is the primary evidence source for
`compliance-runtime` and the first artifact requested during regulatory audits.

## Activation Triggers

- Any workflow step completes or fails (automatic — emitted by `skill_activity`)
- A HITL gate is triggered, approved, or rejected
- A connector accesses an external system (CRM, ITSM, analytics)
- A configuration or policy change is applied
- `compliance-runtime` requests evidence for a specific control
- A user queries or exports audit records (access is itself audited)
- A scheduled integrity check runs (hash-chain verification)

## Execution Protocol

### 1. Write path — record an audit entry

Accept a structured event and append it to the audit log:

```
AuditEntry:
  entry_id:       UUID (deterministic: uuid5(NAMESPACE_URL, actor+action+timestamp))
  prev_hash:      SHA-256 of the previous entry's canonical JSON (chain integrity)
  timestamp:      ISO 8601 UTC
  actor:          "system:<skill_name>" | "human:<user_id>" | "connector:<name>"
  action:         verb — "executed", "approved", "rejected", "accessed", "modified"
  resource:       "<resource_type>/<resource_id>"  (e.g. "workflow/RUN-1234")
  outcome:        "success" | "failure" | "pending"
  risk_level:     "low" | "L1" | "L2" | "L3"
  metadata:       arbitrary key-value pairs (skill output hash, connector endpoint, etc.)
  entry_hash:     SHA-256 of this entry's canonical JSON (self-referential integrity)
```

### 2. Read path — query audit records

Support structured queries for compliance evidence retrieval:

- **By resource**: all events affecting a specific workflow, connector, or skill
- **By actor**: all actions taken by a specific user or system component
- **By time range**: events within a compliance evaluation window
- **By risk level**: L2/L3 events only (for HITL audit reports)
- **By action**: e.g. all "approved" or "rejected" HITL decisions

### 3. Integrity verification

On demand (or scheduled), verify the hash chain:

```
for each entry (oldest to newest):
    assert entry.prev_hash == SHA-256(canonical_json(prior_entry))
    assert entry.entry_hash == SHA-256(canonical_json(entry without entry_hash))
```

Report any broken links as a `tamper_detected` event (which is itself audited).

### 4. Evidence export

For compliance reviews, export a filtered set of entries as:
- **NDJSON** — one entry per line, suitable for SIEM ingestion
- **CSV** — human-readable for auditor spreadsheets
- **PDF report** — summarized evidence package with chain-of-custody attestation

## Output Format

### Audit entry (write confirmation)

```yaml
audit_write:
  entry_id: "AUD-20260508-a1b2c3d4"
  timestamp: "2026-05-08T22:45:00Z"
  actor: "system:cloud-deployment"
  action: "executed"
  resource: "workflow/RUN-1778280307-ef1ece72"
  outcome: "success"
  risk_level: "L3"
  prev_hash: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  entry_hash: "sha256:a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
```

### Query result

```yaml
audit_query:
  query:
    resource: "workflow/RUN-1778280307-ef1ece72"
    time_range: ["2026-05-08T00:00:00Z", "2026-05-09T00:00:00Z"]
  result_count: 4
  chain_intact: true
  entries:
    - entry_id: "AUD-20260508-a1b2c3d4"
      timestamp: "2026-05-08T22:45:00Z"
      actor: "system:cloud-deployment"
      action: "executed"
      outcome: "success"
```

### Integrity report

```yaml
integrity_check:
  checked_at: "2026-05-08T23:00:00Z"
  entries_verified: 1204
  chain_intact: true
  tamper_detected: false
  oldest_entry: "2026-01-01T00:00:00Z"
  newest_entry: "2026-05-08T22:59:59Z"
```

## Integration Points

| Caller | How audit-trail is used |
|---|---|
| `compliance-runtime` | Queries entries as evidence for control evaluation |
| `skill_activity` | Emits an entry after every skill execution |
| `hitl_handler` | Emits entries on gate trigger, approval, and rejection |
| `base_connector` | Emits entries on every external API call |
| `governance` | Reads L2/L3 entries for policy violation detection |
| `executive-reporting` | Aggregates audit data for board-level risk reports |

## References

- `references/audit-entry-schema.md` — canonical field definitions and validation rules
- `references/chain-integrity-spec.md` — hash-chain algorithm and verification procedure
- `references/evidence-export-formats.md` — NDJSON, CSV, and PDF report specifications
- `references/retention-policy.md` — per-framework retention requirements (SOC2: 1yr, HIPAA: 6yr, etc.)