# Business Simulation Methodology Reference

## Simulation Model Types

### 1. Monte Carlo Simulation

**Use for:** Quantifying uncertainty in financial projections, risk assessment, scenario analysis.

```
Algorithm:
1. Define input distributions for each uncertain variable
2. FOR each trial in N_trials (N ≥ 10,000 for stable estimates):
   a. Sample one value per uncertain variable from its distribution
   b. Compute output metric(s) using the business model formula
   c. Record output
3. Aggregate: mean, std, percentiles (P5, P25, P50, P75, P95), VaR

Output: Output distribution with confidence intervals
```

**Distribution selection guide:**

| Variable Type | Recommended Distribution | Parameters |
|---|---|---|
| Revenue (asymmetric upside) | Log-normal | μ, σ derived from historical data |
| Cost (bounded, uncertain) | Triangular | min, mode, max |
| Binary event (occurs/doesn't) | Bernoulli | p = probability of occurrence |
| Correlated variables | Gaussian copula | Correlation matrix |
| Time-to-event | Exponential or Weibull | λ (rate) or (k, λ) |

**Convergence check:**
```
convergence_tolerance = 0.01  # 1% change in P50 across 1000 additional trials
IF |P50(N) - P50(N-1000)| / P50(N-1000) < convergence_tolerance:
    CONVERGED
```

---

### 2. System Dynamics Model

**Use for:** Feedback loops, stock-and-flow dynamics, long-horizon organizational behavior.

```
Core constructs:
- Stocks: Accumulated quantities (e.g., customer_base, employee_count)
- Flows: Rates of change (e.g., customer_acquisition_rate, churn_rate)
- Feedback loops: Causal relationships between stocks and flows

State update (Euler method, dt = 1 period):
  stock[t+1] = stock[t] + (inflow[t] - outflow[t]) × dt

Example — SaaS customer dynamics:
  customer_base[t+1] = customer_base[t] + (new_customers[t] - churned_customers[t])
  new_customers[t] = awareness × conversion_rate × market_size
  churned_customers[t] = customer_base[t] × churn_rate
  churn_rate = f(product_quality, price_competitiveness, support_quality)
```

---

### 3. Agent-Based Model

**Use for:** Emergent market behavior, competitive dynamics, adoption modeling.

```
Each agent has:
  - State: {segment, adoption_status, satisfaction, influence_score}
  - Decision rule: IF (social_influence > threshold AND price ≤ willingness_to_pay):
                       ADOPT product
  - Interaction: influence_score × (neighbor_adoption_rate - current_adoption_rate)

Simulation loop:
  FOR t = 1 to T_max:
    FOR each agent a:
      a.perceive_environment()
      a.update_state()
      a.interact_with_neighbors()
    record_aggregate_metrics(t)
```

---

## Scenario Definition Format

```yaml
scenario:
  id: "SCN-MARKET-ENTRY-001"
  name: "Aggressive Market Entry — Low Price Strategy"
  description: "Enter market at 20% below competitor pricing with high marketing spend"
  type: "what_if"  # what_if | stress_test | sensitivity | base_case

  assumptions:
    pricing_discount_pct: -20
    marketing_spend_multiplier: 2.0
    time_to_market_months: 6
    initial_market_share_target: 0.05

  uncertain_variables:
    market_growth_rate:
      distribution: normal
      mean: 0.08
      std: 0.03
    competitor_response:
      distribution: categorical
      values: ["no_response", "price_match", "aggressive_response"]
      probabilities: [0.30, 0.45, 0.25]

  constraints:
    budget_cap_usd: 5000000
    break_even_required_by_month: 24
    minimum_margin_pct: 0.15
```

---

## Sensitivity Analysis Protocol

### One-at-a-Time (OAT) Sensitivity

```
FOR each input_variable v:
    baseline_output = model(baseline_inputs)
    FOR delta IN [-20%, -10%, +10%, +20%]:
        perturbed_output = model(baseline_inputs WITH v × (1 + delta))
        sensitivity[v][delta] = (perturbed_output - baseline_output) / baseline_output
    elasticity[v] = sensitivity[v][+10%] / 0.10  # % output change per % input change
```

**Tornado chart:** Sort variables by |elasticity| descending. Top 5 are key drivers.

### Global Sensitivity (Sobol Indices)

For complex models with interaction effects:
```
S_i = Var(E[Y | X_i]) / Var(Y)  # First-order Sobol index for variable i
S_Ti = 1 - Var(E[Y | X_-i]) / Var(Y)  # Total-order index

Variables with S_Ti > 0.10 warrant deep analysis.
```

---

## Output Format

```yaml
simulation_result:
  simulation_id: "SIM-20260507-001"
  scenario_id: "SCN-MARKET-ENTRY-001"
  model_type: "monte_carlo"
  n_trials: 50000
  runtime_seconds: 42

  primary_metric:
    name: "net_present_value_usd"
    p5: -2100000
    p25: 800000
    p50: 2400000
    p75: 4100000
    p95: 7800000
    mean: 2520000
    std: 2180000
    probability_positive: 0.73

  risk_metrics:
    var_95: -2100000  # Value at Risk (5th percentile)
    cvar_95: -3400000  # Conditional VaR (mean of worst 5%)
    probability_of_loss: 0.27
    maximum_drawdown_p95: -5200000

  key_drivers:
    - variable: "market_growth_rate"
      elasticity: 1.82
      rank: 1
    - variable: "competitor_response"
      elasticity: -0.94
      rank: 2

  recommendation: "PROCEED_WITH_CONDITIONS"
  conditions: ["Secure $5M budget before launch", "Monitor churn monthly"]
```