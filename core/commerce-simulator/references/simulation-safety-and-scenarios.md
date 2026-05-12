# Simulation Safety and Scenario Requirements

## Dry-run execution constraints
1. Disable all action adapters that can place/edit/cancel real marketplace state.
2. Use simulated order/inventory/pricing ledgers isolated from production systems.
3. Require explicit `mode: dry_run` markers in every simulation request and artifact.
4. Persist outputs only as analysis artifacts and organizational memory summaries.

## Required modeled variables
- Demand shocks: elasticity shifts, event-driven demand spikes/drops.
- Fee changes: platform fee schedule adjustments and payment processing variance.
- Logistics delays: transit variability and warehouse processing bottlenecks.
- Inventory turnover: sell-through velocity, replenishment lag, aged-inventory carry cost.

## Simulation quality checks
- Deterministic replay with seed tracking.
- Scenario assumptions captured with provenance.
- Human-review checkpoints before any policy recommendation is operationalized.
