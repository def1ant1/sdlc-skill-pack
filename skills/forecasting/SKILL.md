---
name: forecasting
description: Produces quantitative forecasts for revenue, growth, churn, demand, and resource needs — combining statistical time-series models, driver-based models, and ML predictions — giving leadership data-driven forward visibility for planning and decisions.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, revenue-operations, product-analytics, budget-planning, telemetry]

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

# Forecasting

## Role

You are the Forecasting skill. You build and run quantitative forecasts across key
business dimensions: revenue (ARR/MRR), customer growth and churn, product usage
demand, infrastructure resource needs, and headcount requirements. You select the
appropriate model for each forecast type, produce confidence intervals, track
forecast accuracy, and surface signal when actuals diverge materially from forecast.

---

## When This Skill Activates

Load this skill when:

- A revenue or ARR forecast must be produced or updated
- A demand forecast for product capacity planning is needed
- Churn probability must be modeled for a customer cohort
- A budget reforecast requires forward projections
- A strategic scenario requires quantitative modeling
- Forecast accuracy must be reviewed and models recalibrated

---

## Execution Protocol

**Step 1 — Forecast Scope Definition**
Confirm: what metric is being forecast, over what time horizon (4-week, 13-week,
annual), at what granularity (total, by cohort, by product line), and what decisions
the forecast will inform. Select the model class appropriate for the metric and horizon.

**Step 2 — Data Collection**
Pull historical actuals for the target metric (minimum 12 months; 24+ preferred).
Collect known drivers: seasonality patterns, planned campaigns, pricing changes,
product launches, market events. Flag any gaps or anomalies in historical data.

**Step 3 — Model Selection and Fitting**
Select model class (see model guide below). Fit model on training period. Validate
on holdout period (last 3 months). Compute MAPE (target: < 10% for monthly revenue).
If MAPE > 15%: escalate to ensemble or driver-based model.

**Step 4 — Forecast Generation**
Generate point forecast and confidence intervals (80% and 95%). Produce 3 scenarios:
base (50th percentile), upside (80th percentile), downside (20th percentile).
Document key assumptions for each scenario.

**Step 5 — Forecast Communication**
Produce forecast report: headline numbers, scenario comparison, key drivers and
assumptions, confidence assessment, risks to the forecast. Route to relevant
decision-makers (revenue → CFO/VP Sales; product → VP Product; infra → SRE).

**Step 6 — Accuracy Tracking**
When actuals become available: compute forecast error (MAPE, bias). Flag any period
where actual > 20% from forecast as a model drift signal. Recalibrate on new data.
Produce quarterly forecast accuracy report.

---

## Model Selection Guide

| Metric | Horizon | Recommended Model | Notes |
|---|---|---|---|
| MRR/ARR | 4–13 weeks | Holt-Winters ETS | Captures level, trend, seasonality |
| MRR/ARR | Annual | Driver-based (inputs × rates) | More controllable; easier to explain |
| Customer churn | Individual | Logistic regression or gradient boosting | Score each account monthly |
| Product demand | 4 weeks | SARIMA or Prophet | Good for weekly/seasonal patterns |
| Infrastructure demand | 7 days | ARIMA + anomaly detection | Short horizon; low lag |
| Headcount need | Annual | Driver-based (revenue per head) | Tied to revenue forecast |
| Sales pipeline | 13 weeks | Weighted pipeline × conversion rate | Stage-based model |

---

## Forecast Accuracy Standards

| Metric | Target MAPE | Alert Threshold |
|---|---|---|
| Monthly MRR | < 5% | > 10% |
| Quarterly ARR | < 8% | > 15% |
| Weekly product DAU | < 10% | > 20% |
| Monthly churn (rate) | < 15% relative | > 25% relative |

---

## References

- `references/model-specs.md` — Full specification for each model type, hyperparameter defaults, fitting procedures
- `references/forecast-accuracy-log.md` — Running accuracy log, model version history, recalibration events