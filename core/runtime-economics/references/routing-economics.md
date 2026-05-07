# Routing Economics

Used by `core/runtime-economics/SKILL.md` to apply cost-aware routing decisions
between local (DGX Spark) and cloud model execution.

---

## Routing Decision Algorithm

Apply rules in priority order. Use the first matching rule.

```
1. SAFETY OVERRIDE: If data contains PII/PHI/regulated content → LOCAL ONLY (no exceptions)
2. BUDGET CAP: If cloud daily/weekly limit reached → LOCAL ONLY until reset
3. GPU SATURATION: If local utilization > 90% → CLOUD OVERFLOW
4. LATENCY SLA: If SLA < 500ms AND local model is warm → LOCAL
5. QUALITY FLOOR: If expected local model confidence < 0.70 → CLOUD
6. CONTEXT LIMIT: If context > local model max → CLOUD
7. TASK ROUTING: Apply task-type table below
```

---

## Task-Type Routing Table

| Task Type | Default Route | Conditions for Override |
|---|---|---|
| Code generation | Local (qwen2.5-coder-32b) | Override to cloud if codebase context > 64K tokens |
| Code review | Local (qwen2.5-coder-32b) | — |
| Summarization | Local (qwen2.5-72b) | — |
| Text extraction | Local (qwen2.5-7b) | — |
| Classification | Local (qwen2.5-7b) | — |
| RAG synthesis | Local (qwen2.5-72b) | Override to cloud if synthesis requires strategic judgment |
| Strategic planning | Cloud (claude-sonnet-4-6) | — |
| Executive reporting | Cloud (claude-sonnet-4-6) | — |
| Architecture design | Cloud (claude-opus-4-6) | High-stakes: use best model |
| Security threat modeling | Cloud (claude-opus-4-6) | Security: never compromise quality |
| Long-context reasoning (> 64K) | Cloud (claude-sonnet-4-6) | — |
| High-volume batch (> 100 req/h) | Local → cloud overflow | Queue local; spill to gpt-4o-mini if saturated |

---

## Cost Comparison Matrix

Break-even analysis: when is cloud cheaper than local (in GPU-minute terms)?

For a standard workflow (1K input + 512 output tokens):

| Local Model | GPU cost | Cloud equiv | Break-even condition |
|---|---|---|---|
| qwen2.5-7b Q4 | ~$0.0001 | gpt-4o-mini ~$0.000375 | Local always wins on cost |
| qwen2.5-32b Q4 | ~$0.0004 | haiku-4-5 ~$0.0024 | Local wins 6:1 on cost |
| qwen2.5-72b Q4 | ~$0.0008 | sonnet-4-6 ~$0.0105 | Local wins 13:1 on cost |
| — | — | opus-4-6 ~$0.0525 | Cloud only when quality essential |

**Conclusion**: Local is almost always cheaper. Route to cloud only for quality-critical
tasks or when local is saturated.

---

## Cloud Overflow Policy

When GPU utilization > 90%:

1. Queue new requests for local with max wait: 30 seconds
2. If queue wait > 30s: route to cloud overflow model
3. Cloud overflow model selection (in order):
   - `gpt-4o-mini` for standard tasks (cheapest)
   - `claude-haiku-4-5` for tasks requiring Anthropic tool use
   - `claude-sonnet-4-6` if overflow task is quality-sensitive
4. Log all overflow events with reason code `LOCAL_SATURATED`
5. Alert if overflow rate > 10% of hourly request volume

---

## Escalation Conditions

Escalate from local to cloud mid-workflow when:

| Condition | Action |
|---|---|
| Local model returns `[UNCERTAIN]` tag | Escalate output for cloud verification |
| Output fails quality gate (score < 0.70) | Re-route entire step to cloud |
| Tool call fails on local model | Retry on cloud model once |
| Local model cold-start delay > 5s | Abort and re-route to cloud |

---

## Cloud Fallback Budget Caps

Enforce hard caps to prevent runaway cloud spend:

```yaml
cloud_fallback_policy:
  daily_cap_usd: 50.00
  weekly_cap_usd: 250.00
  monthly_cap_usd: 800.00
  on_cap_breach:
    - action: block_new_cloud_requests
    - action: alert_operator
    - action: serve_local_only_until_reset
  reset_schedule: daily at 00:00 UTC (daily cap), Monday 00:00 UTC (weekly cap)
```

---

## Utilization Thresholds

| Metric | Threshold | Action |
|---|---|---|
| GPU utilization < 40% | Warning: Underutilized | Review if scheduled cloud tasks can shift local |
| GPU utilization 40–60% | Normal: Low load | No action |
| GPU utilization 60–85% | Normal: Target zone | No action |
| GPU utilization 85–90% | Warning: Approaching saturation | Pre-warm overflow path |
| GPU utilization > 90% | Alert: Saturated | Activate cloud overflow immediately |
| GPU utilization = 100% for > 5 min | Critical | Alert operator; investigate blocked processes |

---

## Routing Audit Log Format

Every routing decision must be logged:

```yaml
routing_event:
  timestamp: "YYYY-MM-DDThh:mm:ssZ"
  workflow_id: "<uuid>"
  task_type: "<task_type>"
  rule_applied: "<rule number or name>"
  route: "local | cloud"
  model: "<model_name>"
  local_utilization_pct: <number>
  estimated_cost_usd: <number>
  actual_cost_usd: <number>  # filled post-completion
  reason: "<human-readable reason>"
```