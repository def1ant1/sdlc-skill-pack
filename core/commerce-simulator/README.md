# Commerce Simulator

`core/commerce-simulator` provides a dry-run simulation environment for ecommerce planning.

## Safety mode (mandatory)
- Simulator runs are **dry-run only**.
- No calls may mutate live marketplace listings, pricing, orders, payouts, or inventory.
- External side-effecting connectors must be disabled in simulator mode.

## Scenario coverage
The simulator models:
- demand shocks (positive/negative demand regime shifts),
- fee changes (marketplace commissions, payment fees, storage/fulfillment charges),
- logistics delays (carrier latency, cross-border hold times, inbound receiving delays),
- inventory turnover dynamics (days-on-hand, stockout risk, stale inventory risk).

## Outputs
- Scenario-level KPI deltas (margin, GMV, stockout probability, fulfillment SLA hit rates).
- Sensitivity curves and policy recommendations.
- Audit trail of assumptions and constraints.

See `references/simulation-safety-and-scenarios.md` for dry-run controls and modeling requirements.
