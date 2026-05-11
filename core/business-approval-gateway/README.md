# Business Approval Gateway

Approval gateway that enforces a deterministic decision flow before side effects are executed.

## Decision flow

1. `request_more_info` → transition to `pending_information` and block side effects.
2. `reject` → transition to `rejected` and block side effects.
3. `approve` → transition to `approved` and allow side effects.

The decision payload is validated by `approval-decision.model.json`.


## Runtime integration

The gateway emits `approval_granted` + `approval_id` values consumed by `scripts/governance/enforce_runtime_policy.py` before any external side effects execute. Denied or pending approvals must fail closed.
