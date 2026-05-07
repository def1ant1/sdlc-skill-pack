# Governance Reporting Template

## Governance Dashboard (Weekly)

```
GOVERNANCE DASHBOARD — Week of YYYY-MM-DD
==========================================

CONTROL HEALTH
  Implementation rate:     XX%  (target: ≥ 95%  | alert: < 85%)
  Evidence freshness:      XX%  (target: ≥ 90%  | alert: < 75%)
  Controls with open gaps: N

RISK REGISTER
  Total open risks:        N
  Critical (score ≥ 20):   N   ← alert if ≥ 1
  High (score 15–19):      N
  Past remediation date:   N   ← escalate each

POLICY ATTESTATION
  Policies current:        XX% (target: 100% | alert: < 100%)
  Due for attestation:     N
  Overdue:                 N   ← escalate each

AUDIT READINESS
  SOC 2 Type II:           XX% (target: ≥ 85%)
  ISO 27001:               XX%
  GDPR:                    XX%
  EU AI Act:               XX%

UPCOMING DATES
  Next audit:              YYYY-MM-DD (<N days)
  Next attestation due:    YYYY-MM-DD
  Next risk review due:    YYYY-MM-DD

ESCALATIONS THIS WEEK
  [list each, with owner and status]
```

---

## Monthly Governance Report

### Section 1 — Governance Posture Summary

| Metric | This Month | Last Month | Trend | Target |
|---|---|---|---|---|
| Control implementation rate | XX% | XX% | ↑/↓/→ | ≥ 95% |
| Evidence freshness | XX% | XX% | ↑/↓/→ | ≥ 90% |
| Open critical risks | N | N | ↑/↓/→ | 0 |
| Policy attestation rate | XX% | XX% | ↑/↓/→ | 100% |
| Audit readiness (highest priority) | XX% | XX% | ↑/↓/→ | ≥ 85% |

### Section 2 — Risk Register Delta

```
New risks this month:     N
Risks mitigated/closed:   N
Risks accepted:           N
Risks past SLA:           N

New Critical Risks:
  [list with RISK-ID, title, owner]

Overdue Remediations:
  [list with RISK-ID, title, original due date, owner]
```

### Section 3 — Control Gap Summary

```
Frameworks with gaps: [list]
New gaps identified:  N
Gaps remediated:      N
Outstanding gaps by severity:
  Critical: N
  High:     N
  Medium:   N
```

### Section 4 — Policy Attestation Status

| Policy | Owner | Last Attested | Next Due | Status |
|---|---|---|---|---|
| Data Governance Policy | Data team | YYYY-MM-DD | YYYY-MM-DD | Current |
| AI Safety Policy | AI team | YYYY-MM-DD | YYYY-MM-DD | Due in 15 days |

### Section 5 — Upcoming Audit Preparation

For any audit within 90 days:

```
Audit:            [framework name]
Date:             YYYY-MM-DD (N days away)
Current readiness: XX%
Target readiness:  ≥ 95%
Gap to target:     XX%

Open items blocking readiness:
  1. [item] — owner — due
  2. [item] — owner — due
```

---

## Governance KPI Definitions

| KPI | Definition | Formula |
|---|---|---|
| Control implementation rate | % of total controls with implemented status | `implemented / total × 100` |
| Evidence freshness | % of implemented controls with evidence updated in last 90 days | `fresh_evidence / implemented × 100` |
| Audit readiness score | Combined implementation and freshness score | `(implemented/total) × (fresh/implemented) × 100` |
| Risk register age | Days since last full risk register review | `days since review_date` |
| Policy attestation current | % of policies with attestation within review period | `attested_current / total_policies × 100` |