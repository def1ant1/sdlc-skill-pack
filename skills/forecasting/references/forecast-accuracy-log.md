# Forecast Accuracy Log

## Purpose

This log tracks forecast accuracy over time to detect model drift, identify
systematic biases, and trigger model recalibration when accuracy degrades.

---

## Accuracy Log Format

```yaml
accuracy_entry:
  id: "ACC-YYYYMM-NNN"
  metric: "<metric name>"
  model_version: "<model type and version>"
  forecast_date: "YYYY-MM-DD"      # when forecast was made
  forecast_horizon_days: N          # how far ahead the forecast looked
  period_start: "YYYY-MM-DD"
  period_end: "YYYY-MM-DD"
  forecasted_value: X.XX
  actual_value: X.XX
  absolute_error: X.XX
  percentage_error: X.X%           # positive = over-forecast
  mape_contribution: X.X%
  within_80_ci: true | false        # was actual within 80% confidence interval?
  within_95_ci: true | false
  notes: "<any events that explain a large error>"
```

---

## Running Accuracy Summary (Template)

```
FORECAST ACCURACY REPORT — [Month YYYY]
=========================================

METRIC: Monthly MRR
Model: Holt-Winters ETS (v2.1)
Rolling 6-month MAPE: X.X%  (target: < 5%)
Bias: +X.X% (over-forecasting by X%)

METRIC: Weekly DAU
Model: SARIMA (1,1,1)(1,0,1)52
Rolling 6-month MAPE: X.X%  (target: < 10%)

METRIC: Customer churn (quarterly)
Model: Cohort churn model (v1.3)
Rolling accuracy (30-day): X.X%  (target: < 15% relative)

RECALIBRATION TRIGGERS DETECTED: [list any metric > alert threshold]
MODELS RECALIBRATED THIS MONTH: [list if any]
```

---

## Recalibration Triggers

Automatic recalibration is triggered when:

| Metric | Alert Threshold | Action |
|---|---|---|
| MRR MAPE (rolling 3-month) | > 10% | Refit Holt-Winters; consider driver-based |
| ARR MAPE (quarterly) | > 15% | Review key assumptions; refit |
| DAU MAPE (rolling 4-week) | > 20% | Refit SARIMA; check for seasonality shift |
| Churn model accuracy | > 25% relative error | Retrain cohort model; review features |
| 80% CI miss rate | > 40% of periods | Model is systematically wrong; rebuild |

---

## Historical Accuracy Ledger

| Date | Metric | Model | Horizon | MAPE | Bias | 80% CI Hit Rate |
|---|---|---|---|---|---|---|
| 2026-04 | MRR | Holt-Winters | 4-week | X.X% | X.X% | X% |
| 2026-03 | MRR | Holt-Winters | 4-week | X.X% | X.X% | X% |
| 2026-02 | MRR | Holt-Winters | 4-week | X.X% | X.X% | X% |

*Entries added monthly when actuals are confirmed.*

---

## Model Version History

| Version | Model | Deployed | Retired | Notes |
|---|---|---|---|---|
| v1.0 | Simple moving average | 2025-01 | 2025-06 | Replaced by ETS for better seasonality |
| v2.0 | Holt-Winters ETS | 2025-06 | 2025-12 | Retrained with expanded training window |
| v2.1 | Holt-Winters ETS | 2026-01 | Active | Tuned alpha after Q4 2025 anomaly |