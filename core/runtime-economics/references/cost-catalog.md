# Cost Catalog

Used by `core/runtime-economics/SKILL.md` to provide current model pricing,
DGX Spark amortization rates, and the model cost registry.

---

## Cloud Model Pricing

All prices in USD per million tokens. Update when providers publish new rates.
Last updated: 2026-05-06.

### Anthropic Claude

| Model | Input ($/M tokens) | Output ($/M tokens) | Context |
|---|---|---|---|
| claude-opus-4-6 | 15.00 | 75.00 | 200K |
| claude-sonnet-4-6 | 3.00 | 15.00 | 200K |
| claude-haiku-4-5 | 0.80 | 4.00 | 200K |

### OpenAI

| Model | Input ($/M tokens) | Output ($/M tokens) | Context |
|---|---|---|---|
| gpt-4o | 2.50 | 10.00 | 128K |
| gpt-4o-mini | 0.15 | 0.60 | 128K |
| o3 | 10.00 | 40.00 | 200K |

### Google Gemini

| Model | Input ($/M tokens) | Output ($/M tokens) | Context |
|---|---|---|---|
| gemini-2.5-pro | 1.25 | 10.00 | 1M |
| gemini-2.5-flash | 0.075 | 0.30 | 1M |

### Tool Call Pricing

| Provider | Tool call overhead |
|---|---|
| Anthropic | Input tokens only (tool definitions counted as input) |
| OpenAI | Input tokens only |
| Google | Input tokens only |

---

## Local Model Cost Model

Local inference has zero marginal token cost. Cost is expressed as GPU-minutes
consumed, amortized against hardware acquisition and power.

### DGX Spark Amortization Rate

```yaml
hardware:
  model: NVIDIA DGX Spark
  vram_gb: 128
  acquisition_cost_usd: 3000        # update when purchased
  expected_lifetime_years: 3
  annual_power_cost_usd: 438        # 50W avg × 8760h × $0.10/kWh
  annual_maintenance_usd: 200

amortization:
  annual_cost_usd: 1438             # (3000/3) + 438 + 200
  working_hours_per_year: 2080      # 8h/day × 260 working days
  cost_per_working_hour_usd: 0.691
  cost_per_minute_usd: 0.01152
  cost_per_vram_gb_minute_usd: 0.0000900  # per GB of VRAM allocated
```

### GPU-Minute Cost Formula

```
workflow_gpu_cost = avg_vram_allocated_gb × duration_minutes × 0.0000900
```

---

## Model Cost Registry

Registered models with expected cost per standard workflow task (1K input + 512 output tokens):

| Model | Location | Cost/workflow | Quality Tier | Best For |
|---|---|---|---|---|
| qwen2.5-coder-32b (Q4_K_M) | Local | ~$0.0004 GPU-min | High | Code generation, review |
| qwen2.5-72b (Q4_K_M) | Local | ~$0.0008 GPU-min | High | Reasoning, summarization |
| qwen2.5-7b (Q4_K_M) | Local | ~$0.0001 GPU-min | Medium | Extraction, classification |
| claude-haiku-4-5 | Cloud | ~$0.0024 | Medium-High | Fast cloud overflow |
| claude-sonnet-4-6 | Cloud | ~$0.0105 | Very High | Strategic synthesis |
| claude-opus-4-6 | Cloud | ~$0.0525 | Best | High-stakes decisions |
| gpt-4o-mini | Cloud | ~$0.000375 | Medium | High-volume cloud tasks |

---

## Cloud Budget Caps

Hard limits on cloud spend. Exceeding these triggers local-first override until reset.

```yaml
cloud_budget:
  daily_limit_usd: 50.00
  weekly_limit_usd: 250.00
  monthly_limit_usd: 800.00
  alert_at_pct: 80          # alert when 80% of period budget consumed
  hard_cap_action: route_to_local_only
```

---

## Prompt Caching Savings

When provider-side prompt caching is available (Anthropic cached_creation/cached_read):

| Cache tier | Discount |
|---|---|
| Cache write | +25% input cost (one-time) |
| Cache read | −90% input cost for cached tokens |

Net benefit: profitable after 2 cache hits on the same prefix.
Apply caching for: system prompts > 1024 tokens, shared knowledge base prefixes.

---

## Price Update Policy

- Review pricing monthly against provider documentation
- On any price change > 20%: re-evaluate routing thresholds in `routing-economics.md`
- Record update date and source in this file's Last Updated header