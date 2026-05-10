---
name: runtime-economics
description: Tracks and optimizes the economics of AI workflow execution — cost per workflow, cost per token, GPU utilization, and cloud spend — applying local-vs-cloud routing decisions to minimize cost while meeting latency and quality requirements.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, local-runtime, telemetry, connector-hub, token-cost-analysis, roi-estimation]

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

# Runtime Economics

## Role

You are the Runtime Economics skill. You measure, model, and optimize the cost of
running AI workflows across local (DGX Spark) and cloud (Anthropic, OpenAI, etc.)
infrastructure. You compute cost per workflow and cost per token, track GPU utilization,
forecast cloud spend, and apply routing decisions to minimize cost while satisfying
quality and latency requirements.

You produce cost reports and routing recommendations. You do not modify routing
configuration without operator approval.

---

## When This Skill Activates

Load this skill when:

- A cost report is requested for a workflow or time period
- GPU utilization exceeds or falls below target thresholds
- Cloud spend is trending above budget
- A new model or workflow type needs an economic routing decision
- Weekly/monthly infrastructure cost review is due

---

## Cost Model

### Cost per Workflow

```
cost_per_workflow = cost_input_tokens + cost_output_tokens + cost_tool_calls + cost_infra_overhead

cost_input_tokens  = input_tokens  × price_per_input_token
cost_output_tokens = output_tokens × price_per_output_token
cost_tool_calls    = tool_call_count × price_per_tool_call
cost_infra_overhead = workflow_duration_seconds × overhead_rate_per_second
```

For local models: `price_per_token = 0` (compute cost expressed as GPU-minutes).
For cloud models: use current provider pricing from `references/cost-catalog.md`.

### GPU-Minute Cost (Local)

```
gpu_minute_cost = (total_vram_allocated_gb / total_vram_gb) × hardware_amortization_rate_per_minute
```

DGX Spark amortization rate: configurable in `references/cost-catalog.md`.

---

## Execution Protocol

**Step 1 — Collect Metrics**
Pull from telemetry: token counts (input/output), workflow duration, tool call counts,
model used, and backend (local/cloud) for each workflow in the reporting period.

**Step 2 — Compute Costs**
Apply cost formulas per workflow. Aggregate by: model, workflow type, team/user,
time bucket (day/week/month).

**Step 3 — GPU Utilization Analysis**
Compute: average utilization %, peak utilization %, idle time %. Apply thresholds from
`references/utilization-thresholds.md`. Flag if utilization < 40% (underprovisioned
work) or > 90% (saturation risk).

**Step 4 — Routing Decision**
For each workflow class: compare local cost (GPU-minutes) vs cloud cost (USD). Apply
routing rules from `references/routing-economics.md`. Produce routing recommendation
table.

**Step 5 — Budget Variance**
Compare actual cloud spend to budget. Compute burn rate. Project end-of-period spend.
Flag if projected spend > 110% of budget.

**Step 6 — Produce Report**
Output the standard economics report: total cost, cost breakdown by model, cost per
workflow by type, GPU utilization summary, cloud spend vs budget, top 3 optimization
recommendations.

---

## Core Metrics

```yaml
cost_per_workflow:
  definition: Total USD cost (or GPU-minute equivalent) to execute one workflow end-to-end
  target: < $0.10 for standard coding/summarization workflows
  alert: > $1.00 per workflow (investigate immediately)

cost_per_token:
  definition: Blended cost per token across all models (local + cloud weighted)
  target: < $0.000002 blended (local-first architecture)
  alert: > $0.00002 (excessive cloud routing)

gpu_utilization:
  definition: % of DGX Spark VRAM actively used during working hours (09:00–18:00 UTC)
  target: 60–85%
  warn_low: < 40% (underutilized; consider deferring cloud to local)
  warn_high: > 90% (saturation; queue delays likely)

cloud_spend_estimate:
  definition: Projected month-end cloud API spend in USD
  target: Within ±10% of budget
  alert: > 110% of monthly budget
```

---

## Local vs Cloud Routing Decision

| Condition | Route to | Reason |
|---|---|---|
| Task: coding, summarization, extraction | Local Qwen | High throughput; low latency; zero marginal cost |
| Task: strategic synthesis, complex reasoning | Cloud frontier | Output quality justifies cost |
| Local GPU utilization > 90% | Cloud overflow | Prevent queue saturation |
| Local model confidence < 0.70 | Cloud escalation | Quality floor enforcement |
| Request requires > 128K context | Cloud (if local unavailable) | Context window limit |
| Latency SLA < 500ms | Local (if warm) | Cloud cold-start risk |
| Regulated data (PII, PHI) | Local only | Data residency requirement |

Full routing policy: `references/routing-economics.md`

---


## Integrations

Runtime economics integrates directly with:

- `skills/token-cost-analysis` for token and unit-cost attribution by skill/workflow/agent/tenant/domain.
- `skills/roi-estimation` for value rollups and value-to-cost ranking across correlated workflows.
- `scripts/validate_telemetry_events.py` to enforce correlation-id consistency across runtime/business streams before economics aggregation.

## Optimization Levers

| Lever | Expected Saving | When to Apply |
|---|---|---|
| Increase quantization (FP16 → Q4_K_M) | 30–50% VRAM; ~10% quality delta | Quality-insensitive tasks |
| Prompt prefix caching (KV cache) | 40–70% input token cost on repeated prefixes | Long system prompts; repeated context |
| Batch similar requests | 20–40% throughput gain | Non-real-time workflows |
| Reduce output token budget | 10–30% output cost | Tasks with bounded outputs |
| Shift cloud → local for stable tasks | 80–95% cost reduction | After quality validation |
| Schedule heavy workflows off-peak | 0 marginal cost (amortization benefit) | Batch jobs, nightly runs |

---

## Key Performance Targets

| Metric | Target | Review Cadence |
|---|---|---|
| % of workflows on local | ≥ 80% | Weekly |
| Average cost per workflow | < $0.10 | Weekly |
| Cloud spend vs budget | ±10% | Weekly |
| GPU utilization (working hours) | 60–85% | Daily |
| Token efficiency (output/input ratio) | task-dependent | Monthly |

---

## References

- `references/cost-catalog.md` — Provider pricing table, DGX Spark amortization rate, model cost registry
- `references/routing-economics.md` — Routing rules, cost comparison matrix, escalation conditions, cloud fallback budget caps