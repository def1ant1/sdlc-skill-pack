---
name: workflow-ab-testing
description: Defines workflow variants, splits live traffic between them, and performs statistical comparison of workflow outcomes.
metadata:
  version: "0.1.0"
  category: ml-ops
  owner: platform
  maturity: draft
  dependencies: ['reinforcement-optimizer', 'workflow-runtime']

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

Controlled experimentation framework for workflow configurations. Allows platform teams
to test workflow variant hypotheses (different skill orderings, model selections, prompt
changes) on live traffic with statistical rigor, then promotes winning variants automatically
when significance thresholds are met.

## Activation Triggers

- An operator registers a new workflow A/B experiment
- `reinforcement-optimizer` requests a live traffic split for a workflow optimization experiment
- An active experiment reaches its minimum sample size (statistical test ready)
- An experiment's control group shows a performance degradation (early stopping trigger)
- An operator requests experiment status or early termination

## Execution Protocol

1. **Experiment registration**: Accept experiment definition:
   - `control`: the current production workflow configuration
   - `variants`: list of challenger configurations (up to 4 variants per experiment)
   - `traffic_split`: percentage allocation per variant (must sum to 100%)
   - `primary_metric`: `quality_score` | `latency_p95` | `cost_per_run` | `user_rating`
   - `min_sample_size`: minimum completions per arm before statistical test
   - `max_duration_days`: safety timeout

2. **Traffic routing**: On each workflow invocation that matches the experiment scope,
   apply the traffic split using a deterministic hash of `{workflow_id, request_id}`
   to ensure consistent assignment across retries.

3. **Metric collection**: After each workflow completion, record outcome metrics for the
   assigned variant. Store in the experiment metrics store.

4. **Statistical analysis**: When any variant reaches `min_sample_size`:
   - Run a Welch's t-test (for continuous metrics) or chi-squared test (for binary outcomes)
   - Compute effect size (Cohen's d) and 95% confidence interval for the difference
   - Apply Bonferroni correction if testing multiple variants simultaneously

5. **Decision**: If `p < 0.05` and effect size is practically significant:
   - Winner: promote to 100% traffic; archive experiment with full results
   - No winner: if all variants are within noise of control, declare no winner and stop
   - Early stopping: if a variant shows significantly worse performance (p < 0.01), stop it immediately

## Output Format

```yaml
ab_experiment:
  experiment_id: "WF-EXP-2026-xxxxx"
  status: running | winner_found | no_winner | stopped_early
  arms:
    control:
      completions: 0
      primary_metric_mean: 0.0
    variant_a:
      completions: 0
      primary_metric_mean: 0.0
  p_value: null
  effect_size: null
  winner: null
  confidence_pct: 0.0
```

## Quality Gates

- Minimum 30 completions per arm before interim analysis
- Statistical significance threshold: p < 0.05 with effect size > 0.2 (small)

## References

- `references/` — Statistical test selection guide, traffic routing hash algorithm, early stopping rules
