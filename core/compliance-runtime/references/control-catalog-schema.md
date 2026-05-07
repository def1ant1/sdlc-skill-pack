# Compliance Control Catalog Schema

## Control Definition Schema

```yaml
control:
  control_id: "SOC2-CC6.1"              # Unique control identifier
  framework: soc2                        # soc2 | iso27001 | hipaa | gdpr | eu_ai_act
  domain: access_control                 # Control domain within framework
  title: "Logical and Physical Access Controls"
  description: "The entity implements logical access security software, infrastructure, and architectures over protected information assets."

  evaluation:
    method: automated                    # automated | manual | hybrid
    frequency: daily                     # hourly | daily | weekly | monthly | quarterly
    evidence_sources:
      - system: idp                      # Identity provider (Okta, Azure AD)
        query: "list all admin accounts and MFA status"
      - system: audit_trail
        query: "privileged access events last 30 days"

  pass_criterion: "mfa_enabled_count / total_admin_count == 1.0 AND privileged_access_review_age_days <= 90"

  evidence_artifact:
    type: configuration_snapshot         # configuration_snapshot | log_export | screenshot | test_result | attestation
    freshness_days: 1                    # Evidence older than this triggers re-collection

  severity_if_failing: critical          # critical | high | medium | low

  owner: "security-team@corp.com"
  responsible_agent: security-architect-agent
```

---

## Framework Coverage Matrix

| Framework | Total Controls | Automated | Manual | Hybrid |
|-----------|---------------|-----------|--------|--------|
| SOC2 Type II | 64 | 48 | 10 | 6 |
| ISO 27001:2022 | 93 | 61 | 22 | 10 |
| HIPAA Security Rule | 54 | 38 | 12 | 4 |
| GDPR (Technical) | 28 | 18 | 8 | 2 |
| EU AI Act (Art. 9-17) | 22 | 8 | 12 | 2 |

---

## Sample Control Definitions

### SOC2 CC6.3 — Access Removal
```yaml
control_id: "SOC2-CC6.3"
framework: soc2
domain: access_control
title: "Access Removal"
evaluation:
  method: automated
  frequency: daily
  evidence_sources:
    - system: idp
      query: "list accounts for employees terminated in last 30 days and their access status"
  pass_criterion: "terminated_employees_with_active_access == 0"
evidence_artifact:
  type: log_export
  freshness_days: 1
severity_if_failing: critical
```

### GDPR Art. 32 — Security of Processing
```yaml
control_id: "GDPR-ART32-ENC"
framework: gdpr
domain: data_security
title: "Encryption of Personal Data at Rest and in Transit"
evaluation:
  method: automated
  frequency: weekly
  evidence_sources:
    - system: cluster_management
      query: "storage encryption status for all PII-classified data stores"
    - system: telemetry
      query: "TLS certificate validity and cipher suite for all external endpoints"
  pass_criterion: "all_pii_stores_encrypted == true AND all_endpoints_tls12_or_higher == true"
evidence_artifact:
  type: configuration_snapshot
  freshness_days: 7
severity_if_failing: high
```

### EU AI Act Art. 9 — Risk Management
```yaml
control_id: "EU-AIA-ART9-RISK"
framework: eu_ai_act
domain: risk_management
title: "AI System Risk Assessment and Management"
evaluation:
  method: hybrid
  frequency: quarterly
  evidence_sources:
    - system: governance
      query: "AI risk assessment documents and review dates"
    - system: hitl_dashboard
      query: "human oversight mechanism configuration for high-risk AI systems"
  pass_criterion: "risk_assessment_age_days <= 365 AND high_risk_systems_with_hitl == high_risk_systems_total"
evidence_artifact:
  type: attestation
  freshness_days: 90
severity_if_failing: critical
owner: "ai-governance@corp.com"
```

---

## Evidence Vault Schema

```yaml
evidence_artifact:
  artifact_id: "EV-SOC2-CC6.1-2026-05-07"
  control_id: "SOC2-CC6.1"
  framework: soc2
  artifact_type: configuration_snapshot
  collected_at: "2026-05-07T10:00:00Z"
  collected_by: "compliance-runtime/automated"
  content_ref: "evidence-vault/SOC2/CC6.1/2026-05-07.json"
  content_hash_sha256: "abc123..."        # Tamper detection
  evaluation_result: passing
  next_collection_at: "2026-05-08T10:00:00Z"
```

---

## Posture Scoring Formula

```python
def compute_posture_score(controls: list[Control]) -> float:
    """
    Weighted posture score: critical controls count double.
    """
    weights = {"critical": 2.0, "high": 1.5, "medium": 1.0, "low": 0.5}

    total_weight = sum(weights[c.severity_if_failing] for c in controls
                       if c.status != "not_applicable")
    passing_weight = sum(weights[c.severity_if_failing] for c in controls
                         if c.status == "passing")

    if total_weight == 0:
        return 100.0

    return (passing_weight / total_weight) * 100.0
```