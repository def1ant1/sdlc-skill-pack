# Revenue Models

Used by `skills/revenue-operations/SKILL.md` to provide churn prediction, LTV/CAC
formulas, pricing elasticity framework, and cohort analysis methodology.

---

## Churn Prediction Model

### Input Signals (scored 0–1 each)

| Signal | Weight | Low Churn | High Churn |
|---|---|---|---|
| Health score | 0.30 | ≥ 70 | < 30 |
| Login frequency (last 30d) | 0.20 | ≥ 15 logins | ≤ 2 logins |
| Feature adoption rate | 0.15 | ≥ 60% | ≤ 20% |
| Support ticket volume (P1+P2) | 0.15 | 0–1 tickets | ≥ 5 tickets |
| NPS score | 0.10 | ≥ 8 | ≤ 5 |
| Days since last active | 0.10 | ≤ 3 days | ≥ 14 days |

### Churn Risk Score

```
churn_risk = (
  (1 - health_norm)   × 0.30 +
  (1 - login_norm)    × 0.20 +
  (1 - adoption_norm) × 0.15 +
  ticket_vol_norm     × 0.15 +
  (1 - nps_norm)      × 0.10 +
  inactivity_norm     × 0.10
)
```

Normalize each input to 0–1. Churn risk range: 0.0 (no risk) – 1.0 (certain churn).

### Churn Risk Tiers

| Risk Score | Tier | Action |
|---|---|---|
| 0.0–0.25 | Low | No action; track normally |
| 0.25–0.50 | Medium | Proactive enablement; send feature tips |
| 0.50–0.75 | High | CS manager outreach; offer success call |
| 0.75–1.00 | Critical | Executive intervention; save offer |

**Save offer eligibility**: Customers in Critical tier with > 6 months tenure and
MRR > $200/month may receive a save offer (discount, feature unlock, or concierge
support). Requires operator approval.

---

## LTV Formulas

### Basic LTV

```
ltv = arpu / monthly_churn_rate
```

Where `monthly_churn_rate = churned_customers_this_month / total_customers_start`.

### LTV with Expansion Revenue

```
ltv_expanded = (arpu + expansion_arpu) / (churn_rate - expansion_rate)
```

Only valid when `churn_rate > expansion_rate` (i.e., expansion doesn't exceed churn).

### LTV by Cohort

Compute LTV separately for each acquisition cohort (month of signup):

```
cohort_ltv = sum(monthly_arpu_per_customer) over customer_lifetime
           = arpu × average_months_retained
```

Track cohort LTV curves to identify: best-performing cohorts (highest retention),
acquisition channel quality, onboarding track effectiveness.

---

## CAC Formula

```
cac = (sales_expense + marketing_expense) / new_customers_acquired
```

Compute CAC separately by:
- **Blended CAC**: All channels combined
- **Paid CAC**: Only paid acquisition spend
- **Organic CAC**: Infrastructure cost only (content, team time)

### CAC by Channel

| Channel | Typical CAC Range | Notes |
|---|---|---|
| Organic search / SEO | $50–$200 | Low CAC; long lead time |
| Content marketing | $100–$300 | Delayed ROI; compound growth |
| Product Hunt / viral | $10–$100 | Unpredictable volume |
| Paid search | $200–$800 | Fast, controllable, expensive |
| Outbound sales | $1,000–$5,000 | Enterprise; high ACV |
| Referral | $50–$150 | High-quality leads |

---

## Pricing Elasticity Framework

When evaluating a price change:

### Step 1 — Estimate Price Sensitivity

Use the Van Westendorp Price Sensitivity Meter (PSM):
- Too cheap (raises quality concerns): ?
- Cheap (good value): ?
- Expensive (would consider): ?
- Too expensive (would not buy): ?

If PSM data unavailable: use churn rate response to past price changes or industry
benchmarks (SaaS elasticity typically −0.5 to −1.5).

### Step 2 — Model Revenue Impact

```
scenario = {
  current_customers: N,
  current_arpu: $X,
  price_increase_pct: +Y%,
  assumed_churn_elasticity: E,  # e.g. −0.5 means 5% price increase → 2.5% churn
}

expected_churn_from_increase = N × (price_increase_pct × abs(churn_elasticity))
retained_customers = N - expected_churn_from_increase
new_arpu = X × (1 + price_increase_pct)
new_mrr = retained_customers × new_arpu
mrr_delta = new_mrr - (N × X)
```

### Step 3 — Transition Plan

For existing customers:
- Grandfather existing customers for 3–6 months (standard)
- Notify 60 days in advance (required)
- Offer annual plan lock-in before increase (capture expansion MRR)
- Segment high-churn-risk customers for save outreach before announcement

---

## Cohort Retention Analysis

**Monthly cohort table format:**

```
Cohort | M0  | M1  | M2  | M3  | M6  | M12
-------|-----|-----|-----|-----|-----|-----
Jan-25 | 100%| 85% | 78% | 72% | 60% | 48%
Feb-25 | 100%| 87% | 81% | 76% | 65% | —
Mar-25 | 100%| 89% | 83% | 79% | —   | —
```

**Retention benchmarks (SaaS):**

| Cohort Month | Good | Excellent |
|---|---|---|
| M1 (Day 30) | ≥ 80% | ≥ 90% |
| M3 (Day 90) | ≥ 65% | ≥ 80% |
| M6 (Day 180) | ≥ 55% | ≥ 70% |
| M12 (Day 365) | ≥ 45% | ≥ 60% |

**Analysis trigger**: If any cohort's M3 retention drops > 10 percentage points below
the prior cohort: flag for investigation. Root causes: product regression, ICP mismatch,
onboarding failure, competitive displacement.