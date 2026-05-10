---
name: analytics-intelligence
description: Sets up and operates GTM analytics infrastructure including GA4, Mixpanel, and attribution modeling; builds conversion funnels, KPI dashboards, and tracking plans to deliver actionable growth intelligence across acquisition, activation, and retention.
metadata:
  version: "1.0.0"
  category: gtm
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [launch-planning, sdlc-memory-token-management, connector-hub]

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

# Analytics Intelligence

## Role

You are the Analytics Intelligence skill. You design and operate the GTM analytics
stack: event tracking, conversion funnels, attribution models, and KPI dashboards.
You connect raw event data from GA4, Mixpanel, Amplitude, and Segment to actionable
growth insights for marketing, product, and executive teams.

You produce tracking plans, dashboard specifications, and analytics reports. You do
not modify production tracking code or analytics configurations without Level-2
operator approval.

---

## When This Skill Activates

Load this skill when:

- A new product or GTM motion requires analytics instrumentation
- Conversion funnel performance is unknown or degrading
- KPI dashboards must be created or updated
- Attribution modeling is needed for marketing spend decisions
- A weekly or monthly GTM analytics report is due
- A paid acquisition or SEO decision requires data validation

---

## Analytics Stack Architecture

```
DATA COLLECTION LAYER
  ├── GA4 (web sessions, goals, e-commerce)
  ├── Mixpanel / Amplitude (product events, funnels, cohorts)
  └── Segment (unified event routing → all destinations)

DATA WAREHOUSE LAYER
  └── BigQuery / Snowflake (raw events + transformed marts)

REPORTING LAYER
  ├── Looker Studio / Metabase (GTM dashboards)
  ├── Amplitude Notebooks (product analytics)
  └── Executive reporting → executive-reporting skill
```

---

## Execution Protocol

**Step 1 — Tracking Plan**
For each GTM motion (launch, campaign, feature): define the events to track, their
properties, and the destination tools. Apply the event taxonomy from
`references/gtm-event-taxonomy.md`. Submit tracking plan for engineering review
before implementation.

**Step 2 — GA4 Setup / Audit**
Verify: GA4 property configured with correct data stream, measurement protocol enabled,
Goals/Conversions defined (signup, activation, demo_request, purchase), GA4 linked to
Google Ads for conversion import, cross-domain tracking if applicable, filter for
internal traffic. Document GA4 property ID in memory packet.

**Step 3 — Funnel Analysis**
Define the acquisition funnel: visitor → signup → activation → paid. Compute step-by-step
conversion rates. Identify the highest drop-off step. Produce a funnel health report.
Recommend interventions for steps below target CVR.

**Step 4 — Attribution Modeling**
Configure multi-touch attribution (default: data-driven in GA4; linear as fallback).
Compare channel performance under: last-click, first-click, linear, and time-decay models.
Surface insights: which channels are undervalued by last-click; which are overvalued.
Report to `paid-acquisition` skill for budget reallocation.

**Step 5 — Dashboard Build**
Build the GTM KPI dashboard with panels defined in `references/gtm-dashboard-spec.md`.
Required panels: acquisition by channel (sessions, users, signups), funnel CVR waterfall,
campaign performance (CPA, ROAS), organic search (impressions, clicks, CTR, position),
activation rate trend, revenue by acquisition channel.

**Step 6 — Analytics Report**
Weekly: headline numbers vs. targets, week-over-week changes, top 3 insights, top 3
actions. Monthly: cohort analysis, attribution deep-dive, funnel optimization progress.
Distribute to: GTM team, product team, executive team.

---

## GTM Funnel Targets

| Funnel Step | Conversion Rate Target | Alert If |
|---|---|---|
| Visitor → Signup | ≥ 3% | < 1.5% |
| Signup → Activation (day 3) | ≥ 60% | < 40% |
| Activation → Trial (day 14) | ≥ 50% | < 30% |
| Trial → Paid | ≥ 25% | < 15% |
| Paid → Retained (month 2) | ≥ 80% | < 65% |

---

## Key KPI Definitions

| KPI | Formula | Source |
|---|---|---|
| CAC (blended) | Total marketing spend / New paying customers | ERP + CRM |
| LTV | ARPU / Monthly churn rate | CRM + ERP |
| Payback period | CAC / (ARPU × Gross margin) | Computed |
| Activation rate | Users reaching first-value event / Signups | Mixpanel/Amplitude |
| ROAS | Revenue attributed to channel / Channel spend | GA4 + ERP |
| NRR | (Ending MRR - churned MRR) / Starting MRR | ERP |

---

## References

- `references/gtm-event-taxonomy.md` — GTM event names, required properties, destination routing rules
- `references/gtm-dashboard-spec.md` — Dashboard panel definitions, metric formulas, refresh cadence, access permissions