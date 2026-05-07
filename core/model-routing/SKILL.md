---
name: model-routing
description: Routes inference requests to the optimal model tier using task complexity estimation, cost-quality optimization, and adaptive local/cloud routing with automatic fallback and overflow handling.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [cluster-management, economic-coordination, telemetry]
---

## Role

Adaptive inference router for the AI platform. Evaluates each incoming task request,
estimates its complexity, selects the optimal model from the registered tier hierarchy
(Nano through Reasoning), applies routing priority rules, and manages overflow to cloud
providers when local capacity is exhausted.

## Activation Triggers

- Any skill or agent initiates an inference request requiring model assignment
- Model-selection-optimization requests a routing decision for a task class
- Uncertainty-aware-routing triggers an escalation to a higher capability tier
- Capacity change event requires routing table rebalancing

## Execution Protocol

1. **Estimate task complexity**: Score the incoming task on the complexity heuristic
   (0–10) based on: domain specificity, reasoning depth required, context length,
   multi-step inference needs, and output format constraints.

2. **Determine minimum capability tier**: Map complexity score to minimum capability tier
   — Nano (0–2), Micro (3–4), Standard (5–6), Advanced (7–8), Reasoning (9–10).

3. **Apply routing priority rules**: Select from eligible models using the 4 priority rules —
   local-first (prefer on-premise if latency budget allows), quality floor (never route
   below minimum acceptable quality), latency budget (reject models exceeding P95 target),
   cost cap (reject models exceeding per-request cost ceiling).

4. **Check capacity**: Verify the selected model has available inference capacity; if not,
   check next-tier fallback; if all local tiers are saturated, route to cloud overflow.

5. **Dispatch and monitor**: Route the request; track actual latency and quality; compare
   to estimated values for routing model calibration.

6. **Log routing decision**: Record task complexity estimate, model selected, routing rules
   applied, actual cost, and latency in the routing decision log.

## Output Format

Routing decision record with: `request_id`, `complexity_score`, `minimum_tier`, `selected_model_id`,
`routing_rules_applied`, `estimated_cost`, `actual_cost`, `latency_p95_ms`, and
`overflow_used` (boolean).

## References

- `references/routing-policy.md` — 5 capability tiers, 4 routing rules, complexity estimation, overflow policy