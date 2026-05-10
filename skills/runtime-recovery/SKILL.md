---
name: runtime-recovery
description: Detects workflow failures, classifies the failure type, selects the appropriate recovery strategy, restores from the nearest valid checkpoint, and resumes execution with state integrity guaranteed.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [checkpoint-management, workflow-runtime, telemetry, hitl-dashboard]

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

Automated recovery orchestrator for the durable workflow runtime. Responds to workflow
failures by classifying the root cause, selecting the optimal recovery strategy (resume,
replay, rollback, or escalate), and executing recovery within operator-defined boundaries.

## Activation Triggers

- Workflow heartbeat timeout detected (no heartbeat for >30 seconds)
- Step exception raised within a workflow execution
- Node failure reported by distributed-agent-runtime
- Operator-initiated recovery request via hitl-dashboard
- State corruption detected during checkpoint integrity verification

## Execution Protocol

1. **Classify failure**: Determine failure type from the error context — transient (network
   timeout, rate limit), permanent (logic error, schema mismatch), resource (OOM, quota),
   authorization, or state corruption.

2. **Select recovery strategy**: Apply decision tree — transient → RETRY (up to 3 attempts);
   resource → PAUSE + QUOTA REQUEST; permanent → ROLLBACK + POST-MORTEM; corruption →
   REPLAY from parent checkpoint; authorization → ESCALATE to hitl-dashboard.

3. **Load checkpoint**: Retrieve the most recent valid checkpoint; verify payload_hash
   integrity; if corrupt, try N-1 checkpoint; if all corrupt, flag for full restart.

4. **Restore context**: Invoke state-restoration to deserialize the checkpoint payload and
   reconstruct the full workflow execution context.

5. **Resume or replay execution**: Re-enter the workflow at the step following the last
   completed step; for replay mode, use recorded inputs and idempotency keys.

6. **Escalate if unrecoverable**: If no valid recovery path exists, emit `workflow.failed`
   event, pause the workflow, and notify hitl-dashboard for human intervention.

## Output Format

Recovery action record with: failure classification, strategy applied, checkpoint used,
steps replayed, recovery duration, and final workflow status (resumed / rolled-back / escalated).

## References

- `references/recovery-strategies.md` — failure classification tree, recovery strategy decision rules, retry and escalation thresholds