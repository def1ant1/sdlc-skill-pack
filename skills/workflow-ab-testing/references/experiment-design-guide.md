# Workflow A/B Testing — Experiment Design Guide

## Experiment Types

| Type | What Varies | Example |
|------|------------|---------|
| Prompt variant | System prompt or few-shot examples | CoT vs. direct instruction |
| Model variant | Model ID or quantization | llama-3.1-8B vs. llama-3.1-13B |
| Workflow variant | Task decomposition or agent routing | Single-pass vs. multi-pass review |
| Config variant | Temperature, timeout, retry count | temperature=0.3 vs. 0.7 |
| Tool variant | Which external tool or skill is called | RAG vs. no-RAG |

---

## Experiment Design Schema

```yaml
ab_experiment:
  experiment_id: "AB-EXP-2026-xxxxx"
  name: "Code Review: Single-Pass vs. Multi-Pass"
  hypothesis: "Multi-pass review with separate security and style passes improves quality_score by ≥5% with acceptable latency increase"
  owner: "ml-ops-team"
  created_at: "2026-05-07T00:00:00Z"

  target:
    skill: "code-review"
    phase: production    # shadow | production

  allocation:
    unit: request        # request | user | session | tenant
    algorithm: thompson_sampling   # thompson_sampling | ucb1 | epsilon_greedy | fixed_split
    fixed_split_pct: null         # Only used if algorithm == fixed_split

  variants:
    - variant_id: "control"
      name: "Single-pass review"
      description: "Baseline: one LLM call covering all dimensions"
      is_control: true
      traffic_weight_initial: 0.50

    - variant_id: "multi-pass"
      name: "Multi-pass review"
      description: "Three sequential passes: security → correctness → style"
      is_control: false
      traffic_weight_initial: 0.50

  primary_metric:
    name: quality_score
    type: continuous
    higher_is_better: true
    minimum_detectable_effect: 0.05   # 5 percentage points

  guardrail_metrics:
    - name: latency_p95_ms
      threshold: 5000
      direction: must_not_exceed   # Abort if guardrail violated
    - name: error_rate_pct
      threshold: 2.0
      direction: must_not_exceed

  sample_size:
    min_per_variant: 50
    target_per_variant: 200
    max_duration_days: 30

  stopping_rules:
    early_stop_on_harm: true     # Stop immediately if guardrail violated
    early_stop_on_significance: true
    significance_threshold: 0.95  # P(winner is best) ≥ 95%
```

---

## Statistical Analysis Methods

### Thompson Sampling (Default for Online Experiments)

Continuously allocates traffic to better-performing variants without a fixed sample size. See `core/reinforcement-optimizer/references/rl-algorithm-specs.md` for full implementation.

**Best for:** Long-running production experiments where we want to minimize regret (serving bad outputs).

### Fixed-Horizon t-Test (for Offline / Shadow Experiments)

```python
from scipy import stats

def analyze_ab_results(
    control_scores: list[float],
    treatment_scores: list[float],
    alpha: float = 0.05,
) -> dict:
    t_stat, p_value = stats.ttest_ind(control_scores, treatment_scores)
    effect_size = (
        (sum(treatment_scores) / len(treatment_scores)) -
        (sum(control_scores) / len(control_scores))
    )
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < alpha,
        "effect_size": effect_size,
        "control_mean": sum(control_scores) / len(control_scores),
        "treatment_mean": sum(treatment_scores) / len(treatment_scores),
    }
```

---

## Traffic Allocation Strategies

### Shadow Mode (Pre-Production)

Both variants run on every request; only control output is returned to the caller. Treatment output is logged for offline comparison. Zero user impact.

```yaml
shadow_config:
  mode: shadow
  record_all_outputs: true
  latency_impact: control_path_only   # Shadow runs async; no latency added
```

### Live Split

Production traffic is split. Use only when:
- Shadow testing has already passed
- Guardrail metrics are actively monitored
- Rollback can be triggered in < 5 minutes

---

## Experiment Results Schema

```yaml
experiment_results:
  experiment_id: "AB-EXP-2026-xxxxx"
  analyzed_at: "2026-05-14T10:00:00Z"
  total_trials: 400
  duration_days: 7

  variant_results:
    - variant_id: "control"
      trials: 198
      primary_metric_mean: 0.791
      primary_metric_std: 0.082
      latency_p95_ms: 1200
      error_rate_pct: 0.3

    - variant_id: "multi-pass"
      trials: 202
      primary_metric_mean: 0.847
      primary_metric_std: 0.071
      latency_p95_ms: 2800
      error_rate_pct: 0.4

  statistical_conclusion:
    winner: "multi-pass"
    improvement_pct: 7.1
    p_winner_is_best: 0.963
    converged: true
    guardrails_violated: false

  recommendation: promote   # promote | no_improvement | inconclusive | abort

  promotion:
    requires_human_approval: false   # Auto-promote for non-P0 skills
    approved_by: null
    promoted_at: null
```

---

## Common Pitfalls

| Pitfall | Risk | Mitigation |
|---------|------|-----------|
| Novelty effect | Treatment looks better initially because it is new | Run for ≥ 7 days |
| Simpson's paradox | Aggregate metric hides subgroup harm | Segment results by task type |
| Metric gaming | Optimizing one metric while harming another | Define guardrail metrics before experiment |
| Insufficient sample | False positive due to low n | Enforce `min_per_variant: 50` |
| No holdout | Cannot measure long-term quality | Keep 10% holdout for final validation |