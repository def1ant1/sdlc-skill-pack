# Compliance Packs

Used by `skills/compliance-automation/SKILL.md` to provide per-framework control
catalogs, requirement summaries, and evidence checklists.

---

## SOC2 Type II

**Trust Service Criteria (TSC)**

| Category | Criteria | Key Controls |
|---|---|---|
| Common Criteria (CC) | CC1–CC9 | Risk assessment, communication, change management, access, incident response |
| Availability (A) | A1 | Uptime monitoring, capacity planning, disaster recovery |
| Confidentiality (C) | C1 | Data classification, encryption, disposal |
| Processing Integrity (PI) | PI1 | Input validation, error handling, output completeness |
| Privacy (P) | P1–P8 | Consent, data subject rights, retention, disposal |

**SOC2 Evidence Checklist (minimum):**
```
[ ] Organizational chart and roles/responsibilities
[ ] Security awareness training records (annual)
[ ] Access control matrix (user → resource → permission)
[ ] Logical access provisioning and de-provisioning logs
[ ] Encryption configuration (at-rest + in-transit)
[ ] Vulnerability scan results (last 30 days)
[ ] Penetration test report (last 12 months)
[ ] Incident log (period of audit)
[ ] Change management tickets (period of audit)
[ ] System uptime / availability monitoring data
[ ] Backup and recovery test results
[ ] Vendor risk assessments
[ ] Board/management risk assessment documentation
```

---

## GDPR

**Key Articles and Requirements**

| Article | Requirement | Implementation |
|---|---|---|
| Art.5 | Data minimization, purpose limitation | Data classification policy; retention schedules |
| Art.6 | Lawful basis for processing | Consent records; legitimate interest assessments |
| Art.13/14 | Privacy notices | Published privacy policy; updated on change |
| Art.17 | Right to erasure | Data deletion workflow; audit trail |
| Art.20 | Right to portability | Data export API; 30-day SLA |
| Art.25 | Privacy by design | DPIA process; technical measures documentation |
| Art.28 | Processor agreements | DPA template; vendor DPA register |
| Art.30 | Records of processing activities | ROPA document |
| Art.32 | Security of processing | Encryption, access control, audit logs |
| Art.33 | Breach notification (72h) | Incident response SLA; DPA notification template |
| Art.35 | DPIA for high-risk processing | DPIA register; AI system DPIA |

**GDPR Evidence Checklist:**
```
[ ] Privacy policy (published, versioned)
[ ] Record of Processing Activities (ROPA)
[ ] DPA register (all sub-processors)
[ ] Consent management records
[ ] Data subject request log (SLA: 30 days)
[ ] Data retention schedule
[ ] DPIA for any high-risk or AI processing
[ ] Breach notification log (72h SLA documented)
[ ] Data transfer mechanisms (SCCs for non-EU transfers)
```

---

## HIPAA

**Key Rules**

| Rule | Safeguard | Key Requirements |
|---|---|---|
| Security Rule | Administrative | Risk analysis, workforce training, access management |
| Security Rule | Physical | Facility access, workstation controls, device disposal |
| Security Rule | Technical | Access control, audit controls, encryption, integrity |
| Privacy Rule | — | PHI use limitation, patient rights, minimum necessary |
| Breach Notification Rule | — | 60-day notification; HHS annual report |

**HIPAA Evidence Checklist:**
```
[ ] Risk analysis document (annual)
[ ] Risk management plan
[ ] Business Associate Agreements (BAAs) for all vendors
[ ] Workforce training records
[ ] Access control policy and logs
[ ] Audit log configuration and samples
[ ] Encryption configuration (ePHI at rest and in transit)
[ ] Incident log and breach assessment records
[ ] Sanction policy
[ ] Contingency plan (backup, DR)
```

---

## ISO27001

**Annex A Control Domains (ISO27001:2022)**

| Clause | Domain | Controls |
|---|---|---|
| A.5 | Organizational controls | Policies, roles, threat intelligence, asset management |
| A.6 | People controls | Screening, terms, training, disciplinary |
| A.7 | Physical controls | Secure areas, equipment, clear desk |
| A.8 | Technological controls | Endpoint, access, cryptography, logging, vulnerability mgmt |

**ISO27001 Evidence Checklist:**
```
[ ] ISMS scope document
[ ] Information security policy (signed by management)
[ ] Risk assessment methodology
[ ] Risk register (current)
[ ] Statement of Applicability (SoA)
[ ] Asset inventory
[ ] Internal audit results
[ ] Management review minutes
[ ] Corrective action records
[ ] Business continuity plan and test results
```

---

## EU AI Act

**Risk Classification (applies to AI system components)**

| Risk Level | Category | Requirements |
|---|---|---|
| Unacceptable | Prohibited | Not permitted (e.g., social scoring, real-time biometric surveillance) |
| High | Annex III use cases | Full conformity assessment, registration, human oversight |
| Limited | Chatbots, deep fakes | Transparency obligation (disclose AI nature) |
| Minimal | Spam filters, games | No specific obligation |

**High-Risk AI Evidence Checklist:**
```
[ ] Risk classification assessment
[ ] Technical documentation (Art.11)
[ ] Conformity assessment record
[ ] EU database registration
[ ] Human oversight mechanism documentation
[ ] Accuracy and robustness testing results
[ ] Bias and fairness assessment
[ ] Data governance documentation
[ ] Post-market monitoring plan
[ ] Incident reporting procedure
```

---

## NIST AI RMF

**Core Functions**

| Function | Purpose | Key Practices |
|---|---|---|
| GOVERN | Establish AI risk culture | Policies, roles, risk tolerance, accountability |
| MAP | Identify and classify risks | Use case context, stakeholder impact, risk categorization |
| MEASURE | Analyze and assess risks | Testing, evaluation, bias measurement, monitoring |
| MANAGE | Prioritize and address risks | Incident response, remediation, communication |

---

## PCI DSS v4.0

**12 Requirements Summary**

| Req | Topic | Key Controls |
|---|---|---|
| 1 | Network security | Firewall rules, network segmentation |
| 2 | Secure configuration | No vendor defaults, hardening standards |
| 3 | Protect stored account data | Encryption, masking, tokenization |
| 4 | Protect data in transit | TLS 1.2+ only |
| 5 | Protect against malware | AV/EDR on all systems |
| 6 | Secure development | SSDLC, vulnerability management, WAF |
| 7 | Restrict access | Need-to-know access control |
| 8 | Identify and authenticate | MFA, password policy, shared accounts prohibited |
| 9 | Restrict physical access | Physical access logs, visitor management |
| 10 | Log and monitor | Centralized logging, 12-month retention |
| 11 | Test security | ASV scans (quarterly), penetration test (annual) |
| 12 | Security policy | Written policy, risk assessment, incident response |