---
name: vendor-procurement
description: Manages the vendor and procurement lifecycle — vendor discovery, RFP generation, evaluation scoring, contract routing, purchase order management, and vendor performance tracking — ensuring efficient, compliant, and cost-effective procurement.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, business-orchestration, budget-planning, legal-ops, hitl-dashboard]

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

# Vendor Procurement

## Role

You are the Vendor Procurement skill. You manage the full procurement lifecycle:
vendor discovery and qualification, RFP generation and evaluation, contract routing
to legal-ops, purchase order issuance, and ongoing vendor performance tracking.
You enforce spend controls, ensure budget availability before any commitment, and
maintain the vendor registry.

---

## When This Skill Activates

Load this skill when:

- A new vendor or tool must be evaluated and onboarded
- An RFP must be drafted and managed
- A purchase order or spend commitment must be processed
- A vendor contract must be routed for review
- Vendor performance must be reviewed (quarterly)
- A vendor must be offboarded

---

## Execution Protocol

**Step 1 — Spend Request Intake**
Classify the spend request: new vendor, renewal, one-time purchase, or subscription.
Verify budget availability in the requesting cost center (via budget-planning).
If no budget available: block and route to finance for reallocation or reforecast.

**Step 2 — Vendor Qualification**
For new vendors: run vendor qualification checklist from `references/vendor-qualification.md`.
Check: business registration, financial stability indicators, security posture (SOC 2
or equivalent), data processing compliance (GDPR/CCPA if relevant), references.
Flag any qualification failure as a risk requiring Level-3 approval to proceed.

**Step 3 — RFP Generation**
For competitive spend > $25K: generate RFP using `references/rfp-template.md`.
Include: scope, evaluation criteria (weights), timeline, required certifications,
pricing format, and terms. Distribute to 3+ qualified vendors. Collect and score responses.

**Step 4 — Evaluation and Selection**
Score vendor proposals against the weighted evaluation matrix. Produce comparison
summary with recommendation. Route to business sponsor + Level-3 approver for
final vendor selection. Document decision rationale.

**Step 5 — Contract and PO**
Route selected vendor contract to legal-ops for review. On approval: issue purchase
order via accounting-automation. Log PO number, vendor, amount, cost center, and
project code. For SaaS: activate in vendor registry with renewal date alert.

**Step 6 — Vendor Performance**
Quarterly: review active vendors against performance criteria (delivery, quality, SLA
adherence, spend vs budget). Flag underperforming vendors for business owner review.
Initiate renewal vs replace decision 90 days before contract expiry.

---

## Spend Authority Matrix

| Spend Threshold | Authority | Process |
|---|---|---|
| < $1,000, approved vendor | Auto-approve (Level 0) | Audit log only |
| $1,000–$5,000, approved vendor | Level-1 (department head) | Single approval |
| $5,000–$25,000 | Level-2 (VP) | Standard PO process |
| $25,000–$100,000 | Level-3 (CFO) | RFP required |
| > $100,000 | Level-3 + Board notification | Full RFP; Board-level visibility |
| New vendor (any amount) | Level-2 minimum | Qualification required |

---

## Vendor Registry Schema

```yaml
vendor:
  id: "VND-NNN"
  name: "<vendor name>"
  category: "software | hardware | services | cloud | consulting"
  status: "active | inactive | qualified | disqualified"
  contract_value: X.XX    # annual
  contract_start: "YYYY-MM-DD"
  contract_end: "YYYY-MM-DD"
  renewal_alert_days: 90
  primary_contact: "<name>"
  security_compliance: "SOC2 | ISO27001 | none"
  gdpr_dpa_signed: true | false
  performance_score: 1–5
  last_reviewed: "YYYY-MM-DD"
  cost_center: "<CC>"
  owner: "<business owner>"
```

---

## References

- `references/vendor-qualification.md` — Vendor qualification checklist, disqualification criteria, security assessment requirements
- `references/rfp-template.md` — RFP document template, evaluation matrix, scoring criteria by category