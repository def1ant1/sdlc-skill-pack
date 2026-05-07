# Prediction Model Catalog

## Overview

Catalog of prediction model types available in the predictive-reasoning skill, with
selection criteria by forecast horizon and data characteristics, calibration requirements,
and uncertainty quantification methods.

---

## Model Type Catalog

### ARIMA / SARIMA

**Type:** Statistical time series forecasting
**Strengths:** Interpretable; handles autocorrelation; well-understood confidence intervals
**Limitations:** Linear only; requires stationarity; struggles with structural breaks

**Selection criteria:**
- Data: univariate time series with clear autocorrelation
- Horizon: short to medium (1–52 periods ahead)
- History required: ≥ 2× the forecast horizon, minimum 50 observations
- Seasonality: SARIMA for seasonal patterns; ARIMA for non-seasonal

**Calibration requirements:**
- ADF test for stationarity (d parameter selection)
- ACF/PACF analysis for p,q parameter selection
- Information criterion (AIC/BIC) for model selection
- Ljung-Box test for residual independence

---

### Prophet (Facebook/Meta)

**Type:** Decomposable time series model
**Strengths:** Handles holidays, missing data, multiple seasonalities; robust to outliers
**Limitations:** Requires domain specification of seasonalities; less accurate for noisy data

**Selection criteria:**
- Data: daily or sub-daily time series with multiple seasonal patterns
- Horizon: medium (weeks to months)
- History required: ≥ 1 full seasonal cycle, minimum 2 years for annual seasonality
- Use case: business metrics with known event effects (holidays, promotions)

**Calibration requirements:**
- Holiday calendar specification (organizational and public holidays)
- Seasonality mode selection (additive vs. multiplicative)
- Changepoint detection sensitivity tuning

---

### XGBoost / LightGBM (Gradient Boosting)

**Type:** Supervised ML, tabular features
**Strengths:** Excellent on tabular data; handles non-linear relationships; fast training
**Limitations:** Requires feature engineering; can overfit with limited data; poor uncertainty quantification

**Selection criteria:**
- Data: tabular with ≥ 10 useful features including lagged values
- Horizon: any (point-in-time prediction with manual feature construction)
- History required: ≥ 1,000 training examples
- Use case: classification and regression with rich feature sets

**Calibration requirements:**
- Feature importance analysis (SHAP values)
- Cross-validation (time-series aware — no data leakage)
- Hyperparameter tuning (learning rate, max depth, n_estimators)
- Calibration plot for classification tasks (probability calibration)

---

### LSTM / Temporal Fusion Transformer

**Type:** Deep learning, sequence models
**Strengths:** Captures long-range dependencies; handles multivariate inputs; learns complex patterns
**Limitations:** Requires large datasets; slow to train; black-box; overconfident uncertainty

**Selection criteria:**
- Data: multivariate time series; ≥ 10,000 training examples
- Horizon: any (direct or recursive multi-step)
- History required: ≥ 2 years of daily data; ≥ 6 months of hourly data
- Use case: complex forecasting where statistical models underperform

**Calibration requirements:**
- Validation set (time-based split) for early stopping
- Dropout for uncertainty estimation (MC-Dropout)
- Prediction interval calibration (verify coverage on holdout set)

---

### Bayesian Structural Time Series (BSTS)

**Type:** Probabilistic state-space model
**Strengths:** Native uncertainty quantification; interpretable components; handles sparse data
**Limitations:** Computationally expensive; requires Bayesian expertise; slow inference

**Selection criteria:**
- Data: time series where quantified uncertainty is critical for decisions
- Horizon: short to medium
- History required: ≥ 50 observations
- Use case: causal impact analysis, anomaly detection, uncertainty-critical decisions

**Calibration requirements:**
- Prior specification (trend variance, seasonal variance, observation noise)
- MCMC convergence check (R-hat < 1.05)
- Posterior predictive check for model fit

---

## Forecast Horizon → Model Selection Guide

| Horizon | Recommended Models | Notes |
|---|---|---|
| 1–7 periods | ARIMA, Prophet | Statistical models sufficient |
| 8–52 periods | Prophet, BSTS, XGBoost | Seasonal patterns matter |
| 53–104 periods | TFT, LSTM, BSTS | Deep models capture long-range dependencies |
| 105+ periods | Scenario-based Monte Carlo | Uncertainty dominates; use distributions not point estimates |

---

## Uncertainty Quantification Methods

| Method | Models | Output | Notes |
|---|---|---|---|
| Analytical CI | ARIMA, SARIMA | Gaussian confidence intervals | Valid when residuals are normal |
| Bootstrap | XGBoost, any | Empirical percentile intervals | Computationally intensive |
| Conformal prediction | Any ML model | Distribution-free prediction intervals | Coverage guarantee on holdout set |
| MC-Dropout | LSTM, TFT | Monte Carlo uncertainty estimates | Approximate Bayesian inference |
| MCMC posterior | BSTS | Full posterior distribution | Gold standard; computationally expensive |

**Required calibration test:** For any prediction interval, verify on a held-out test set
that the nominal coverage (e.g., 90% interval) matches the empirical coverage within ±5
percentage points. If coverage is off, apply Platt scaling or isotonic regression.

---

## Model Performance Tracking Schema

```yaml
model_performance_record:
  model_id: "PM-REVENUE-ARIMA-001"
  model_type: "ARIMA"
  target_metric: "monthly_revenue"
  forecast_horizon: 3                # 3 months ahead

  evaluation_period:
    start: "2025-01-01"
    end: "2026-01-01"
    observations: 12

  accuracy_metrics:
    MAE: 42300
    MAPE: 0.034                      # 3.4%
    RMSE: 58900
    coverage_90pct_interval: 0.917   # Empirical vs. nominal 0.90

  drift_detection:
    last_check: "2026-05-01"
    drift_detected: false
    retrain_recommended: false

  next_scheduled_retrain: "2026-08-01"
```