# Compliance Posture Reporting — Report Template Specification

## Report Types

| Report Type | Audience | Cadence | Format |
|------------|---------|---------|--------|
| Executive Compliance Summary | Board / C-Suite | Monthly | 1-page PDF |
| Regulatory Posture Report | Legal / Compliance team | Monthly | Full PDF |
| Control Health Dashboard | Compliance agent / Ops | Real-time | Dashboard |
| Audit Evidence Package | External auditors | On-demand | ZIP + PDF |
| Risk Register | CISO / Board | Quarterly | PDF + XLSX |
| Framework Gap Analysis | Compliance team | Quarterly | PDF |

---

## Executive Compliance Summary Template

```
APOTHEON PLATFORM — COMPLIANCE POSTURE SUMMARY
Period: [Month Year]
Generated: [Date] by compliance-posture-reporting skill

┌─────────────────────────────────────────────────────────┐
│  OVERALL POSTURE SCORE: [XX/100]  Status: [COMPLIANT]   │
└─────────────────────────────────────────────────────────┘

FRAMEWORK STATUS
─────────────────────────────────────────────────────────
Framework     Controls  Passing  At-Risk  Failing  Score
─────────────────────────────────────────────────────────
SOC 2 Type II    52       49        2        1      94%
ISO 27001        93       88        4        1      95%
EU AI Act        28       25        3        0      89%
GDPR             35       34        1        0      97%
─────────────────────────────────────────────────────────
COMBINED          208      196       10       2      94%

OPEN FINDINGS
─────────────────────────────────────────────────────────
# Finding                          Framework  Due      Owner
1 Encryption key rotation overdue  SOC2/ISO   05-14    SRE
2 Training data lineage gap        EU AI Act  05-21    ML-Ops
3 Vendor assessment overdue (AWS)  ISO        05-28    Legal

TREND
─────────────────────────────────────────────────────────
Prior month score: 91% → Current: 94% (+3pp)
Findings resolved since last report: 7
New findings since last report: 2

NEXT AUDIT
─────────────────────────────────────────────────────────
SOC 2 Type II annual audit: 2026-09-15
Auditor: Deloitte
Status: On track
```

---

## Regulatory Posture Report Schema

```yaml
compliance_posture_report:
  report_id: "CPR-2026-xxxxx"
  generated_at: "2026-05-07T00:00:00Z"
  period:
    start: "2026-04-01"
    end: "2026-04-30"
  report_type: monthly_posture
  generated_by: "compliance-posture-reporting"

  overall:
    posture_score: 94
    posture_status: compliant | at_risk | non_compliant
    total_controls: 208
    controls_passing: 196
    controls_at_risk: 10
    controls_failing: 2

  framework_scores:
    - framework: SOC2_TYPE2
      applicable_controls: 52
      passing: 49
      at_risk: 2
      failing: 1
      score_pct: 94.2
      trend: improving   # improving | stable | declining
      last_audit_date: "2025-09-15"
      next_audit_date: "2026-09-15"

    - framework: ISO_27001_2022
      applicable_controls: 93
      passing: 88
      at_risk: 4
      failing: 1
      score_pct: 94.6
      trend: stable

    - framework: EU_AI_ACT
      applicable_controls: 28
      passing: 25
      at_risk: 3
      failing: 0
      score_pct: 89.3
      trend: improving

  open_findings:
    - finding_id: "FIND-2026-xxxxx"
      control_id: "SOC2-CC6.7"
      title: "Encryption key rotation overdue"
      severity: high
      status: open
      due_date: "2026-05-14"
      owner: "sre-agent"
      days_open: 12

  resolved_findings:
    - finding_id: "FIND-2026-yyyyy"
      title: "MFA not enforced for all admin accounts"
      resolved_at: "2026-04-15"
      resolution: "MFA policy enforced via zero-trust-runtime"

  evidence_collection:
    total_evidence_items: 847
    collected_this_period: 94
    automated_collection_pct: 88.0
    pending_manual_collection: 11

  attestation:
    attested_by: null   # Requires human sign-off before distribution
    attested_at: null
    distribution: [board, legal-team, external-auditors]
```

---

## Audit Evidence Package Schema

```yaml
audit_evidence_package:
  package_id: "AEP-2026-xxxxx"
  framework: SOC2_TYPE2
  audit_period:
    start: "2025-10-01"
    end: "2026-09-30"
  generated_at: "2026-05-07T00:00:00Z"
  generated_for: "Deloitte — SOC 2 Type II Audit"

  contents:
    - section: "Control Environment"
      control_ids: [SOC2-CC1.1, SOC2-CC1.2, SOC2-CC1.3]
      evidence_items:
        - evidence_id: "EV-2026-00001"
          type: policy_document
          title: "Information Security Policy v4.1"
          uri: "vault://compliance/policies/infosec-policy-v4.1.pdf"
          collected_at: "2026-04-01T00:00:00Z"
          hash: "sha256:abc123"

    - section: "Logical Access"
      control_ids: [SOC2-CC6.1, SOC2-CC6.2, SOC2-CC6.3]
      evidence_items:
        - evidence_id: "EV-2026-00042"
          type: automated_export
          title: "Access review log — April 2026"
          uri: "vault://compliance/evidence/access-review-2026-04.csv"
          collected_at: "2026-05-01T06:00:00Z"
          hash: "sha256:def456"

  package_format: zip_with_index    # ZIP containing all evidence + manifest PDF
  encryption: AES-256-GCM
  access_control: auditor-only
  retention_years: 7
```

---

## Report Distribution Policy

```yaml
distribution_policy:
  executive_summary:
    recipients: [board-members, ceo, cto, ciso]
    channel: email_with_pdf_attachment
    requires_human_approval_before_send: true
    approver: ciso

  regulatory_posture:
    recipients: [compliance-team, legal-team]
    channel: google_drive_share
    requires_human_approval_before_send: true
    approver: compliance-lead

  audit_evidence:
    recipients: [external-auditors]
    channel: secure_file_transfer   # e.g. ShareFile, Box
    requires_human_approval_before_send: true
    approver: ciso
    encrypt: true

  control_health_dashboard:
    access: compliance-agent, sre-agent, security-architect-agent
    channel: internal_dashboard_api
    requires_human_approval_before_send: false   # Automated; internal only
```