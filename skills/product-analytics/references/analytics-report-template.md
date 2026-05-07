# Analytics Report Template

## Weekly Product Metrics Report

```
PRODUCT METRICS REPORT — Week of YYYY-MM-DD
============================================

HEADLINE
  <One sentence describing the most notable product metric movement this week>

ACQUISITION & ACTIVATION
  New signups:           N  (+X% WoW)
  Trial-to-paid conv:    X%  (target: Y%)
  Activation rate:       X%  (target: Y%)
  Activation definition: <"first value moment" = user completed X>

ENGAGEMENT
  DAU:                   N  (+X% WoW)
  MAU:                   N  (+X% MoM)
  DAU/MAU ratio:         X%  (target: Y%)
  D7 retention:          X%  (target: Y%)
  D30 retention:         X%  (target: Y%)

TOP FEATURES (by usage, last 7 days)
  1. [Feature]: N users (X% of DAU)
  2. [Feature]: N users (X% of DAU)
  3. [Feature]: N users (X% of DAU)

EXPERIMENTS RUNNING
  [Experiment name]: Control X%, Treatment Y%, N users/arm
  Primary metric: [metric] | Current lift: +X% | Status: Running | Days left: N

EXPERIMENTS CONCLUDED
  [Experiment name]: [SHIP | HOLD] — [one line summary of result]

ALERTS
  [Any metric outside threshold — include metric, current value, target, and delta]

NOTES
  [Any context that explains unusual movements — launches, bugs, seasonality]
```

---

## Monthly Product Report

Additional sections for monthly:

```
COHORT RETENTION TABLE
  Month   | D0  | D7  | D14 | D30 | D60 | D90
  --------|-----|-----|-----|-----|-----|-----
  Jan 2026| 100%| X%  | X%  | X%  | X%  | X%
  Feb 2026| 100%| X%  | X%  | X%  | X%  | X%

FEATURE ADOPTION HEATMAP
  Feature          | Adopters | % of MAU | Trend
  User profile     | N        | X%       | ↑
  Dashboard        | N        | X%       | →
  API integration  | N        | X%       | ↓

NORTH STAR METRIC TREND
  [Chart: 13-week rolling north star metric with baseline and target]
  Current: X | Target: Y | Baseline: Z | 12-week trend: ↑/↓ X%
```

---

## Experiment Results Template

```
EXPERIMENT RESULTS
==================
Name:         [experiment name]
Hypothesis:   If we [change], then [metric] will [direction] by [amount]
              because [reasoning].
Duration:     YYYY-MM-DD to YYYY-MM-DD (N days)
Traffic:      50% control / 50% treatment — N users per arm

PRIMARY METRIC
  Control:    X% (±Y% 95% CI)
  Treatment:  X% (±Y% 95% CI)
  Lift:       +X% | p-value: 0.0XX | Statistical power: X%
  Significant: YES / NO (threshold: p < 0.05)

GUARDRAIL METRICS
  [Metric]: Control X%, Treatment Y% — [OK | VIOLATION]
  [Metric]: Control X%, Treatment Y% — [OK | VIOLATION]

DECISION: SHIP / HOLD / ITERATE
Rationale: [1-2 sentences explaining the decision]

CAVEATS: [Any limitations or confounders to be aware of]
```

---

## KPI Alert Thresholds

| Metric | Amber | Red | Action |
|---|---|---|---|
| Activation rate | < 30% | < 20% | Investigate onboarding funnel |
| D30 retention | < 25% | < 15% | Product quality review |
| DAU/MAU | < 15% | < 10% | Engagement investigation |
| Trial conversion | < 10% | < 5% | Sales + product review |
| North star drop | > 5% WoW | > 15% WoW | Emergency product review |