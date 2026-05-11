# Financial Controls Policy

## Purpose
Define baseline controls for financial recommendations and money-moving workflows.

## Policy
- Enforce spend/payment thresholds with approval authority routing.
- Require separation of duties for request, approval, and execution on high-impact transactions.
- Prohibit autonomous release of funds, tax positions, or accounting finalization without designated human approvers.
- Preserve immutable logs for financial decisions, overrides, and exceptions.

## Required Controls
- Threshold matrix and approver policy.
- Exception handling with mandatory rationale.
- Periodic control testing and reconciliation.

## Runtime cost governance

- Scheduler must evaluate projected per-run estimated cost before execution.
- Policy actions: `allow`, `warn`, `block` based on plan-tier budget thresholds.
- Cost events SHOULD be emitted using `schemas/cost-event.schema.json` for auditability.
