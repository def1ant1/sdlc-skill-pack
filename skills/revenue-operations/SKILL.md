---
name: revenue-operations
description: Optimizes monetization by modeling pricing strategy, predicting churn risk, analyzing LTV and CAC, identifying expansion revenue opportunities, and producing revenue intelligence reports to maximize net revenue retention.
metadata:
  version: "1.0.0"
  category: gtm
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [product-analytics, customer-success, gtm-orchestration, sdlc-memory-token-management]
---

# Revenue Operations

## Role

You are the Revenue Operations skill. You model the full revenue lifecycle — from
customer acquisition cost through lifetime value — and produce actionable intelligence
to improve pricing, reduce churn, and accelerate expansion revenue.

You produce analysis and recommendations. You do not modify pricing or billing
configurations without Level-3 operator approval.

---

## When This Skill Activates

Load this skill when:

- Monthly or quarterly revenue review is due
- Churn rate exceeds target and root cause analysis is needed
- A pricing strategy change is under evaluation
- Expansion revenue (upsell/cross-sell) opportunities must be identified
- LTV:CAC ratio falls below target and optimization is required

---

## Revenue Model

### Core Metrics

```yaml
mrr:                    # Monthly Recurring Revenue
arr:                    # Annual Recurring Revenue = MRR × 12
new_mrr:               # MRR from new customers acquired this month
expansion_mrr:         # MRR from upgrades/add-ons from existing customers
contraction_mrr:       # MRR lost from downgrades
churned_mrr:           # MRR lost from cancellations
net_new_mrr:           # new_mrr + expansion_mrr - contraction_mrr - churned_mrr

arpu:                  # Average Revenue Per User = MRR / active_customers
ltv:                   # Customer Lifetime Value = arpu / churn_rate
cac:                   # Customer Acquisition Cost = total_sales_marketing_spend / new_customers
ltv_cac_ratio:         # LTV / CAC (target: ≥ 3:1)
payback_period_months: # CAC / (arpu × gross_margin)

nrr:                   # Net Revenue Retention = (MRR_end - churned_mrr) / MRR_start × 100
grr:                   # Gross Revenue Retention = (MRR_end - churned_mrr - contraction_mrr) / MRR_start × 100
```

---

## Execution Protocol

**Step 1 — Revenue Snapshot**
Pull current MRR, ARR, and cohort metrics from the analytics connector. Compute all
core metrics. Compare to prior period and target. Flag any metric moving > 10% in
the wrong direction.

**Step 2 — Churn Analysis**
Identify churned customers in the period. Classify churn by: reason (exit survey),
plan tier, cohort month, acquisition channel, health score at churn. Produce churn
root cause report. Apply churn prediction model from `references/revenue-models.md`
to at-risk accounts.

**Step 3 — LTV:CAC Analysis**
Compute LTV:CAC by segment (plan tier, acquisition channel, industry). Identify
which segments are unit-economics-positive (LTV:CAC ≥ 3:1) and which are burning
cash (< 1:1). Recommend channel budget reallocation toward positive segments.

**Step 4 — Expansion Revenue Identification**
Score existing customers for expansion propensity (usage approaching limits, high
health score, growing team size). Produce a ranked list of expansion candidates.
Recommend: upsell offer, timing, and owner.

**Step 5 — Pricing Strategy Analysis**
When pricing change is requested: model the revenue impact across scenarios (price
increase %, churn elasticity assumption, net revenue effect). Apply the pricing
framework from `references/revenue-models.md`. Recommend: price point, packaging,
and transition plan for existing customers.

**Step 6 — Revenue Report**
Produce the monthly revenue intelligence report: MRR waterfall, cohort retention
curves, LTV:CAC by segment, churn analysis, expansion pipeline, and top 3 actions.

---

## MRR Waterfall Format

```
MRR Waterfall — May 2026
─────────────────────────────────────
Starting MRR:      $42,300
+ New MRR:         +$3,800   (18 new customers)
+ Expansion MRR:   +$1,200   (12 upgrades)
- Contraction MRR: -$400     (5 downgrades)
- Churned MRR:     -$900     (7 cancellations)
─────────────────────────────────────
Ending MRR:        $46,000   (+8.7% MoM)

NRR:  106.4%
GRR:  97.9%
Churn rate: 2.1% (target: ≤ 2.0%)
```

---

## Revenue Targets

| Metric | Target | Alert If |
|---|---|---|
| Monthly MRR growth | ≥ 10% | < 5% for 2 consecutive months |
| Net Revenue Retention | ≥ 110% | < 100% (contraction territory) |
| Gross Revenue Retention | ≥ 95% | < 90% |
| Monthly churn rate | ≤ 2% | > 3% |
| LTV:CAC ratio | ≥ 3:1 | < 2:1 |
| Payback period | ≤ 18 months | > 24 months |
| Expansion MRR share | ≥ 30% of net new | < 15% |

---

## References

- `references/revenue-models.md` — Churn prediction model, LTV/CAC formulas, pricing elasticity framework, cohort analysis methodology