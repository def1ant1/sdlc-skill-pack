# audit-log-review

Audit log review with preserved evidence packets and gated corrective mutations.

## Governance requirements
- Enforce policy checks before any external or mutable action.
- Emit explicit source lineage with timestamps where analytical conclusions depend on upstream data.
- If a required approval is missing, continue in analysis-only mode and emit `approval_requested`.

## Domain-specific controls
- Security mutations require human approval and evidence preservation (pre/post state + audit references).
