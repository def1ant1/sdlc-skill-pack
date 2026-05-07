# Control Attestation

## Overview

Control attestation is the formal process by which policy owners confirm that a
policy is being followed and its associated controls are implemented and effective.
Attestation is required annually for all policies and may be triggered by:
- A scheduled review date being reached
- A significant change to the policy or its scope
- An audit preparation requirement
- A compliance gap being identified

---

## Attestation Workflow

```
1. INITIATION
   - Compliance-governance skill identifies policy due for attestation
   - Attestation package prepared (see below)
   - Package routed to policy owner via hitl-dashboard

2. OWNER REVIEW (SLA: 5 business days)
   - Policy owner reviews policy text, evidence, and control status
   - Owner updates any stale evidence
   - Owner confirms adherence or identifies gaps

3. SIGN-OFF
   - Owner submits attestation: CONFIRM | PARTIAL | EXCEPTION
   - Route to Level-2 approver for review
   - Level-2 approver approves or requests additional evidence

4. RECORDING
   - Attestation record written to compliance registry
   - Next attestation date set (12 months default; 6 months for high-risk policies)
   - Evidence links archived

5. GAP HANDLING (if PARTIAL or EXCEPTION)
   - Gap documented in risk register
   - Remediation plan required within 10 business days
   - Escalated to Level-3 if gap is Critical severity
```

---

## Attestation Package Contents

The attestation package delivered to the policy owner must include:

1. **Policy document** (current version with version number and effective date)
2. **Control list** — all controls associated with this policy with current status
3. **Evidence summary** — evidence on file for each control, with date collected
4. **Stale evidence flag** — any evidence older than 90 days highlighted
5. **Gap list** — any controls without evidence or with FAIL status
6. **Prior attestation** — result and date of the last attestation cycle
7. **Sign-off form** — digital attestation form with options below

---

## Attestation Outcomes

| Outcome | Meaning | Follow-up Required |
|---|---|---|
| CONFIRM | Policy is being followed; all controls implemented; evidence current | None; record and set next date |
| PARTIAL | Most controls implemented; minor gaps with remediation plan | Remediation plan required within 10 days |
| EXCEPTION | Significant gap; policy not fully followed; risk accepted | Risk register entry required; Level-3 approval; compensating controls |

---

## Attestation Record Schema

```yaml
attestation:
  id: "ATT-YYYYMMDD-NNN"
  policy_id: "<policy identifier>"
  policy_version: "x.y.z"
  cycle_date: "YYYY-MM-DD"
  owner: "<owner name/role>"
  approver: "<Level-2 approver>"
  outcome: "CONFIRM | PARTIAL | EXCEPTION"
  controls_reviewed: N
  controls_implemented: N
  controls_with_gaps: N
  evidence_reviewed: [list of evidence IDs]
  gaps_identified:
    - control_id: "<id>"
      description: "<gap>"
      severity: "critical | high | medium | low"
      remediation_due: "YYYY-MM-DD"
      remediation_owner: "<owner>"
  exceptions_accepted: []
  signed_by: "<owner>"
  signed_at: "ISO8601"
  approved_by: "<approver>"
  approved_at: "ISO8601"
  next_attestation: "YYYY-MM-DD"
  notes: "<free text>"
```

---

## Evidence Requirements

Evidence must be:

1. **Recent**: Collected within 90 days of attestation (or as required by the framework)
2. **Relevant**: Directly demonstrates the control is operating
3. **Complete**: Covers the full scope of the control (all systems, all users, etc.)
4. **Authentic**: Verifiable; traceable to an authoritative source

Evidence types accepted:

| Type | Example | Acceptable for |
|---|---|---|
| System screenshot | Dashboard showing MFA enabled for all users | Access control controls |
| Audit log export | SIEM logs showing access reviewed quarterly | Access review controls |
| Configuration file | Policy document from version control | Policy controls |
| Scan report | Vulnerability scan results from CI | Vulnerability management |
| Training completion record | LMS export showing staff completion | Training controls |
| Penetration test report | Third-party pentest results | Security testing |

---

## High-Risk Policy Attestation

Policies classified as high-risk require:

- Semi-annual attestation (every 6 months, not annually)
- Level-3 approver sign-off (not Level-2)
- Third-party evidence validation for at least 2 controls per cycle

High-risk classification triggers:
- Policy covers PII or sensitive data processing
- Policy is required by a regulatory framework (GDPR, SOC 2, ISO 27001)
- Policy was the subject of a prior compliance gap or audit finding