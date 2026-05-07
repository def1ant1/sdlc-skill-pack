# Vendor Qualification Checklist

## Qualification Process

All new vendors receiving payments > $1,000 OR handling company data must be qualified.
Qualification is a one-time process; vendors are re-qualified every 2 years or after
a significant incident.

---

## Section 1 — Business Verification

- [ ] Vendor is a registered legal entity (verify via business registry)
- [ ] Vendor has been operating for ≥ 12 months (or has credible references)
- [ ] Vendor has a valid business address and primary contact
- [ ] No unresolved litigation or regulatory actions disclosed
- [ ] Sanctions screening passed (OFAC, EU sanctions lists)

**Disqualification**: Active sanctions hit, unresolved material litigation.

---

## Section 2 — Financial Stability

- [ ] For vendors > $50K annual spend: financial stability check completed
  - Option A: Recent credit report or D&B score (D&B > 50 acceptable)
  - Option B: References from 3 similar-sized customers
  - Option C: Waiver approved by CFO if vendor is early-stage and strategic

---

## Section 3 — Security & Compliance

- [ ] Vendor security posture assessed based on data access level:

| Data Access | Requirement |
|---|---|
| No company data | Self-attested security questionnaire |
| Internal data (non-customer, non-PII) | SOC 2 Type I or equivalent |
| Customer data or PII | SOC 2 Type II or ISO 27001 (current) |
| Payment data | PCI-DSS certification |
| PHI/health data | HIPAA BAA required |

- [ ] Security questionnaire completed and reviewed (if no SOC 2)
- [ ] Penetration test results reviewed (for customer data vendors)
- [ ] Data breach history disclosed and assessed
- [ ] Incident response process documented

**Disqualification**: No security controls for data-accessing vendors; recent material breach without evidence of remediation.

---

## Section 4 — Data Governance

- [ ] Vendor's data processing practices documented
- [ ] For vendors processing PII: Data Processing Agreement (DPA) executed
- [ ] GDPR compliance confirmed (for EU data processors)
- [ ] Sub-processor list reviewed and accepted
- [ ] Data retention and deletion policies documented
- [ ] Data residency requirements confirmed (if applicable)

**Disqualification**: Refuses to sign DPA for PII processing; non-GDPR-compliant sub-processors.

---

## Section 5 — Operational Reliability

- [ ] Uptime SLA documented (if applicable)
- [ ] Vendor disaster recovery / BCP documented
- [ ] Support model and response times confirmed
- [ ] References checked (minimum 2 for spend > $25K)

---

## Qualification Outcome

| Score | All critical items passed | Action |
|---|---|---|
| Fully Qualified | Yes | Add to vendor registry; proceed to contract |
| Conditionally Qualified | Minor gaps with remediation plan | Proceed with compensating controls; re-qualify in 6 months |
| Disqualified | Any critical failure | Cannot proceed; document reason; escalate if business-critical |

---

## Re-Qualification Triggers

- 2-year renewal (standard cadence)
- Vendor discloses a security breach
- Significant change in vendor's data access scope
- Vendor acquired by another company
- Material complaints or incidents during vendor relationship

---

## Qualification Record

```yaml
vendor_qualification:
  vendor_id: "VND-NNN"
  qualification_date: "YYYY-MM-DD"
  qualified_by: "<name>"
  outcome: "qualified | conditional | disqualified"
  data_access_level: "none | internal | customer-pii | payment"
  security_certification: "SOC2-T2 | SOC2-T1 | ISO27001 | questionnaire | none"
  dpa_required: true | false
  dpa_executed: true | false
  disqualification_reason: "<if disqualified>"
  next_review: "YYYY-MM-DD"
  notes: "<any conditions or special requirements>"
```