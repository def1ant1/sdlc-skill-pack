# reconciliation-automation

Provides finance analytics with required KPI calculations and governance checks.

## Required outputs
- Runway (months)
- 13-week cash forecast
- AR/AP aging buckets
- Gross & contribution margins
- Anomaly flags and KPI summary

## Governance
- Block report if required sources are missing.
- Flag report if any source is older than 72 hours.
- Attach explicit source lineage for every metric.

## Canonical finance entities
- Primary entities: `account`, `invoice`, `payment`, `lineage`, `approval`, `policy-context`, `task`, and `decision`.
- Optional entities by workflow: `vendor`, `customer`, `subscription`, `order`, and `contract`.
- Every financial output must preserve source lineage and emit canonical IDs for entity joins.

## Standardized financial output sections
- **Observed data**: source records, freshness timestamps, lineage, and data quality exceptions.
- **Calculations**: explicit formulas, computed values, tolerances, and reconciliation diffs.
- **Assumptions**: scenario assumptions, accounting policy choices, and uncertainty notes.
- **Recommendations**: prioritized actions, owner, due date, and expected financial impact.

## Approval gates for high-risk actions
- Any **payment**, **accounting-book update** (journal posting, close sign-off, ledger mutation), or **tax-facing** action must pause for human approval before execution.
- Emit `approval_requested` before blocked actions and `approval_decided` before any follow-on action.
- If approval is denied or missing, report must continue in analysis-only mode with no side effects.

## Governance-aware evaluation requirements
- Evals must include calculation-correctness datasets with expected numeric outputs and tolerance assertions.
- Evals must include governance-negative datasets that confirm approval gating and policy blocking behavior.
- Passing criteria requires both numeric correctness and governance compliance gates to pass.
