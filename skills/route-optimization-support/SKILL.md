# route-optimization-support

Route optimization support that remains analysis-only until required approvals are granted.

## Governance requirements
- Enforce policy checks before any external or mutable action.
- Emit explicit source lineage with timestamps where analytical conclusions depend on upstream data.
- If a required approval is missing, continue in analysis-only mode and emit `approval_requested`.

## Domain-specific controls
- Logistics bookings, payments, and shipment documents require human approval before execution.
