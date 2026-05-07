# Continuous Control Monitoring — SOC2 & ISO 27001 Control Catalog

## SOC2 Type II — Common Criteria Controls

| Control ID | Domain | Title | Method | Frequency | Severity |
|-----------|--------|-------|--------|-----------|----------|
| CC1.1 | Control Environment | COSO Principle 1: Commitment to integrity | hybrid | quarterly | high |
| CC2.1 | Communication | Obtaining/generating quality information | hybrid | monthly | medium |
| CC3.1 | Risk Assessment | Specifying objectives | manual | quarterly | high |
| CC5.1 | Control Activities | Controls to mitigate risk | hybrid | monthly | high |
| CC6.1 | Logical Access | Logical access security | automated | daily | critical |
| CC6.2 | Logical Access | Authentication before access | automated | daily | critical |
| CC6.3 | Logical Access | Access removal for terminated users | automated | daily | critical |
| CC6.6 | Logical Access | Security threats outside system boundaries | automated | weekly | high |
| CC6.7 | Logical Access | Encryption of data in transmission | automated | weekly | critical |
| CC7.1 | Systems Operations | Configuration baseline management | automated | daily | high |
| CC7.2 | Systems Operations | System alerts and monitoring | automated | daily | high |
| CC7.4 | Systems Operations | Incident response | hybrid | monthly | critical |
| CC8.1 | Change Management | Change authorization and testing | automated | daily | high |
| CC9.1 | Risk Mitigation | Risk identification and assessment | manual | quarterly | high |
| CC9.2 | Risk Mitigation | Vendor/supplier management | hybrid | quarterly | high |

---

## SOC2 Evaluation Methods — Key Controls

### CC6.1 — Logical Access Security Controls
```yaml
evaluation:
  method: automated
  steps:
    - query: idp
      check: "All admin accounts have MFA enabled"
      evidence: "Admin account roster with MFA status"
      pass_if: "mfa_count / admin_count == 1.0"

    - query: zero-trust-runtime
      check: "All service-to-service calls use mTLS or valid JWT"
      evidence: "Authentication log sample (last 1000 requests)"
      pass_if: "auth_failure_rate < 0.001"

    - query: cluster-management
      check: "Network policies enforce least-privilege connectivity"
      evidence: "Network policy configuration snapshot"
      pass_if: "default_deny_policy_present == true"
```

### CC6.7 — Encryption of Data in Transmission
```yaml
evaluation:
  method: automated
  steps:
    - query: telemetry
      check: "All external endpoints use TLS 1.2 or higher"
      evidence: "TLS certificate and cipher suite scan results"
      pass_if: "tls_below_1_2_endpoints == 0"

    - query: cluster-management
      check: "Inter-service communication uses mTLS"
      evidence: "Service mesh configuration showing mTLS enforcement"
      pass_if: "mtls_enforcement_mode == strict"
```

### CC8.1 — Change Management
```yaml
evaluation:
  method: automated
  steps:
    - query: itsm-integration
      check: "All production deployments have an approved change record"
      evidence: "Change record audit trail for last 30 days"
      pass_if: "deployments_without_change_record == 0"

    - query: audit-trail
      check: "Changes were deployed by a different person than the requester"
      evidence: "Deployment log with requester and approver IDs"
      pass_if: "requester_equals_approver_count == 0"
```

---

## ISO 27001:2022 — Annex A Controls (Selected)

| Control ID | Domain | Title | Method | Frequency | Severity |
|-----------|--------|-------|--------|-----------|----------|
| A.5.9 | Information Security Policies | Policy review | manual | annual | medium |
| A.5.15 | Access Control | Access control policy | hybrid | quarterly | high |
| A.5.16 | Identity Management | Identity management | automated | daily | critical |
| A.5.17 | Authentication | Authentication information | automated | daily | critical |
| A.5.23 | Cloud Services | Security for cloud services | automated | weekly | high |
| A.7.8 | Physical Security | Equipment siting and protection | manual | quarterly | medium |
| A.8.3 | Information Classification | Information labeling | automated | weekly | high |
| A.8.5 | Secure Authentication | Secure authentication | automated | daily | critical |
| A.8.6 | Capacity Management | Capacity management | automated | daily | medium |
| A.8.7 | Malware Protection | Malware protection | automated | daily | critical |
| A.8.9 | Configuration Management | Configuration of infrastructure | automated | daily | high |
| A.8.12 | Data Leakage Prevention | Data leakage prevention | automated | weekly | high |
| A.8.15 | Logging | Logging | automated | daily | high |
| A.8.16 | Monitoring | Monitoring activities | automated | hourly | critical |
| A.8.24 | Use of Cryptography | Use of cryptography | automated | weekly | critical |
| A.8.28 | Secure Coding | Secure coding | automated | per-deployment | high |

---

## EU AI Act Controls (Article 9-17)

| Control ID | Article | Requirement | Method | Frequency |
|-----------|---------|-------------|--------|-----------|
| EU-AIA-ART9 | Art. 9 | Risk management system | hybrid | quarterly |
| EU-AIA-ART10 | Art. 10 | Data governance | automated | monthly |
| EU-AIA-ART11 | Art. 11 | Technical documentation | manual | per-release |
| EU-AIA-ART12 | Art. 12 | Record keeping / logging | automated | daily |
| EU-AIA-ART13 | Art. 13 | Transparency to users | manual | quarterly |
| EU-AIA-ART14 | Art. 14 | Human oversight | automated | daily |
| EU-AIA-ART15 | Art. 15 | Accuracy and robustness | automated | monthly |
| EU-AIA-ART17 | Art. 17 | Quality management system | manual | annual |

---

## Evidence Freshness Policy

```yaml
evidence_freshness:
  automated_controls:
    critical: 1 day
    high: 7 days
    medium: 30 days
    low: 90 days

  manual_controls:
    critical: 7 days
    high: 30 days
    medium: 90 days
    low: 365 days

  stale_evidence_action: "Re-evaluate and collect fresh evidence before the next audit window"
```