# Recovery Strategies Reference

## Failure Classification Tree

```
Failure Detected
├── Heartbeat missing (> 30s)
│   ├── Node still reachable → RESUME from latest checkpoint
│   └── Node unreachable → REPLAY from parent checkpoint on healthy node
├── Step exception raised
│   ├── Transient (network timeout, rate limit, 5xx) → RETRY (up to 3x)
│   ├── Resource (OOM, quota exceeded) → PAUSE + QUOTA_REQUEST
│   ├── Permanent (logic error, schema mismatch, 4xx) → ROLLBACK + POST_MORTEM
│   └── Authorization (403, permission denied) → ESCALATE to hitl-dashboard
├── State corruption detected (hash mismatch)
│   ├── Latest checkpoint corrupt → Try N-1 checkpoint
│   ├── N-1 also corrupt → REPLAY from parent goal checkpoint
│   └── All checkpoints corrupt → FLAG for FULL_RESTART
└── Operator-initiated → Select strategy per operator instruction
```

---

## Recovery Strategy Definitions

### RETRY

**When to use:** Transient failures — network timeout, rate limit (429), temporary
service unavailability (503). The underlying cause is expected to resolve without
intervention.

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| max_attempts | 3 | Maximum retry attempts before escalating |
| initial_backoff_ms | 500 | Initial wait before first retry |
| backoff_multiplier | 2.0 | Exponential backoff multiplier |
| max_backoff_ms | 30,000 | Maximum wait between retries (30s) |
| jitter_fraction | 0.1 | Random jitter added to prevent thundering herd |

**Retry budget:** No more than 10 total retries across all steps in a single workflow
execution. If budget exhausted, escalate to ROLLBACK.

---

### RESUME

**When to use:** Workflow is paused (heartbeat loss, resource exhaustion, planned
suspension) but the checkpoint is valid and the failure is resolved.

**Protocol:**
1. Verify latest checkpoint integrity (SHA-256 hash match)
2. Deserialize workflow context from checkpoint payload
3. Restore all variable bindings and step completion map
4. Re-enter execution at `step_index + 1` (next uncompleted step)
5. Re-register all pending tasks that were in the queue at checkpoint time

**Idempotency requirement:** Steps resumed from checkpoint must use their original
idempotency keys. External actions with confirmed prior completions are skipped.

---

### REPLAY

**When to use:** Latest checkpoint is corrupt or unavailable; execution must restart
from a prior known-good state using the recorded event log.

**Protocol:**
1. Locate the nearest valid ancestor checkpoint (walk back through checkpoint registry)
2. Restore state from ancestor checkpoint
3. Replay all subsequent steps using recorded inputs from the event-bus event log
4. Suppress live side effects during replay (no emails, no external API writes) unless
   explicitly marked as idempotent-safe
5. Verify replay outputs match recorded outputs within the configured tolerance

**Divergence tolerance:** If any step output diverges by more than 5% from the recorded
output (for numeric metrics) or is semantically different (for text outputs), PAUSE replay
and escalate to hitl-dashboard.

---

### ROLLBACK

**When to use:** Permanent failure — logic error, schema mismatch, data validation
failure, or unrecoverable step exception. The workflow cannot safely continue; completed
steps must be undone.

**Protocol:**
1. Halt further step execution immediately
2. Walk the completed step list in reverse order
3. For each completed step with a registered compensation action, execute the compensation
4. Steps without compensation actions are logged as non-reversible and flagged in the
   post-mortem
5. Emit `workflow.rolled_back` event with list of compensated and non-compensated steps
6. Trigger POST_MORTEM workflow

**Rollback budget:** Maximum 30 minutes for rollback execution. If rollback exceeds budget,
ESCALATE for manual intervention.

---

### ESCALATE

**When to use:** Authorization failure, unrecoverable multi-strategy failure, or operator-
specified escalation requirement. Human decision is required.

**Protocol:**
1. Suspend the workflow (no further automated execution)
2. Emit `workflow.escalated` event
3. Create a hitl-dashboard notification with:
   - Workflow ID and current state
   - Failure classification and evidence
   - Recovery strategies attempted and their outcomes
   - Recommended human action options
4. Wait for operator response; timeout after 4 hours triggers a repeat alert
5. On operator response: execute the operator-selected action (resume / rollback / terminate)

---

## Strategy Selection Decision Matrix

| Failure Type | First Strategy | If First Fails | If Second Fails |
|---|---|---|---|
| Network timeout | RETRY | RESUME | ESCALATE |
| Rate limit (429) | RETRY (with longer backoff) | PAUSE | ESCALATE |
| OOM / quota | PAUSE + QUOTA_REQUEST | RESUME (after quota granted) | ESCALATE |
| Logic error | ROLLBACK | — | ESCALATE |
| Schema mismatch | ROLLBACK | — | ESCALATE |
| Authorization | ESCALATE | — | — |
| Checkpoint corrupt (latest) | RESUME (from N-1) | REPLAY | FULL_RESTART |
| All checkpoints corrupt | ESCALATE | — | — |
| Heartbeat loss (node up) | RESUME | REPLAY | ESCALATE |
| Heartbeat loss (node down) | REPLAY (new node) | ESCALATE | — |

---

## Post-Mortem Template

Triggered automatically on ROLLBACK or FULL_RESTART completion:

```yaml
post_mortem:
  workflow_id: "WF-YYYYMMDD-NNN"
  failure_timestamp: "ISO8601"
  failure_type: "permanent | corruption | ..."
  root_cause: "Free text description"
  impact:
    steps_completed: N
    steps_rolled_back: N
    non_compensated_steps: [list]
    data_mutations_irreversible: [list]
  recovery_timeline:
    - timestamp: "ISO8601"
      action: "RETRY attempt 1"
      outcome: "failed"
    - timestamp: "ISO8601"
      action: "ROLLBACK initiated"
      outcome: "completed"
  prevention_recommendations: [list]
  owner: "agent_id or operator"
```