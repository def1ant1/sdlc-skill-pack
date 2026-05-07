# Experiment Design

Used by `skills/product-analytics/SKILL.md` to structure A/B experiments, compute
required sample sizes, define guardrail rules, and interpret results.

---

## Hypothesis Format

```
We believe that [change] for [audience segment]
will result in [expected outcome measured by primary metric]
because [reasoning / evidence].

Null hypothesis: No difference between control and variant.
```

**Example:**
```
We believe that adding an inline template gallery to the workflow creation modal
for new users (< 7 days) will increase workflow_created events within session
because first-time users hesitate when facing a blank canvas.

Null hypothesis: No difference in workflow_created rate between control and variant.
```

---

## Experiment Specification Template

```yaml
experiment:
  name: "<short-slug>"
  hypothesis: "<hypothesis statement>"
  owner: "<team or person>"
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"  # calculated; not set manually

  audience:
    segment: "<new_users | all_users | pro_users | enterprise_users>"
    traffic_allocation: 0.50  # fraction of segment exposed (0.0–1.0)
    split:
      control: 0.50   # fraction of exposed going to control
      variant_a: 0.50 # fraction of exposed going to variant

  primary_metric:
    name: "<event_name or computed metric>"
    type: "<conversion_rate | mean | revenue>"
    direction: increase  # increase | decrease

  guardrail_metrics:
    - name: "<metric>"
      max_degradation: 0.05  # 5% degradation triggers abort

  stats:
    significance_threshold: 0.05   # p < 0.05
    power: 0.80                    # 80% statistical power
    mde: 0.05                      # minimum detectable effect (relative)
    required_sample_per_variant: 0 # computed — see formula below
    estimated_run_days: 0          # computed

  status: draft  # draft | running | paused | completed | aborted
  result: null   # null | significant_win | significant_loss | inconclusive
```

---

## Sample Size Calculation

```
n = (2 × σ² × (z_α + z_β)²) / (MDE × μ)²
```

For conversion rates, use the simplified form:

```
n = (z_α + z_β)² × (p(1−p) + p'(1−p')) / (p' − p)²
```

Where:
- `p` = baseline conversion rate
- `p'` = p × (1 + MDE) = expected variant conversion rate
- `z_α` = 1.96 (for α = 0.05, two-tailed)
- `z_β` = 0.84 (for power = 0.80)

**Quick reference table** (two-tailed, α=0.05, power=0.80):

| Baseline Rate | MDE 5% | MDE 10% | MDE 20% |
|---|---|---|---|
| 10% | 14,744 | 3,788 | 987 |
| 20% | 24,197 | 6,194 | 1,606 |
| 30% | 29,076 | 7,441 | 1,927 |
| 50% | 31,344 | 8,022 | 2,076 |

All values are per variant. Minimum: 200 per variant regardless of formula output.

---

## Run Duration Rules

1. **Minimum**: 7 days — captures full weekly cycle (weekend vs weekday behavior)
2. **Maximum**: 42 days — longer experiments risk novelty effects and instrumentation drift
3. **Compute from sample size**: `days = required_sample / (daily_eligible_users × traffic_allocation)`
4. If computed days > 42: reduce scope (narrow audience) or increase MDE target

---

## Guardrail Metrics

Always include as guardrails:

| Guardrail | Abort threshold |
|---|---|
| Error rate | +5% relative increase |
| Page / workflow load time | +10% relative increase |
| Support ticket volume | +15% relative increase |
| Payment failure rate | +3% relative increase |
| Session duration | −15% relative decrease |

If any guardrail breaches threshold: **abort immediately, revert to control**.

---

## Statistical Significance Interpretation

| p-value | Result | Action |
|---|---|---|
| < 0.05 AND positive direction | Significant win | Ship variant |
| < 0.05 AND negative direction | Significant loss | Abort; do not ship |
| 0.05–0.20 | Trending; not significant | Extend run if feasible |
| > 0.20 | Inconclusive | Do not ship; rethink hypothesis |

**Never**: peek at results before planned end date and stop early due to significance.
**Exception**: guardrail breach or ethical/safety concern.

---

## Results Report Format

```
Experiment: <name>
Run dates: YYYY-MM-DD – YYYY-MM-DD
Samples: Control=N, Variant=N

Primary Metric:
  Control: X%
  Variant: Y%
  Relative lift: +Z%
  p-value: 0.0XX
  Result: [Significant Win | Significant Loss | Inconclusive]

Guardrail Metrics:
  [metric]: Control=X, Variant=Y, Change=+Z% [PASS | FAIL]

Decision: [Ship | Do Not Ship | Extend | Abort]
Reasoning: <1–2 sentences>

Next Steps:
  - <action 1>
  - <action 2>
```

---

## Multi-Variant Experiments

When testing > 1 variant:
- Apply Bonferroni correction: `adjusted_α = 0.05 / number_of_comparisons`
- For 2 variants vs control: `adjusted_α = 0.025`
- Increase sample size accordingly (use adjusted α in the sample size formula)
- Ship only the winning variant, not the runner-up, unless effect sizes are near-identical

---

## Experiment Registry

All experiments must be registered before launching. Minimum registration fields:

```yaml
id: EXP-YYYYMMDD-NNN
name: <slug>
owner: <name>
status: draft
hypothesis: <text>
primary_metric: <metric>
start_date: <YYYY-MM-DD>
```

Assign sequential IDs within the year. Log final result upon experiment closure.