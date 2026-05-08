# Revenue Optimization — Models & Frameworks

## Churn Prediction Model

### Input Features

| Feature | Weight | Source |
|---------|--------|--------|
| Days since last login | High | Product events |
| Usage trend (30d vs. 60d) | High | Product events |
| Health score (current) | High | customer-success |
| Support tickets (open P0/P1) | Medium | ITSM |
| NPS score (last response) | Medium | CRM |
| Feature adoption breadth | Medium | Product events |
| Days until renewal | Medium | ERP |
| Seats used / seats licensed | Low | CRM |
| Payment failures (last 90d) | High | ERP |

### Churn Risk Score Formula

```python
def churn_risk_score(features: dict) -> float:
    """Returns churn risk in [0, 1]. Higher = more likely to churn."""
    score = 0.0

    # Recency: days since last login
    days_inactive = features.get("days_since_last_login", 0)
    if days_inactive > 30:
        score += 0.25
    elif days_inactive > 14:
        score += 0.10

    # Usage trend: declining usage
    usage_trend = features.get("usage_trend_pct", 0)  # negative = declining
    if usage_trend < -0.30:
        score += 0.20
    elif usage_trend < -0.10:
        score += 0.10

    # Health score
    health = features.get("health_score", 100)  # [0, 100]
    if health < 30:
        score += 0.25
    elif health < 60:
        score += 0.10

    # Open P0/P1 tickets
    if features.get("open_critical_tickets", 0) > 0:
        score += 0.10

    # NPS detractor
    nps = features.get("nps_score", 9)
    if nps is not None and nps <= 6:
        score += 0.10

    # Payment failure
    if features.get("recent_payment_failures", 0) > 0:
        score += 0.15

    return min(1.0, score)
```

### Intervention Tiers

| Risk Score | Tier | Intervention |
|-----------|------|-------------|
| ≥ 0.70 | Critical | Executive outreach + CS manager call within 24h |
| 0.45–0.69 | High | CS check-in call + usage tips email within 48h |
| 0.25–0.44 | Medium | Automated re-engagement sequence |
| < 0.25 | Low | Standard engagement; no intervention |

---

## LTV / CAC Model

```
LTV = ARPU / Monthly Churn Rate
    = (MRR / Active Customers) / (Churned Customers / Active Customers)

CAC = Total Sales & Marketing Spend / New Paying Customers Acquired

LTV:CAC Ratio = LTV / CAC  (Target: ≥ 3:1)

Payback Period (months) = CAC / (ARPU × Gross Margin Pct)
```

### LTV:CAC by Segment Template

| Segment | ARPU | Churn Rate | LTV | CAC | LTV:CAC | Payback (mo) | Status |
|---------|------|-----------|-----|-----|---------|-------------|--------|
| SMB (Starter) | $150 | 4.0% | $3,750 | $800 | 4.7:1 | 7 | Healthy |
| Mid-Market (Growth) | $600 | 2.0% | $30,000 | $4,000 | 7.5:1 | 9 | Healthy |
| Enterprise | $3,000 | 0.5% | $600,000 | $25,000 | 24:1 | 11 | Healthy |

---

## Pricing Elasticity Model

### Van Westendorp Price Sensitivity Meter

Four survey questions:
1. At what price would you consider this product **too expensive** to buy?
2. At what price would you consider this product **expensive, but still worth considering**?
3. At what price would you consider this product a **bargain**?
4. At what price would you consider this product **too cheap to trust**?

Plot cumulative distributions and find intersections:
- **Acceptable Price Range (APR):** Between "too cheap" and "too expensive" intersections
- **Optimal Price Point (OPP):** Intersection of "too expensive" and "too cheap" curves
- **Indifference Price Point (IPP):** Intersection of "expensive" and "bargain" curves

### Price Increase Revenue Impact Model

```
Scenario: P% price increase for new customers; E% churn elasticity for existing

New customer revenue impact:
  Δ_new = current_new_mrr × P / 100

Existing customer impact (if price increase applied):
  Churned_mrr = existing_mrr × E × P / 100
  Δ_existing = existing_mrr × P / 100 - Churned_mrr

Net NRR impact:
  ΔNRR = (Δ_existing / starting_mrr) × 100
```

---

## Expansion Propensity Score

Rank existing customers for upsell likelihood:

| Signal | Score Contribution |
|--------|------------------|
| Usage ≥ 80% of plan limit | +30 |
| Health score ≥ 70 | +20 |
| Active users grew ≥ 20% in 60d | +20 |
| Feature adoption breadth ≥ 60% | +15 |
| Last NPS ≥ 8 | +10 |
| Renewal in 60–90 days | +5 |
| Open support ticket | -15 |
| Usage declining | -20 |

Score range [0, 100]. Accounts scoring ≥ 60 are expansion candidates.
Route to `customer-success` for outreach.