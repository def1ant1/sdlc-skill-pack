# Evidence Collection

Used by `skills/compliance-automation/SKILL.md` to define evidence types, collection
methods, artifact naming conventions, and the evidence storage schema.

---

## Evidence Types

| Type | Description | Collection Method |
|---|---|---|
| `log_export` | Audit logs, access logs, system logs | Automated export from SIEM/log platform |
| `config_export` | Security configuration, IAM policies | API export or screenshot with metadata |
| `policy_document` | Written policy, signed by owner | Document repository pull |
| `screenshot` | UI state capture with timestamp | Manual capture with metadata annotation |
| `test_result` | Penetration test, scan, DR test report | Uploaded PDF/report from vendor |
| `training_record` | Completion certificates, attendance | HR/LMS export |
| `attestation` | Signed statement from responsible party | Signed document with date |
| `code_artifact` | Relevant code showing control implementation | Git commit hash + file path |
| `ticket_export` | Change management, incident records | Jira/Linear export |
| `contract` | DPA, BAA, vendor contract | Document repository |

---

## Artifact Naming Convention

```
<framework>_<control_id>_<evidence_type>_<YYYY-MM-DD>.<ext>
```

Examples:
```
soc2_CC6.1_config_export_2026-05-06.json
gdpr_Art32_log_export_2026-05-01.csv
hipaa_164.312a_attestation_2026-04-15.pdf
iso27001_A.9.1_policy_document_2026-01-10.pdf
```

---

## Evidence Storage Schema

```yaml
evidence_artifact:
  id: "EVD-YYYYMMDD-NNN"           # Sequential within day
  framework: "soc2 | gdpr | hipaa | iso27001 | eu_ai_act | nist_ai_rmf | pci_dss"
  control_id: "<framework control reference>"
  control_name: "<human-readable control name>"
  evidence_type: "<type from table above>"
  collected_by: "<user or automated>"
  collected_at: "YYYY-MM-DDThh:mm:ssZ"
  period_start: "YYYY-MM-DD"       # Start of evidence period
  period_end: "YYYY-MM-DD"         # End of evidence period
  artifact_path: "<storage path or URL>"
  artifact_hash_sha256: "<hash of file>"
  notes: "<any relevant context>"
  reviewed_by: "<reviewer name>"    # null until reviewed
  reviewed_at: "YYYY-MM-DDThh:mm:ssZ"  # null until reviewed
  status: "collected | reviewed | accepted | rejected"
  expiry_date: "YYYY-MM-DD"        # Computed from max-age rules
```

---

## Automated Collection Sources

### Logs (Automated)

| Source | Connector | Frequency | Formats |
|---|---|---|---|
| Application audit log | Telemetry connector | Daily | JSON |
| Infrastructure access log | Cloud platform API | Daily | JSON/CSV |
| Authentication events | Identity provider | Daily | JSON |
| Network flow logs | Cloud VPC | Weekly | CSV |
| Vulnerability scan | Scanner API | Monthly | JSON/PDF |

### Configurations (Automated)

| Source | Connector | Key Fields |
|---|---|---|
| IAM policies | Cloud platform API | Roles, permissions, last modified |
| Encryption config | KMS/secrets manager API | Algorithm, key rotation date |
| Network security groups | Cloud platform API | Inbound/outbound rules |
| MFA enforcement | Identity provider | Enabled users %, exceptions |
| TLS configuration | SSL scanner | Cipher suites, certificate expiry |

---

## Evidence Gap Detection

Run gap detection after each collection cycle:

1. For each control in `status: implemented`: check evidence artifact exists and is not stale
2. Stale = `collected_at` > max-age for evidence type (see SKILL.md staleness rules)
3. Missing = no artifact exists for control
4. Output gap report:

```yaml
gap_report:
  generated_at: "YYYY-MM-DDThh:mm:ssZ"
  framework: "<framework>"
  audit_period: "YYYY-MM-DD – YYYY-MM-DD"
  gaps:
    - control_id: "<id>"
      control_name: "<name>"
      gap_type: "missing | stale"
      severity: "Critical | High | Medium | Low"
      last_collected: "YYYY-MM-DD | never"
      remediation: "<action to collect>"
      owner: "<team>"
      due_date: "YYYY-MM-DD"
```

---

## Audit Package Assembly Checklist

```
[ ] All implemented controls have non-stale evidence
[ ] All policy documents are current (< 12 months) and signed
[ ] Gap register is complete with remediation status for all gaps
[ ] Evidence artifacts are named per convention and hashed
[ ] Evidence index CSV generated (id, control, type, date, path)
[ ] Penetration test report included (< 12 months)
[ ] Most recent vulnerability scan included (< 30 days)
[ ] Training records included (> 95% workforce completion)
[ ] Incident log for audit period included
[ ] Operator review sign-off obtained before submission
```