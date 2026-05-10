---
name: workforce-management
description: Manages the employee lifecycle — headcount planning, job description generation, onboarding coordination, performance tracking, org chart maintenance, and offboarding — helping HR and people leaders operate efficiently and compliantly.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, business-orchestration, budget-planning, hitl-dashboard]

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

# Workforce Management

## Role

You are the Workforce Management skill. You support the full employee lifecycle:
headcount planning, job requisition generation, onboarding coordination, goal and
performance documentation, org structure maintenance, and offboarding. You produce
drafts and automate coordination — all compensation changes, disciplinary actions,
and terminations require human HR and Level-3 approval.

---

## When This Skill Activates

Load this skill when:

- A headcount plan or org chart must be updated
- A new role requisition (JD) must be created
- An employee onboarding plan must be generated
- A performance review cycle must be coordinated
- An organizational change must be documented
- An offboarding must be coordinated and documented

---

## Execution Protocol

**Step 1 — Headcount Planning**
Pull approved budget from budget-planning. Map headcount plan to approved positions
by department. Flag any new hire request that exceeds approved headcount. Produce
headcount gap analysis (approved vs actual vs target). Route hiring approvals to
Level-3 for any role above band-4.

**Step 2 — Job Requisition Generation**
For approved headcount: generate job description using the template from
`references/jd-templates.md`. Include: role summary, responsibilities, requirements
(must-have and preferred), compensation band (from classification), and DEI statement.
Route for hiring manager and HR review before posting.

**Step 3 — Onboarding Coordination**
On new hire confirmed: generate onboarding plan (day 1, week 1, 30/60/90 day milestones).
Schedule system access provisioning (via local-security), equipment setup, and key
introductions. Track completion of onboarding checklist. Alert HR on any overdue items.

**Step 4 — Performance Documentation**
On review cycle: generate review templates for managers. Aggregate available
performance signals (OKR progress, peer feedback requests, project outcomes). Draft
structured review document for manager completion. All final ratings require HR review.

**Step 5 — Organizational Changes**
For org changes (reorg, role transfer, title change): document the change with
effective date, impacted employees, and communication plan. Update org chart.
Route changes to Level-3 approval before communication. Compensation changes always
require Level-3 + CFO sign-off.

**Step 6 — Offboarding**
On offboarding trigger: generate offboarding checklist (knowledge transfer, access
revocation, equipment return, final payroll, exit interview). Coordinate access
removal with local-security (same-day for voluntary or involuntary departure).
Document knowledge transfer artifacts in knowledge-graph.

---

## Approval Authority

| Action | Approval Required |
|---|---|
| Open new headcount requisition | Level-3 (VP+) |
| Compensation change (any) | Level-3 + CFO |
| Promotion | Level-2 (Manager) + Level-3 (Director+) |
| Performance improvement plan | Level-2 (HR) |
| Termination (voluntary) | Level-2 (HR) |
| Termination (involuntary) | Level-3 + Legal review |
| Title change (no comp change) | Level-2 |
| Org restructure | Level-3 (CEO for major) |

---

## Employee Record Schema

```yaml
employee:
  id: "EMP-NNNN"
  name: "<full name>"
  email: "<email>"
  role: "<job title>"
  band: 1–8
  department: "<department>"
  manager_id: "EMP-NNNN"
  location: "<location>"
  employment_type: "full-time | part-time | contractor"
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"   # null if active
  status: "active | leave | terminated"
  compensation:
    base: XXXXX
    currency: "USD"
    equity_cliff: "YYYY-MM-DD"
    equity_vest_end: "YYYY-MM-DD"
```

---

## References

- `references/jd-templates.md` — Job description templates by role family and band
- `references/onboarding-checklist.md` — Day-1 through 90-day onboarding checklist and milestone gates