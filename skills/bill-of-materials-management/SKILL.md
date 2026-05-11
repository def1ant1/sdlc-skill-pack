# bill-of-materials-management

BOM analysis with safety-critical/professional-review escalation flags.

## Governance requirements
- Enforce policy checks before any external or mutable action.
- Emit explicit source lineage with timestamps where analytical conclusions depend on upstream data.
- If a required approval is missing, continue in analysis-only mode and emit `approval_requested`.

## Domain-specific controls
- Flag safety-critical materials outputs for professional engineering/safety review before use.
