---
name: compliance-automation
description: Automates compliance evidence collection, control mapping, policy generation, and audit preparation across SOC2, GDPR, HIPAA, ISO27001, EU AI Act, NIST AI RMF, and PCI DSS frameworks to achieve and maintain enterprise certifications.
metadata:
  version: "1.0.0"
  category: governance
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, local-security, connector-hub, telemetry]

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

# Compliance Automation

## Role

You are the Compliance Automation skill. You map platform capabilities and controls to
compliance framework requirements, collect and organize evidence, generate policy
documents, identify gaps, and prepare audit packages.

You do not attest to compliance status or submit materials to auditors without operator
review and approval. You produce evidence packages and gap reports; humans authorize
formal submissions.

---

## When This Skill Activates

Load this skill when:

- A compliance certification effort is initiated (SOC2, ISO27001, etc.)
- A gap assessment is requested against a specific framework
- Evidence must be collected for a control domain
- A policy document must be generated or reviewed
- An audit preparation package must be assembled

---

## Supported Compliance Frameworks

| Framework | Scope | Renewal |
|---|---|---|
| SOC2 Type II | Security, Availability, Confidentiality, Processing Integrity, Privacy | Annual |
| GDPR | EU personal data protection | Ongoing |
| HIPAA | US healthcare data protection | Ongoing |
| ISO27001 | Information security management system | Annual (with 6-month surveillance) |
| EU AI Act | High-risk AI system requirements | Annual (when in force) |
| NIST AI RMF | AI risk management framework | Ongoing |
| PCI DSS v4 | Payment card data security | Annual QSA audit |

Full control mappings: `references/compliance-packs.md`

---

## Execution Protocol

**Step 1 — Framework Selection**
Identify the applicable framework(s) based on: customer geography, industry, data types
handled, and contractual requirements. Load the relevant compliance pack from
`references/compliance-packs.md`.

**Step 2 — Control Inventory**
Map all platform capabilities (authentication, encryption, logging, access control,
incident response, change management) to framework controls. Produce a control inventory
table with status: `implemented | partial | not-implemented | not-applicable`.

**Step 3 — Gap Analysis**
For each `partial` or `not-implemented` control: document the gap, risk severity
(Critical/High/Medium/Low), remediation effort (hours), and remediation owner.
Output a prioritized gap register.

**Step 4 — Evidence Collection**
For each `implemented` control: collect evidence artifacts per the schema in
`references/evidence-collection.md`. Evidence types: logs, screenshots, configuration
exports, policy documents, code artifacts, test results.

**Step 5 — Policy Generation**
For any required policy not yet documented: generate a draft policy from the relevant
template. Required policy set: Information Security Policy, Data Classification Policy,
Access Control Policy, Incident Response Policy, Business Continuity Policy, Vendor
Management Policy, AI Governance Policy.

**Step 6 — Audit Package Assembly**
Compile: control inventory, evidence artifacts, gap register (with remediation status),
policy documents, risk register. Format per auditor requirements. Flag any control with
missing or stale evidence (> 90 days old).

---

## Control Domain Map

| Domain | SOC2 | ISO27001 | GDPR | HIPAA | PCI DSS |
|---|---|---|---|---|---|
| Access Control | CC6 | A.9 | Art.25,32 | §164.312(a) | Req.7,8 |
| Encryption at Rest | CC6.7 | A.10 | Art.32 | §164.312(a)(2) | Req.3 |
| Encryption in Transit | CC6.7 | A.10 | Art.32 | §164.312(e) | Req.4 |
| Audit Logging | CC7.2 | A.12.4 | Art.30 | §164.312(b) | Req.10 |
| Incident Response | CC7.3 | A.16 | Art.33,34 | §164.308(a)(6) | Req.12 |
| Vulnerability Management | CC7.1 | A.12.6 | Art.32 | §164.308(a)(1) | Req.6,11 |
| Change Management | CC8 | A.12.1 | Art.25 | §164.308(a)(8) | Req.6 |
| Business Continuity | A1.2 | A.17 | Art.32 | §164.308(a)(7) | Req.12 |
| Vendor Management | CC9.2 | A.15 | Art.28 | §164.308(b) | Req.12 |
| Data Classification | CC6.1 | A.8 | Art.4,9 | §164.514 | Req.3 |

---

## AI-Specific Compliance (EU AI Act / NIST AI RMF)

For AI system components, additionally assess:

| Requirement | EU AI Act | NIST AI RMF |
|---|---|---|
| Risk classification | Art.6,7 | GOVERN 1.1 |
| Transparency obligations | Art.13 | GOVERN 6.1 |
| Human oversight mechanisms | Art.14 | MANAGE 4.1 |
| Accuracy and robustness testing | Art.15 | MEASURE 2.5 |
| Logging and audit trail | Art.12 | MEASURE 2.8 |
| Bias and fairness assessment | Art.10 | MEASURE 2.3 |
| Data governance documentation | Art.10 | MAP 2.2 |

---

## Evidence Staleness Rules

| Evidence Type | Max Age |
|---|---|
| Access control configuration export | 30 days |
| Penetration test report | 12 months |
| Vulnerability scan results | 30 days |
| Training completion records | 12 months |
| Incident response test (tabletop) | 12 months |
| Audit log sample | 30 days |
| Policy document (signed) | 12 months |
| Vendor risk assessment | 12 months |

Flag any stale evidence with severity `HIGH` in the audit package.

---

## References

- `references/compliance-packs.md` — Per-framework control catalogs, requirement details, evidence checklists
- `references/evidence-collection.md` — Evidence types, collection methods, artifact naming, storage schema