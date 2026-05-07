# Capacity Planning Model Reference

## Capacity Planning Framework

### Step 1: Demand Forecasting

```python
def forecast_demand(historical_metrics, horizon_days=90):
    """
    Forecast future request demand from historical data.
    Uses decomposition: trend × seasonality × residual
    """
    from statsmodels.tsa.seasonal import STL
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    # STL decomposition to separate trend and seasonality
    stl = STL(historical_metrics.rps_hourly, period=168)  # 168h = weekly cycle
    result = stl.fit()

    trend = result.trend
    seasonal = result.seasonal
    residual = result.resid

    # Fit SARIMA on detrended/deseasoned residual for stochastic component
    sarima = SARIMAX(residual, order=(2, 1, 2), seasonal_order=(1, 1, 1, 168))
    sarima_fit = sarima.fit()

    # Forecast
    forecast = sarima_fit.forecast(steps=horizon_days * 24)

    return DemandForecast(
        p50=trend_extrapolation(trend) + seasonal_projection(seasonal) + forecast,
        p75=demand_p75_with_uncertainty(forecast, confidence=0.75),
        p95=demand_p95_with_uncertainty(forecast, confidence=0.95)
    )
```

### Step 2: Capacity Sizing

```
For each capability tier T, compute required capacity to meet SLO:

  target_utilization[T] = 0.70  # 70% utilization target (30% headroom for bursts)

  required_capacity[T] = demand_p95[T] / (μ[T] × target_utilization[T])

  where:
    demand_p95[T] = P95 forecast of requests per second for tier T
    μ[T] = throughput per replica for tier T (req/sec/replica)

  round up to nearest integer (ceil)

  safety_margin = max(2 replicas, 20% of required_capacity)
  planned_capacity[T] = required_capacity[T] + safety_margin
```

### Step 3: Cost Optimization

```python
def optimize_capacity(demand_forecast, model_catalog, budget_usd_per_month):
    """
    Minimize cost while meeting SLO constraints.
    Uses linear programming for optimal mix of model tiers.
    """
    from scipy.optimize import linprog

    # Variables: x[i] = number of replicas for model_i
    # Objective: minimize Σ cost[i] × x[i]
    # Constraints:
    #   Σ throughput[i][tier] × x[i] >= demand[tier] for each tier
    #   Σ cost[i] × x[i] <= budget
    #   x[i] >= min_replicas[i]
    #   x[i] <= max_replicas[i]

    costs = [m.cost_per_hour for m in model_catalog]
    throughputs = [[m.throughput_rps[tier] for m in model_catalog] for tier in TIERS]
    demands = [demand_forecast.p95[tier] for tier in TIERS]

    result = linprog(
        c=costs,
        A_ub=-np.array(throughputs),  # Negated for ≥ constraint
        b_ub=-np.array(demands),
        bounds=[(m.min_replicas, m.max_replicas) for m in model_catalog],
        method='highs'
    )

    return CapacityPlan(
        replicas_per_model=result.x,
        total_monthly_cost=sum(result.x * costs) * 720,  # 720h/month
        cost_vs_budget_pct=(sum(result.x * costs) * 720 / budget_usd_per_month) * 100
    )
```

---

## Capacity Metrics

| Metric | Definition | Target |
|---|---|---|
| Utilization | actual_load / provisioned_capacity | 60–75% (average) |
| Peak utilization | max_load / provisioned_capacity | ≤ 90% |
| Headroom | 1 - utilization | ≥ 25% for burst absorption |
| Cost efficiency | actual_useful_work / capacity_cost | Maximize |
| SLO attainment | requests_meeting_latency_SLO / total_requests | ≥ 99.5% |

---

## Rebalancing Triggers

### Horizontal Scaling Triggers

```yaml
scale_out_triggers:
  - metric: "p95_latency > latency_budget × 0.85"
    action: "add 2 replicas"
    cooldown_minutes: 5

  - metric: "avg_utilization > 0.75 for 5 consecutive minutes"
    action: "add 1 replica"
    cooldown_minutes: 10

  - metric: "queue_depth > max_batch_size × 3"
    action: "add 1 replica"
    cooldown_minutes: 5

scale_in_triggers:
  - metric: "avg_utilization < 0.40 for 15 consecutive minutes"
    action: "remove 1 replica"
    cooldown_minutes: 15
    min_replicas: 2  # Never scale below minimum

  - metric: "off_peak_hours AND utilization < 0.30"
    action: "scale to minimum_replicas[tier]"
    cooldown_minutes: 30
```

### Vertical Scaling Triggers

```yaml
upgrade_triggers:
  - condition: "p95_latency cannot be met even at max_replicas"
    action: "migrate to higher capability tier"
    requires: "manual approval"

  - condition: "GPU memory OOM events > 0 in 1 hour"
    action: "migrate to model with larger GPU memory"
    requires: "immediate action"

downgrade_triggers:
  - condition: "capability tier is over-provisioned for actual task distribution"
    threshold: "> 60% of tasks would pass quality bar on lower tier"
    action: "evaluate migration to lower tier for cost savings"
    requires: "quarterly review"
```

---

## Capacity Plan Document

```yaml
capacity_plan:
  plan_id: "CAP-2026-Q3"
  planning_period: "2026-07 to 2026-09"
  created_at: "2026-05-07"
  next_review: "2026-06-07"

  demand_forecast:
    method: "SARIMA + STL"
    forecast_p50_peak_rps: 1800
    forecast_p95_peak_rps: 2400
    growth_rate_monthly_pct: 12
    confidence_interval_80: [1600, 2900]

  planned_capacity:
    nano_tier:
      replicas: 8
      cost_per_month_usd: 1200
    standard_tier:
      replicas: 12
      cost_per_month_usd: 6000
    advanced_tier:
      replicas: 6
      cost_per_month_usd: 8400

  total_monthly_cost_usd: 15600
  budget_usd_per_month: 18000
  budget_utilization_pct: 86.7

  risk_assessment:
    demand_exceeds_capacity_probability: 0.04  # P(demand > planned capacity)
    slo_breach_probability: 0.008
    cost_overrun_probability: 0.11  # If growth is at P95

  contingency_plan:
    trigger: "peak_rps > 2400 for > 30 minutes"
    action: "emergency scale-out to burst_capacity (pre-approved)"
    burst_capacity_replicas: 4  # Additional replicas on standby
    burst_capacity_cost_usd_per_hour: 180
```