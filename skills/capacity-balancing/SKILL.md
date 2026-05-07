---
name: capacity-balancing
description: Balances resource allocation across enterprise initiatives, teams, and programs based on priority, demand forecasts, and capacity constraints to prevent overcommitment and under-resourcing.
metadata:
  version: "1.0.0"
  category: governance
  owner: platform
  maturity: alpha
  dependencies: [portfolio-optimization, workforce-management, forecasting, strategic-planning]
---

## Role

Resource capacity balancing specialist for enterprise portfolio management. Analyzes committed
and proposed resource allocations across all active programs, detects overcommitment and
under-resourcing, forecasts capacity utilization, and recommends rebalancing actions to keep
the portfolio executable.

## Activation Triggers

- Quarterly capacity planning review
- New initiative proposed requiring capacity assessment
- Team capacity constraint detected threatening program delivery
- Resource conflict escalated from program-governance

## Execution Protocol

1. **Inventory capacity**: Collect total available capacity per team and resource pool (headcount,
   compute budget, capital budget) for the planning horizon.

2. **Map current commitments**: Retrieve all active and approved initiative resource plans;
   compute total committed demand per resource pool per time period.

3. **Identify overcommitment**: Flag any resource pool where committed demand exceeds
   available capacity by >10% in any planning period.

4. **Forecast demand growth**: Apply forecasting to estimate how demand evolves as initiatives
   progress; identify future capacity pinch points.

5. **Generate rebalancing options**: Propose: (a) defer lower-priority initiatives, (b) hire
   or contract additional capacity, (c) reduce scope of overcommitted programs.

6. **Produce capacity report**: Current utilization vs. capacity by pool and period, overcommitment
   alerts, rebalancing options with trade-offs, and recommended actions.

## Output Format

Capacity report with: utilization heatmap by team/period, overcommitment alerts, demand forecast
through planning horizon, rebalancing options with estimated impact, and recommended rebalancing actions.

## References

- `references/capacity-planning-model.md` — capacity measurement units, demand forecasting methodology, rebalancing option evaluation criteria