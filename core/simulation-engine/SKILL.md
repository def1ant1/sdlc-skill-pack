---
name: simulation-engine
description: Enterprise simulation runtime for modeling business processes, infrastructure behaviors, and organizational dynamics to support scenario planning, war gaming, and digital twin maintenance.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [cognitive-runtime, knowledge-graph, forecasting, synthetic-data]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Predictive simulation core for the enterprise OS. Maintains digital twin models of business
processes, infrastructure, and organizational systems; runs scenario simulations; and produces
probabilistic outcome forecasts for decision support across business, security, and infrastructure domains.

## Activation Triggers

- Scenario planning requested for a strategic decision
- Infrastructure change requires risk assessment before execution
- Organizational change impact modeling requested
- Incident simulation game day exercise initiated
- Pricing or capacity scenario analysis requested

## Execution Protocol

1. **Select or build model**: Retrieve the appropriate digital twin model from the simulation
   library; or synthesize a model from knowledge-graph data if none exists.

2. **Configure scenario**: Apply scenario parameters — demand shock, failure injection,
   org change, pricing delta — to the model's initial conditions.

3. **Initialize simulation state**: Seed model with current actual state from data-fabric
   (current revenue, utilization, headcount, capacity).

4. **Run simulation**: Advance model through time steps; apply stochastic perturbations
   per configured uncertainty distributions; capture key metrics at each step.

5. **Aggregate outcome distribution**: Run N=1000 Monte Carlo iterations; compute P10/P50/P90
   distributions for key outcome metrics.

6. **Produce scenario report**: Expected outcome, confidence interval, key risk factors, break-even
   analysis, and scenario comparison if multiple scenarios requested.

## Output Format

Scenario simulation report with: P10/P50/P90 outcome ranges for key metrics, probability of
SLO or target breach, key uncertainty drivers, and recommended risk mitigations.

## References

- `references/simulation-models.md` — model library for business, infrastructure, security, and org simulation; uncertainty parameterization