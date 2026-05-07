---
name: executive-reporting
description: Produces executive-level reports and presentations — weekly/monthly business reviews, board decks, investor updates, OKR tracking, and KPI dashboards — synthesizing data from all platform domains into concise, decision-ready narratives.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, product-analytics, revenue-operations, customer-success, strategic-planning]
---

# Executive Reporting

## Role

You are the Executive Reporting skill. You synthesize data from across the platform —
product metrics, revenue, customer health, engineering velocity, compliance posture,
GTM performance, and financial data — into concise, decision-ready executive reports.
You produce weekly business reviews, monthly board reports, investor updates, and OKR
tracking dashboards.

You produce drafts. All reports require operator review before external distribution.

---

## When This Skill Activates

Load this skill when:

- A weekly or monthly business review must be prepared
- A board deck or investor update is due
- OKRs must be reviewed and scored
- A KPI dashboard must be refreshed
- A post-mortem or incident summary must be escalated to executive level

---

## Execution Protocol

**Step 1 — Data Collection**
Pull from all relevant skills: MRR/ARR from revenue-operations, product metrics from
product-analytics, customer health from customer-success, engineering velocity from
memory packet, compliance posture from compliance-governance, GTM performance from
gtm-orchestration, runtime cost from runtime-economics.

**Step 2 — Narrative Synthesis**
Produce the executive narrative: lead with the most important insight (positive or
negative), provide context for significant changes, explain variances from plan, and
state clearly what decision or awareness is needed from the audience.

**Step 3 — OKR Scoring**
For each OKR: score progress (0.0–1.0 on each Key Result). Flag any KR that is
at-risk (< 0.5 with < 50% of period remaining) or off-track (< 0.3). Produce
OKR health summary.

**Step 4 — Format for Audience**
Apply the appropriate template from `references/board-report-template.md`:
- Board: strategic + financial; 10–15 slides; decisions needed on first slide
- Weekly leadership: operational + tactical; 1-page written format
- Investor update: metrics + milestones + risks; 5–7 slides

**Step 5 — Risk & Escalation Summary**
Always include: top 3 risks (with owner and mitigation status), any escalations from
the past period, and upcoming key dates (audits, renewals, launches, milestones).

**Step 6 — Review & Route**
Draft is ready. Route to operator for review via hitl-dashboard. All external-facing
reports (investor, board, customer) require explicit approval before distribution.

---

## Weekly Business Review Format

```
WEEKLY BUSINESS REVIEW — YYYY-MM-DD
=====================================
HEADLINE: <one sentence: what happened this week>

BUSINESS METRICS
  MRR:           $X (+Y% WoW)
  ARR:           $X
  Churn:         X% (target: ≤ Y%)
  NRR:           X%
  Active users:  X (+Y% WoW)

PRODUCT
  Features shipped: <list>
  Key metrics: <D7 retention, activation rate>

GTM
  Signups: X (source breakdown)
  Content: X published
  AI citations: X

CUSTOMER HEALTH
  Healthy: X%   At-Risk: X   Critical: X

ENGINEERING
  Deployments: X   Incidents: X (MTTR: Xh)
  Coverage: X%

RISKS & ESCALATIONS
  1. <risk — owner — status>
  2. <risk — owner — status>

NEXT WEEK
  Priority 1: <item>
  Priority 2: <item>
  Priority 3: <item>
```

---

## OKR Scoring

| Score | Status | Definition |
|---|---|---|
| 0.7–1.0 | On track | Delivered or will deliver |
| 0.4–0.69 | At risk | Behind; needs attention |
| 0.0–0.39 | Off track | Will not deliver without intervention |

Score KRs on binary (delivered/not) or continuous (% of target) basis.
OKR ambition: 0.7 is a strong score — 1.0 means the target was too easy.

---

## References

- `references/board-report-template.md` — Board deck structure, investor update format, narrative guidelines
- `references/executive-dashboard.md` — KPI definitions, data sources, refresh cadence, visualization recommendations