# Model Routing Policy

## Overview

The `model-routing` skill selects the optimal inference backend and model for every request.
This document defines the routing policy rules, model capability tiers, and the cost-quality
tradeoff framework.

---

## Model Capability Tiers

| Tier | Local Models | Cloud Models | Use Cases |
|---|---|---|---|
| Tier 1 — Nano | Qwen2.5-0.5B, Phi-3.5-mini | — | Classification, tagging, simple extraction |
| Tier 2 — Small | Qwen2.5-7B, Mistral-7B | Haiku 4.5 | Summarization, standard reasoning, retrieval reranking |
| Tier 3 — Medium | Qwen2.5-32B, Mistral-32B | Sonnet 4.6 | Code generation, complex analysis, multi-step reasoning |
| Tier 4 — Large | Qwen2.5-72B, DeepSeek-V3 | Opus 4.6 | Architecture design, research, high-stakes decisions |
| Tier 5 — Reasoning | QwQ-32B, DeepSeek-R1 | o3 (cloud) | Mathematical reasoning, formal verification, planning |

---

## Routing Priority Rules

### Rule 1: Local-First

All requests route to the highest-capable local model that meets the quality requirement.
Cloud routing is triggered only when:
- No local model meets the quality threshold
- Local capacity is saturated (GPU SM utilization > 90%)
- Task explicitly requires cloud-only capability (e.g., real-time web access)
- Latency SLO cannot be met locally due to queue depth

### Rule 2: Quality Floor

Each task type has a minimum quality tier:

| Task Type | Minimum Tier | Rationale |
|---|---|---|
| Classification/tagging | Tier 1 | Simple pattern matching |
| Summarization | Tier 2 | Semantic understanding required |
| Code generation | Tier 3 | Complex reasoning required |
| Architecture decisions | Tier 4 | High stakes; quality critical |
| Multi-step planning | Tier 3–4 | Depends on complexity |
| Safety evaluation | Tier 3 | Reliability required |
| Board-level reporting | Tier 4 | Accuracy critical |

### Rule 3: Latency Budget

| Latency Budget | Routing Behavior |
|---|---|
| < 500ms | Tier 1-2 only; cloud disallowed (network overhead) |
| 500ms – 5s | Tier 1-3; local preferred; cloud if saturated |
| 5s – 30s | Any tier; local strongly preferred |
| > 30s (async) | Any tier including cloud reasoning models |

### Rule 4: Cost Cap

If a cost cap is specified per request:

```
cost_cap_usd / expected_output_tokens = max_cost_per_token

Route to highest-quality model where cost_per_token ≤ max_cost_per_token
```

Local models: ~$0.0000001/token (compute cost estimate)
Cloud Haiku 4.5: ~$0.00000025/token
Cloud Sonnet 4.6: ~$0.000003/token
Cloud Opus 4.6: ~$0.000015/token

---

## Complexity Estimation Heuristics

Before routing, `model-routing` estimates task complexity to select the minimum-sufficient tier:

| Signal | Low Complexity | High Complexity |
|---|---|---|
| Input tokens | < 500 | > 5000 |
| Task type keywords | classify, extract, summarize | reason, plan, design, architect |
| Chain-of-thought required | No | Yes |
| Tool use required | None | Multiple sequential tools |
| Prior similar task latency | < 1s | > 10s |
| Output type | Label, score, short text | Long-form, code, structured plan |

**Complexity score:** 0–10 (low = Tier 1, high = Tier 5)

---

## Routing Decision Log

Every routing decision is recorded for policy learning:

```yaml
routing_decision:
  request_id: "REQ-YYYYMMDD-NNN"
  timestamp: "ISO8601"
  task_type: "<type>"
  complexity_score: N
  quality_floor: N
  latency_budget_ms: N
  cost_cap_usd: X
  candidates_evaluated:
    - model: "qwen2.5-32b"
      tier: 3
      quality_score: 0.87
      estimated_latency_ms: 2400
      estimated_cost_usd: 0.000021
      local: true
      selected: true
      reason: "best quality within latency budget"
    - model: "claude-sonnet-4-6"
      tier: 3
      quality_score: 0.91
      estimated_latency_ms: 3100
      estimated_cost_usd: 0.00018
      local: false
      selected: false
      reason: "exceeded cost cap"
  final_model: "qwen2.5-32b"
  final_backend: "local_vllm"
  actual_latency_ms: 2180
  actual_cost_usd: 0.000019
  quality_score_actual: 0.89
```

These logs feed routing policy learning — models that consistently underperform their estimated
quality score receive a routing penalty in future decisions.

---

## Overflow Policy

When local capacity is saturated:

1. Queue request for up to 30 seconds (configurable)
2. If queue wait would exceed latency budget: route to cloud immediately
3. If cloud cost would exceed budget: reject with `routing.no_viable_model` error
4. Emergency override: P0 incident response always routes to highest-available model