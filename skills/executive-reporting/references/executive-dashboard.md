# Executive Dashboard

## Dashboard Overview

The executive dashboard is a single-page view of the company's health across all
domains. Refreshed weekly (automated) with daily spot-checks for key revenue metrics.
Audience: CEO, CFO, VP Engineering, VP Product, Board (read-only access).

---

## KPI Definitions

### Revenue Metrics

| KPI | Definition | Data Source | Refresh |
|---|---|---|---|
| MRR | Monthly Recurring Revenue: sum of all active subscription charges in a given month | revenue-operations | Daily |
| ARR | Annual Recurring Revenue: MRR × 12 | revenue-operations | Daily |
| Net New ARR | New ARR + Expansion ARR − Churned ARR for the period | revenue-operations | Weekly |
| NRR | Net Revenue Retention: (Beginning ARR + Expansion − Contraction − Churn) / Beginning ARR | revenue-operations | Monthly |
| Gross Revenue Churn | ARR lost to cancellations / Beginning ARR | revenue-operations | Monthly |
| LTV | Customer Lifetime Value: Avg MRR per customer / Gross Churn Rate | revenue-operations | Monthly |
| CAC | Customer Acquisition Cost: Total S&M spend / New customers acquired | revenue-operations | Monthly |
| Payback Period | CAC / (Avg MRR × Gross Margin) in months | revenue-operations | Monthly |

---

### Product Metrics

| KPI | Definition | Data Source | Refresh |
|---|---|---|---|
| DAU/MAU | Daily Active Users / Monthly Active Users | product-analytics | Daily |
| Activation Rate | % of new signups reaching the "first value moment" within 7 days | product-analytics | Weekly |
| D7 Retention | % of day-0 users still active on day 7 | product-analytics | Weekly |
| D30 Retention | % of day-0 users still active on day 30 | product-analytics | Weekly |
| Feature Adoption | % of active accounts using each feature in last 30 days | product-analytics | Weekly |
| NPS | Net Promoter Score: % Promoters − % Detractors | customer-success | Monthly (survey) |

---

### Engineering Metrics

| KPI | Definition | Data Source | Refresh |
|---|---|---|---|
| Deployment Frequency | Deploys to production per week | release-management | Weekly |
| MTTR | Mean Time to Recover: avg P0/P1 incident duration | sre-incident-response | Weekly |
| Change Failure Rate | % of deployments causing a P0/P1 incident | sre-incident-response | Weekly |
| Test Coverage | % line coverage across domain packages | qa-automation | Per deploy |
| Error Budget Remaining | % of monthly error budget not yet consumed | observability | Daily |

---

### Customer Health Metrics

| KPI | Definition | Data Source | Refresh |
|---|---|---|---|
| Healthy Accounts | % of accounts with health score ≥ 70 | customer-success | Daily |
| At-Risk Accounts | Count of accounts with health score 40–69 | customer-success | Daily |
| Critical Accounts | Count of accounts with health score < 40 | customer-success | Daily |
| CSAT | Customer Satisfaction Score: avg of satisfaction survey responses | customer-success | Monthly |

---

### GTM Metrics

| KPI | Definition | Data Source | Refresh |
|---|---|---|---|
| New Signups | Accounts created in period | product-analytics | Daily |
| Trial-to-Paid Conversion | % of trials converting to paid within 14 days | revenue-operations | Weekly |
| Pipeline Value | Total open opportunity value | revenue-operations | Weekly |
| AI Citations | Mentions in AI chatbot responses (brand visibility) | gtm-orchestration | Weekly |

---

### Financial Operations

| KPI | Definition | Data Source | Refresh |
|---|---|---|---|
| Gross Margin | (Revenue − COGS) / Revenue | accounting-automation | Monthly |
| Burn Rate | Monthly cash outflow | accounting-automation | Monthly |
| Runway | Cash balance / Monthly burn rate | accounting-automation | Monthly |
| AI Compute Cost | Spend on LLM API calls + GPU infrastructure per month | runtime-economics | Monthly |

---

## Dashboard Layout

```
ROW 1 — REVENUE (always first)
  [MRR] [ARR] [Net New ARR] [NRR] [Burn Rate] [Runway]

ROW 2 — GROWTH
  [Signups] [Trial→Paid Conv.] [CAC] [Payback Period]

ROW 3 — PRODUCT
  [DAU/MAU] [Activation Rate] [D30 Retention] [NPS]

ROW 4 — CUSTOMER HEALTH
  [Healthy %] [At-Risk Count] [Critical Count] [CSAT]

ROW 5 — ENGINEERING
  [Deploy Freq.] [MTTR] [Change Failure Rate] [Error Budget]

ROW 6 — ALERTS
  [Any metric outside target range highlighted in amber/red]
```

---

## Alert Thresholds

| KPI | Amber (Investigate) | Red (Escalate) |
|---|---|---|
| Gross Revenue Churn | > 2% MoM | > 5% MoM |
| NRR | < 100% | < 90% |
| D30 Retention | < 30% | < 20% |
| Critical Accounts | ≥ 1 | ≥ 3 |
| MTTR | > 2h | > 4h |
| Error Budget Remaining | < 50% | < 20% |
| Runway | < 12 months | < 6 months |