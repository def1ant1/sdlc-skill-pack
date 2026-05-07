---
name: workflow-runtime
description: Executes durable workflows with automatic checkpointing, state recovery, and deterministic replay, guaranteeing at-least-once step execution and consistent state across failures and restarts.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [checkpoint-management, event-bus, telemetry, hitl-dashboard]
---

## Role

Durable workflow execution engine for the Autonomous OS. Executes workflows defined in the
workflow DSL with guaranteed durability — checkpointing state after every step, recovering
from failures via the runtime-recovery skill, and supporting deterministic replay for audit
and debugging purposes.

## Activation Triggers

- Workflow definition submitted for execution by sdlc-orchestration or cognitive-runtime
- Checkpoint recovery path restores a suspended workflow for resumption
- Operator submits a manual workflow execution request
- Event-bus delivers a trigger event matching a workflow's activation condition

## Execution Protocol

1. **Initialize execution context**: Create a workflow execution record with a unique
   WF-YYYYMMDD-NNN ID; load the workflow definition; initialize step state machine.

2. **Execute steps with checkpointing**: For each step, execute the defined action; upon
   successful completion, invoke checkpoint-management to persist state before advancing.

3. **Emit heartbeats**: Publish heartbeat events every 10 seconds to event-bus; absence
   of heartbeat for > 30 seconds triggers runtime-recovery.

4. **Handle step failures**: On step exception, classify the failure type; apply the
   configured retry policy (default: 3 retries with exponential backoff) before escalating
   to runtime-recovery.

5. **Enforce idempotency**: Use idempotency keys on all external actions; on replay or
   retry, skip steps that have already produced a confirmed result.

6. **Complete or escalate**: On final step completion, emit `workflow.completed` event
   with execution summary; on unrecoverable failure, emit `workflow.failed` and notify
   hitl-dashboard.

## Output Format

Workflow execution record with: `workflow_id`, `definition_version`, `steps_completed`,
`checkpoints_created`, `execution_duration_ms`, `final_status` (COMPLETED/FAILED/SUSPENDED),
and `output_artifacts` (list of step outputs).

## References

- `references/checkpoint-schema.md` — checkpoint payload format, storage backends, retention policy, idempotency protocol
- `references/recovery-runbook.md` — failure classification tree, 5 recovery strategies, post-mortem template