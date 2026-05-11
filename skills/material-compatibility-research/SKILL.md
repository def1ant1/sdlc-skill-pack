# material-compatibility-research

Material compatibility research with safety-critical warnings and professional review requirements.

## Governance requirements
- Enforce policy checks before any external or mutable action.
- Emit explicit source lineage with timestamps where analytical conclusions depend on upstream data.
- If a required approval is missing, continue in analysis-only mode and emit `approval_requested`.

## Domain-specific controls
- Flag safety-critical materials outputs for professional engineering/safety review before use.
