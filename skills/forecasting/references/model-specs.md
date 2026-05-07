# Forecasting Model Specifications

## Model Inventory

### 1. Holt-Winters Exponential Smoothing (ETS)

**Use case**: MRR/ARR with trend and seasonality (4–13 week horizon).

**Parameters**:
```
alpha (level smoothing):    0.2–0.5  (higher = more weight on recent)
beta  (trend smoothing):    0.1–0.3
gamma (seasonal smoothing): 0.1–0.3
seasonal_periods: 12 (monthly) or 52 (weekly)
model: additive (constant variance) or multiplicative (growing variance)
```

**Fitting procedure**:
1. Split data: 80% train, 20% validation (most recent 20%)
2. Fit model on train set using grid search over parameter space
3. Select parameters minimizing MAPE on validation set
4. Refit on full dataset with selected parameters
5. Generate forecast with 80% and 95% confidence intervals

**MAPE target**: < 5% for monthly MRR (30-day horizon).

---

### 2. SARIMA (Seasonal ARIMA)

**Use case**: Product usage demand, weekly patterns (4-week horizon).

**Parameters**:
```
p (AR order): 1–3
d (differencing): 0–2
q (MA order): 0–3
P, D, Q (seasonal): same ranges
s (seasonal period): 7 (weekly) or 12 (monthly)
```

**Selection**: Use AIC/BIC for automatic order selection. Use `pmdarima.auto_arima()` with appropriate constraints.

**MAPE target**: < 10% for weekly DAU.

---

### 3. Prophet (Facebook/Meta)

**Use case**: Time series with strong seasonality, holidays, or known trend change points.

```python
from prophet import Prophet

model = Prophet(
    changepoint_prior_scale=0.05,    # flexibility of trend changes
    seasonality_prior_scale=10,      # strength of seasonality
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
)
model.add_country_holidays(country_name='US')
model.fit(df)  # df must have columns: ds (datetime), y (metric)

future = model.make_future_dataframe(periods=13, freq='W')
forecast = model.predict(future)
```

**MAPE target**: < 10% for weekly metrics.

---

### 4. Driver-Based Model

**Use case**: ARR with known business drivers; annual planning.

```
ARR_forecast = (beginning_ARR)
             + (new_customer_adds × avg_ACV)
             + (expansion_rate × beginning_ARR)
             - (churn_rate × beginning_ARR)

Where:
  avg_ACV = average annual contract value (from pipeline data)
  expansion_rate = historical NRR - 1 - churn_rate
  churn_rate = historical gross churn (by month)
```

**Calibration**: Recalibrate monthly with actual values. Update assumptions on each reforecast cycle.

---

### 5. Cohort-Based Churn Model

**Use case**: Customer-level churn probability scoring.

**Features** (input to gradient boosted classifier):
- Days since last login
- Feature adoption score (count of features used in last 30 days)
- Support ticket volume (last 90 days)
- MRR change last 90 days
- NPS response (if available)
- Contract end date proximity (days)
- Health score percentile

**Labels**: Churned within 90 days (binary).

**Training**: Retrain monthly on 24 months of historical data. Evaluate on 3-month holdout.

**Output**: Probability score 0–1 for each account. Threshold 0.5 → at-risk flag.

---

## Model Performance Log Format

```yaml
model_run:
  model_type: "holt-winters | sarima | prophet | driver-based | churn-cohort"
  metric: "<metric being forecast>"
  run_date: "YYYY-MM-DD"
  horizon_days: N
  training_period: "YYYY-MM-DD to YYYY-MM-DD"
  validation_period: "YYYY-MM-DD to YYYY-MM-DD"
  validation_mape: X.X%
  validation_bias: X.X%    # positive = over-forecast, negative = under-forecast
  parameters: {}
  decision: "deploy | hold | retrain"
  deployed_at: "YYYY-MM-DD"
```