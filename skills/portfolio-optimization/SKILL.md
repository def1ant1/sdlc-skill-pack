---
name: portfolio-optimization
description: Scores and ranks strategic initiatives across multiple criteria (ROI, strategic alignment, risk, capacity fit), optimizes resource allocation across the portfolio, and produces investment recommendations for executive decision-making.
metadata:
  version: "1.0.0"
  category: governance
  owner: strategy
  maturity: alpha
  dependencies: [initiative-prioritization, capacity-balancing, telemetry]
---

## Role

Multi-criteria portfolio scoring and optimization engine for the PMO. Evaluates the full
initiative portfolio against strategic objectives and resource constraints, produces
Pareto-optimal investment allocations, and generates executive-grade portfolio recommendations
with explicit trade-off analysis.

## Activation Triggers

- Annual or quarterly planning cycle requires portfolio prioritization
- Capacity-balancing detects overcommitment requiring portfolio rebalancing
- New initiative submission requires impact analysis against the existing portfolio
- Executive sponsor requests portfolio health assessment and reallocation recommendation

## Execution Protocol

1. **Load portfolio**: Retrieve all active and proposed initiatives with their investment
   requirements, expected benefits, strategic alignment scores, risk ratings, and dependencies.

2. **Score each initiative**: Apply weighted multi-criteria scoring — strategic alignment (30%),
   expected ROI (25%), risk-adjusted NPV (20%), capacity fit (15%), time-to-value (10%).

3. **Model constraints**: Define the resource envelope (budget, headcount, compute) and any
   mandatory initiatives (regulatory, P0 commitments); apply as hard constraints.

4. **Optimize allocation**: Run integer programming or greedy knapsack optimization to find
   the portfolio allocation that maximizes aggregate weighted score within constraints;
   enumerate the Pareto frontier for executive trade-off visibility.

5. **Analyze trade-offs**: For the recommended allocation, document: initiatives included vs.
   deferred, resource utilization by type, expected portfolio ROI, and risk concentration.

6. **Produce investment recommendation**: Render executive portfolio report with recommended
   allocation, rationale, key trade-offs, and sensitivity analysis (what changes if budget
   increases/decreases by 20%).

## Output Format

Portfolio optimization report with: `portfolio_id`, `initiatives_evaluated` (count),
`recommended_allocation` (initiative list with investment and expected return), `total_portfolio_roi`,
`resource_utilization` (by type), `deferred_initiatives` (with deferral rationale), and
`sensitivity_analysis`.

## References

- `references/portfolio-scoring-model.md` — scoring weights, constraint types, optimization algorithm, sensitivity analysis protocol