# inflation-impact-analysis

Inflation impact analysis with timestamped source inputs and scenario ranges.

## Governance requirements
- Enforce policy checks before any external or mutable action.
- Emit explicit source lineage with timestamps where analytical conclusions depend on upstream data.
- If a required approval is missing, continue in analysis-only mode and emit `approval_requested`.

## Domain-specific controls
- Economic outputs must include `source_timestamps` and `scenario_ranges` (base/upside/downside).
