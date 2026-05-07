# Business Workflow Taxonomy

## Overview

This taxonomy defines all business task types recognized by business-orchestration,
the domain skill responsible for each, and the routing rules applied.

---

## Finance Domain

| Task Type | Trigger Keywords | Primary Skill | Urgency | Approval |
|---|---|---|---|---|
| Invoice processing | invoice, bill, payable | accounting-automation | Routine | Auto < $1K; L2 > $1K |
| Expense reimbursement | expense, receipt, reimbursement | accounting-automation | Routine | Auto; L2 > policy limit |
| Account reconciliation | reconcile, bank statement, close | accounting-automation | Routine | L2 sign-off to close |
| Period close | month-end, quarter-end, close | accounting-automation | Urgent | L3 (CFO) |
| Budget planning | budget, annual plan, forecast | budget-planning | Routine | L3 (CFO) |
| Budget variance review | variance, over budget, underspend | budget-planning | Urgent | L2 |
| Revenue reporting | MRR, ARR, revenue, bookings | revenue-operations | Routine | L2 |

---

## Legal Domain

| Task Type | Trigger Keywords | Primary Skill | Urgency | Approval |
|---|---|---|---|---|
| NDA generation | NDA, non-disclosure, confidentiality | legal-ops | Routine | L2 + legal review |
| Contract review | contract, agreement, terms | legal-ops | Urgent | L2 + legal review |
| Policy update | policy, procedure, update | legal-ops | Routine | L3 |
| Regulatory assessment | regulation, compliance, GDPR, EU AI | legal-ops | Urgent | L2 |
| IP documentation | patent, trademark, IP, copyright | legal-ops | Routine | L2 + legal review |

---

## HR / Workforce Domain

| Task Type | Trigger Keywords | Primary Skill | Urgency | Approval |
|---|---|---|---|---|
| Job requisition | hire, JD, job description, role | workforce-management | Routine | L3 |
| Onboarding | onboard, new hire, start | workforce-management | Urgent | L2 |
| Performance review | review, performance, goals, OKR | workforce-management | Routine | L2 |
| Compensation change | salary, raise, equity, compensation | workforce-management | Routine | L3 + CFO |
| Offboarding | offboard, departure, last day, terminate | workforce-management | Critical | L3 |
| Org change | reorg, reporting, structure | workforce-management | Routine | L3 |

---

## Procurement Domain

| Task Type | Trigger Keywords | Primary Skill | Urgency | Approval |
|---|---|---|---|---|
| Vendor onboarding | new vendor, supplier, qualify | vendor-procurement | Routine | L2 |
| RFP | RFP, proposal, competitive bid | vendor-procurement | Routine | L3 > $25K |
| Purchase order | PO, purchase, order, buy | vendor-procurement | Routine | L2 |
| Contract renewal | renew, renewal, expiring | vendor-procurement | Urgent | L2 |
| Vendor evaluation | vendor review, performance, score | vendor-procurement | Routine | L1 |

---

## Meetings Domain

| Task Type | Trigger Keywords | Primary Skill | Urgency | Approval |
|---|---|---|---|---|
| Meeting transcription | transcript, recording, notes | meeting-intelligence | Routine | None |
| Action item extraction | action items, tasks, follow-up | meeting-intelligence | Routine | None |
| Summary generation | summary, minutes, recap | meeting-intelligence | Routine | L1 before distribution |
| Decision capture | decision, agreed, confirmed | meeting-intelligence | Routine | None |
| Follow-up tracking | overdue, deadline, check-in | meeting-intelligence | Urgent | None |

---

## Customer Domain

| Task Type | Trigger Keywords | Primary Skill | Urgency | Approval |
|---|---|---|---|---|
| Health scoring | health, at-risk, customer score | customer-success | Routine | None |
| Escalation | escalate, critical account, churn | customer-success | Critical | L2 |
| Onboarding | customer onboard, setup, activate | customer-success | Urgent | None |
| Renewal | renewal, contract end, upsell | customer-success | Urgent | L2 |
| NPS / CSAT | survey, NPS, satisfaction | customer-success | Routine | None |

---

## Cross-Domain Workflow Patterns

| Pattern | Domains Involved | Trigger | Workflow Template |
|---|---|---|---|
| New vendor procurement | Procurement → Legal → Finance | New vendor request | `vendor-onboard` |
| New hire | HR → Legal → IT → Finance | Hire approval | `new-hire` |
| Customer contract | Legal → Finance → Customer | New enterprise deal | `enterprise-deal` |
| Budget cycle | Finance → Strategy → HR → All depts | Annual planning | `annual-budget` |
| Incident escalation | SRE → Finance → Legal → Exec | P0 with financial impact | `p0-incident` |

---

## Routing Priority Rules

1. **Safety first**: Any task touching financial transactions > $50K or legal risk is routed to human approval before any autonomous action
2. **Urgency escalation**: Keywords indicating urgency override default approval thresholds
3. **Cross-domain detection**: Tasks touching > 1 domain are routed to workflow-engine for composition
4. **Ambiguity**: Tasks matching no rule → route to business-orchestration for human classification
5. **Unknown vendors**: Any financial task involving an unregistered vendor requires vendor qualification first