# Marketplace Publishing — Certification Gate Specification

## Gate Overview

Every skill must pass all applicable gates before appearing in the public marketplace. Gates are executed in order; a gate failure blocks all subsequent gates.

| Gate | ID | Automated | Blocking | Required For |
|------|----|-----------|----------|-------------|
| Manifest Schema | G-01 | Yes | Yes | All tiers |
| Checksum Integrity | G-02 | Yes | Yes | All tiers |
| Static Analysis | G-03 | Yes | Yes | All tiers |
| Vulnerability Scan | G-04 | Yes | Yes | Verified + Enterprise |
| Sandbox Smoke Test | G-05 | Yes | Yes | All tiers |
| Permission Review | G-06 | Human | Yes | If `network: true` or `subprocess: true` |
| SLA Review | G-07 | Human | Yes | Enterprise |
| Legal Sign-off | G-08 | Human | Yes | Enterprise |

---

## Gate Specifications

### G-01: Manifest Schema Validation

```yaml
checks:
  - field: skill_name
    rule: "^[a-z][a-z0-9-]*[a-z0-9]$"   # kebab-case
  - field: skill_version
    rule: "^\\d+\\.\\d+\\.\\d+$"          # SemVer
  - field: description
    rule: "max_length: 1024 AND no_angle_brackets"
  - field: runtime_api_version
    rule: "must be a supported API version"
  - required_fields:
    - skill_name
    - skill_version
    - runtime_api_version
    - entrypoint.handler
    - author.name
    - author.org
```

### G-02: Checksum Integrity

Recomputes SHA-256 of all files in bundle (excluding `manifest.yaml`) and compares against `checksum.value`. Any mismatch → immediate rejection with event type `INTEGRITY_VIOLATION`.

### G-03: Static Analysis

```yaml
tools:
  python:
    - ruff: "max_errors: 0"
    - bandit: "severity_threshold: medium"  # Any medium+ finding is a failure

pass_criteria:
  ruff_errors: 0
  bandit_findings_medium_or_above: 0
```

### G-04: Vulnerability Scan

Uses OSV (Open Source Vulnerabilities) database. Checks all declared `dependencies` in `manifest.yaml`.

```yaml
pass_criteria:
  critical_cves: 0
  high_cves: 0
  medium_cves: "<=2 with documented mitigations"
```

### G-05: Sandbox Smoke Test

Executes the skill handler with the synthetic test vectors in `tests/`. Validates:
- No permission violations
- Response conforms to declared output schema
- Latency P95 < 5,000 ms
- Memory usage < declared `memory_limit_mb`

### G-06: Permission Review (Human)

Triggered when `network: true` or `subprocess: true`. A portal reviewer must approve:
- Documented justification for the permission
- List of specific `external_apis` or subprocesses
- Data handling description for external calls

### G-07: SLA Review (Human, Enterprise only)

Operations team reviews:
- Declared `timeout_seconds` is appropriate for the workload
- `max_calls_per_minute` quota is provisioned
- Runbook exists for skill failure scenarios

### G-08: Legal Sign-off (Human, Enterprise only)

Legal reviews:
- Data classification of inputs/outputs
- Third-party API terms of service compliance
- Export control if AI model is involved

---

## Tier Requirements Summary

| Requirement | Community | Verified | Enterprise |
|-------------|-----------|----------|------------|
| All G-01–G-03 | Required | Required | Required |
| G-04 (vuln scan) | Optional | Required | Required |
| G-05 (smoke test) | Required | Required | Required |
| G-06 (perm review) | If triggered | If triggered | If triggered |
| G-07 (SLA review) | No | No | Required |
| G-08 (legal) | No | No | Required |
| Peer review (2 approvals) | No | Required | Required |
| Reference docs | Recommended | Required | Required |
| Test coverage ≥ 80% | No | Required | Required |

---

## Revocation Policy

A published skill version may be revoked if:

| Trigger | Revocation Type | SLA |
|---------|----------------|-----|
| Critical CVE discovered post-publish | Immediate yank | < 1 hour |
| Behavioral contract violation reported | Pending review → yank | < 24 hours |
| Author requests withdrawal | Soft-delete (existing installs unaffected) | < 4 hours |
| Policy violation (data exfiltration detected) | Hard revoke + blacklist | < 15 minutes |

Revoked skills are removed from search results. Active installations receive a deprecation notice via notification-orchestration.

---

## Publish Event Schema

```yaml
publish_event:
  event_id: "PUB-2026-xxxxx"
  skill_name: "skill-name"
  skill_version: "x.y.z"
  publisher: "author@example.com"
  submitted_at: "2026-05-07T10:00:00Z"
  tier_requested: community | verified | enterprise
  gates_passed: [G-01, G-02, G-03, G-05]
  gates_pending: []
  gates_failed: []
  outcome: published | rejected | pending
  published_at: "2026-05-07T10:10:00Z"
  certificate_id: "CERT-ID-xxxxx"
```