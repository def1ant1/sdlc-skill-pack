# Recovery Runbook

## Overview

This runbook guides `runtime-recovery` through failure classification and recovery strategy
selection for failed or interrupted workflows.

---

## Failure Classification Tree

```
Workflow failure detected
│
├── Is heartbeat missing?
│   ├── YES → Node or process failure
│   │   ├── Last checkpoint < 5 min ago → RESUME from checkpoint
│   │   └── Last checkpoint > 5 min ago → REPLAY from last valid checkpoint
│   └── NO → Continue classification
│
├── Is it a step exception?
│   ├── Exception type: TransientError (network, timeout, rate limit)
│   │   └── Strategy: RETRY (up to 3 times with exponential backoff)
│   ├── Exception type: ValidationError (bad input, schema mismatch)
│   │   └── Strategy: ROLLBACK to pre-step state + ALERT operator
│   ├── Exception type: ResourceExhausted (OOM, quota)
│   │   └── Strategy: PAUSE + REQUEST QUOTA INCREASE + RESUME
│   ├── Exception type: AuthorizationError (insufficient authority)
│   │   └── Strategy: ESCALATE to hitl-dashboard for human approval
│   └── Exception type: PermanentError (logic error, corrupted state)
│       └── Strategy: ROLLBACK + POST-MORTEM + HUMAN REVIEW
│
└── Is it a state corruption?
    ├── Checkpoint hash mismatch → Load parent checkpoint → REPLAY
    └── No valid checkpoint → FULL RESTART + operator notification
```

---

## Recovery Strategies

### RETRY

**When:** Transient error; external service temporarily unavailable.

**Procedure:**
1. Wait: 30s × 2^(attempt-1) (30s, 60s, 120s)
2. Re-execute failed step with identical inputs
3. On third failure: escalate to ROLLBACK

**Max retries:** 3 (configurable per workflow)

---

### RESUME

**When:** Process crash or node failure; last checkpoint is recent and valid.

**Procedure:**
1. Load most recent valid checkpoint (verify hash)
2. Restore workflow context from checkpoint
3. Re-enter workflow at the step after the last completed step
4. Skip any steps marked as completed in checkpoint
5. Continue execution from resumed step

**Prerequisite:** Valid checkpoint exists; state hash verifies.

---

### REPLAY

**When:** State corruption; checkpoint gap too large; audit or compliance requirement.

**Procedure:**
1. Load the last known-good checkpoint (may not be the most recent)
2. Initialize replay context with side-effect suppression enabled
3. Replay each step in order using recorded inputs from event log
4. For each step with a recorded side effect: use idempotency key to skip re-execution
5. Continue until current step reached; then resume live execution

**Note:** Replay is deterministic only if all external calls use idempotency keys.
Non-idempotent external calls are flagged and queued for human review.

---

### ROLLBACK

**When:** Validation error; permanent error; operator-initiated rollback.

**Procedure:**
1. Load checkpoint from before the failed step
2. Reverse any completed side effects that are reversible (API calls with rollback endpoints, DB transactions)
3. Emit `workflow.rolled_back` event with rollback scope
4. Notify stakeholders of rollback
5. Queue post-mortem task

**Reversibility matrix:**

| Side Effect Type | Reversible? | Rollback Method |
|---|---|---|
| DB transaction (within open TX) | Yes | Transaction rollback |
| API call with undo endpoint | Yes | Call rollback endpoint |
| File write | Yes | Delete written file |
| Email/Slack sent | No | Correction message |
| Money transferred | No | Initiate reversal; human review |
| Code deployed | Partial | Redeploy previous version |

---

### ESCALATE

**When:** Authorization error; high-stakes action blocked; no valid recovery path.

**Procedure:**
1. Pause workflow (preserve state in checkpoint)
2. Emit `workflow.escalated` event to hitl-dashboard
3. Present context to human operator: failed step, reason, proposed actions
4. Await operator decision:
   - Approve alternate path → resume with operator override logged
   - Abandon workflow → trigger ROLLBACK
   - Modify scope → replan from current checkpoint

---

## Recovery Metrics

Track these metrics for every recovery event:

| Metric | Description |
|---|---|
| Time to recover (TTR) | From failure detection to resumed execution |
| Checkpoint age at recovery | How old was the checkpoint used for recovery |
| Steps replayed | Number of steps re-executed during recovery |
| Recovery outcome | success / partial-success / escalated / abandoned |
| Data loss window | Time period for which work may have been lost |

Recovery metrics feed the weekly observability report and inform checkpoint interval tuning.

---

## Post-Mortem Template

For any workflow that required ESCALATE, ROLLBACK, or FULL RESTART:

```
WORKFLOW RECOVERY POST-MORTEM
==============================
Workflow ID: WF-YYYYMMDD-NNN
Failure time: YYYY-MM-DD HH:MM UTC
Recovery time: YYYY-MM-DD HH:MM UTC
TTR: N minutes

Root cause: <description>
Failure category: transient | validation | resource | authorization | permanent

Impact:
- Steps rolled back: N
- Data loss window: N minutes
- Downstream workflows affected: N

Recovery actions taken:
1. ...

Prevention:
1. ...

Follow-up tasks:
- [ ] Task description — owner — due date
```