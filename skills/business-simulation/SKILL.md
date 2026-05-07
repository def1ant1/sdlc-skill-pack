---
name: business-simulation
description: Runs Monte Carlo scenario analysis on business decisions and strategic initiatives, quantifying outcome distributions, risk profiles, and break-even conditions to support evidence-based executive decisions.
metadata:
  version: "1.0.0"
  category: simulation
  owner: strategy
  maturity: alpha
  dependencies: [simulation-engine, predictive-reasoning, telemetry]
---

## Role

Monte Carlo business simulation engine for strategic decision support. Models uncertain
business outcomes by sampling from probability distributions over key assumptions, producing
outcome distributions, confidence intervals, and risk-adjusted metrics that give executives
a quantitative basis for major decisions.

## Activation Triggers

- Decision-intelligence skill routes a high-stakes business decision requiring quantitative risk analysis
- Strategic-planning skill requires probabilistic outcome modeling for a long-horizon initiative
- Budget-planning skill requires scenario analysis for annual planning assumptions
- Operator requests simulation of a specific business scenario

## Execution Protocol

1. **Define decision model**: Identify decision alternatives, key uncertain variables, their
   probability distributions (normal, log-normal, triangular, uniform), and outcome metrics
   of interest (revenue, margin, time-to-break-even, NPV).

2. **Parameterize distributions**: Elicit or estimate distribution parameters from historical
   data, analogous cases, or expert calibration; document all assumptions and data sources.

3. **Run Monte Carlo simulation**: Execute N trials (default: 10,000); for each trial, sample
   all uncertain variables and compute outcome metrics using the decision model.

4. **Compute outcome distributions**: Aggregate trial results into outcome distributions;
   compute P10, P50, P90 percentiles, expected value, and standard deviation for each metric.

5. **Identify dominant scenarios**: Cluster trials by outcome range; characterize the top 3
   scenarios (optimistic, base, pessimistic) with their defining conditions.

6. **Produce decision report**: Summarize outcome distributions, risk-adjusted metrics,
   break-even conditions, and scenario narratives with actionable decision guidance.

## Output Format

Business simulation report with: `decision_id`, `scenarios_modeled` (3 named scenarios),
`outcome_distribution` (P10/P50/P90 per metric), `expected_value`, `risk_score` (downside
probability), `break_even_conditions`, and `recommended_decision` with confidence level.

## References

- `references/simulation-methodology.md` — Monte Carlo protocol, distribution parameterization guide, scenario characterization rules