# Model Selection Criteria Reference

## Scoring Weights

| Criterion | Weight | Rationale |
|---|---|---|
| Capability match | 40% | Quality of output is the primary concern |
| Cost efficiency | 25% | Economic viability of routing decision |
| Latency headroom | 20% | Latency SLO must be met |
| Alignment score | 15% | Safety is non-negotiable but most models pass |

---

## Capability Tier → Task Type Mapping

| Task Type | Minimum Tier | Recommended Tier | Rationale |
|---|---|---|---|
| Simple Q&A, retrieval | Nano | Micro | Low reasoning demand |
| Summarization, extraction | Micro | Standard | Moderate synthesis needed |
| Code generation (simple) | Micro | Standard | Pattern-following with moderate complexity |
| Analysis, report writing | Standard | Advanced | Requires coherent multi-step reasoning |
| Code generation (complex) | Standard | Advanced | Architecture and debugging require depth |
| Strategic planning | Advanced | Reasoning | Long-horizon, multi-constraint reasoning |
| Mathematical reasoning | Advanced | Reasoning | Formal proof and computation chains |
| Novel research synthesis | Reasoning | Reasoning | Highest reasoning demand |

---

## Capability Score Computation (0–100)

```
capability_score = min(100,
    benchmark_match_score × 0.60 +   # Benchmark performance on this task type
    context_window_fit × 0.25 +       # Window sufficient for input length
    specialization_bonus × 0.15       # Fine-tuning on relevant domain
)

benchmark_match_score = (model_benchmark_score_for_task / max_benchmark_score) × 100
context_window_fit = 100 if context_tokens ≤ model_max_tokens × 0.8 else 0
specialization_bonus = 15 if model has verified fine-tuning on task domain else 0
```

---

## Cost Efficiency Score (0–100)

```
cost_efficiency_score = 100 × (1 - (model_cost_per_1k_tokens / cost_ceiling_per_1k_tokens))
```

- Score = 0 if cost exceeds ceiling (hard constraint eliminates the model)
- Score = 100 if cost is 0 (free local model within resource budget)

**Cost ceiling defaults by task class:**

| Task Class | Cost Ceiling (per 1K output tokens) |
|---|---|
| P0 — incident response | No ceiling |
| P1 — customer-facing | $0.05 |
| P2 — engineering SDLC | $0.02 |
| P3 — analytics | $0.01 |
| Background | $0.005 |

---

## Latency Headroom Score (0–100)

```
latency_headroom_score = 100 × (1 - (model_p95_latency_ms / latency_budget_ms))
```

- Score = 0 if P95 latency exceeds budget (hard constraint eliminates the model)
- Score = 100 if P95 latency ≤ 10% of budget

**Latency budget defaults by task class:**

| Task Class | P95 Latency Budget |
|---|---|
| P0 — incident response | 30,000 ms |
| P1 — customer-facing (interactive) | 3,000 ms |
| P1 — customer-facing (batch) | 30,000 ms |
| P2 — engineering SDLC | 60,000 ms |
| P3 — analytics | 300,000 ms |

---

## Alignment Score (0–100)

```
alignment_score = model_alignment_registry_score
```

- Score < 70: Model is ineligible for routing (hard constraint)
- Score 70–84: Model may be used with monitoring flag
- Score ≥ 85: Model is preferred for alignment-sensitive tasks

---

## Routing Preference Rules

Applied as score adjustments after composite score calculation:

| Rule | Adjustment | Condition |
|---|---|---|
| Local-first preference | +10 points | Model runs on on-premise hardware |
| Preferred vendor bonus | +5 points | Model is from the designated preferred vendor |
| Utilization penalty | -5 to -20 points | Model GPU utilization > 80% (scale with utilization) |
| Canary model bonus | +3 points | Model is in canary promotion stage (gather production data) |
| Deprecated model penalty | -15 points | Model is in DEPRECATED lifecycle stage |

---

## Routing Decision Log YAML

```yaml
routing_decision:
  decision_id: "RD-20260507-001234"
  request_id: "REQ-WF042-STEP8"
  timestamp: "2026-05-07T14:23:00.456Z"

  task_requirements:
    task_type: "code_generation_complex"
    minimum_tier: Standard
    context_tokens: 8192
    latency_budget_ms: 60000
    cost_ceiling_per_1k: 0.02
    alignment_minimum: 85

  candidates_evaluated: 5
  candidates_eliminated:
    - model_id: "nano-local-001"
      reason: "Below minimum capability tier"
    - model_id: "cloud-reasoning-001"
      reason: "Cost exceeds ceiling ($0.08 > $0.02)"

  scored_candidates:
    - model_id: "standard-local-002"
      capability_score: 82
      cost_efficiency_score: 95
      latency_headroom_score: 78
      alignment_score: 88
      composite_score: 85.5
    - model_id: "advanced-local-001"
      capability_score: 91
      cost_efficiency_score: 75
      latency_headroom_score: 85
      alignment_score: 90
      composite_score: 85.6

  selected_model: "advanced-local-001"
  fallback_models: ["standard-local-002", "standard-cloud-003"]
  routing_adjustments_applied: ["local-first: +10"]
  final_composite_score: 95.6

  estimated_cost_per_request: 0.014
  estimated_latency_p95_ms: 18500
```