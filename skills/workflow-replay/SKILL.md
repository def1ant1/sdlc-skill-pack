---
name: workflow-replay
description: Deterministically replays a recorded workflow execution using captured inputs and idempotency keys, enabling audit verification, debugging, and state reconstruction without side effects.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [workflow-runtime, checkpoint-management, event-bus, telemetry]

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

Deterministic replay engine for durable workflow executions. Reconstructs historical workflow
runs using recorded event logs and idempotency keys, enabling audit verification, root-cause
debugging, and safe state reconstruction for recovery purposes.

## Activation Triggers

- Operator-requested replay for audit or debugging via hitl-dashboard
- Recovery path requiring full workflow replay from a parent checkpoint
- Compliance audit requiring verified execution trace reproduction
- Regression testing of modified workflow definitions against historical inputs

## Execution Protocol

1. **Load execution record**: Retrieve the original workflow definition version, event log,
   and all recorded step inputs from durable storage using the workflow-id.

2. **Verify replay eligibility**: Confirm all recorded inputs are available; check that
   idempotency keys cover every step; flag any gaps that would produce non-deterministic replay.

3. **Initialize replay context**: Restore workflow state from the target checkpoint; configure
   replay mode — suppresses external side effects (no emails, no API writes) unless explicitly
   enabled by operator.

4. **Execute step-by-step replay**: For each step in the original execution order, inject
   recorded inputs rather than executing live I/O; apply the same workflow logic; compare
   output to the recorded output and log any divergence.

5. **Detect divergence**: If actual output differs from recorded output by more than the
   configured tolerance, pause replay and emit a `replay.divergence` event with the step
   index, recorded vs. actual outputs, and divergence severity.

6. **Emit replay report**: Publish a complete replay record with step-by-step comparison,
   total divergences, replay duration, and a determinism confidence score.

## Output Format

Replay report with: `workflow_id`, `replay_mode` (audit / debug / recovery), `steps_replayed`,
`divergences_detected`, `determinism_score` (0.0–1.0), `replay_duration_ms`, and per-step
comparison entries.

## References

- `references/replay-protocol.md` — idempotency key format, side-effect suppression rules, divergence tolerance thresholds