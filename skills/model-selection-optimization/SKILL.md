---
name: model-selection-optimization
description: Evaluates and ranks available models against task requirements using multi-criteria scoring across capability, latency, cost, and alignment dimensions to identify the optimal model for each task type.
metadata:
  version: "1.0.0"
  category: model-lifecycle
  owner: platform
  maturity: alpha
  dependencies: [model-routing, model-lifecycle, benchmark-factory, telemetry]

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

Multi-criteria model selection optimizer for the model routing layer. Evaluates the full
set of available models against a task's requirements — capability match, latency budget,
cost ceiling, and alignment requirements — to produce a ranked selection with confidence
scores and fallback recommendations.

## Activation Triggers

- Model-routing receives a task request and requires an optimized model assignment
- Model-lifecycle promotes a new model version requiring routing table update
- Operator requests a model selection audit for a specific task class
- A/B test framework requires model assignment optimization for a traffic split experiment

## Execution Protocol

1. **Parse task requirements**: Extract capability requirements, quality floor, latency budget
   (P95 target), cost ceiling (per-request), and any alignment or compliance constraints.

2. **Filter eligible models**: From the model registry, retain only models that pass all hard
   constraints — capability tier meets requirement, latency P95 within budget, alignment score
   above minimum.

3. **Score eligible models**: For each eligible model, compute a weighted multi-criteria score:
   capability match (40%), cost efficiency (25%), latency headroom (20%), alignment score (15%).

4. **Apply routing preferences**: Adjust scores for routing preferences — local-first bonus,
   preferred vendor weight, current utilization penalty.

5. **Rank and select**: Produce a ranked list; select the highest-scoring model as primary;
   identify the top 2 alternates as fallbacks.

6. **Log selection decision**: Record the selection rationale, all candidate scores, and
   selected model in the routing decision log for cost accounting and analysis.

## Output Format

Model selection record with: `task_id`, `selected_model_id` (with score), `fallback_models`
(ranked list), `selection_criteria_scores` (per dimension), `estimated_cost_per_request`,
`estimated_latency_p95`, and routing decision rationale.

## References

- `references/model-selection-criteria.md` — scoring weights, capability tier mapping, routing preference rules