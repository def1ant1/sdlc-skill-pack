# Security Scan Pipeline

## Pipeline Overview

The security scan pipeline runs automatically on every push and PR. Results are
classified by severity and enforced through merge gates. All findings are logged
to the vulnerability registry and tracked to closure.

---

## Pipeline Stages

```
Code Push / PR Open
        │
        ▼
┌──────────────────┐
│ 1. SAST          │  Static analysis of source code
│    (< 3 min)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 2. Dependency    │  Known CVEs in third-party deps
│    Scan (< 2min) │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 3. Secret Scan   │  Credentials, tokens, keys in code
│    (< 1 min)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 4. Container     │  Base image CVEs (on Dockerfile change)
│    Scan          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 5. DAST          │  Dynamic scan of deployed staging (pre-merge)
│    (< 15 min)    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 6. IaC Scan      │  Misconfiguration in Terraform/Helm/K8s YAML
└──────┬───────────┘
       │
       ▼
    Results → Merge Gate Evaluation
```

---

## Tool Configuration

| Stage | Tool | Scope |
|---|---|---|
| SAST | Semgrep (custom ruleset + OWASP) | All source files |
| Dependency | OWASP Dependency-Check / Trivy | `go.sum`, `package-lock.json`, `requirements.txt` |
| Secret | TruffleHog or gitleaks | All commits in PR diff |
| Container | Trivy | `Dockerfile` and base images |
| DAST | OWASP ZAP (baseline scan) | Staging environment post-deploy |
| IaC | Checkov | `terraform/`, `k8s/`, `helm/` |

---

## Severity Classification

| Severity | Definition | Merge Gate |
|---|---|---|
| CRITICAL | Exploitable remotely; data loss or full compromise | Blocks immediately; no exceptions |
| HIGH | Exploitable with elevated access or significant impact | Blocks merge; requires security sign-off to override |
| MEDIUM | Limited exploitability or impact; workaround exists | Must be acknowledged and triaged within 5 days |
| LOW | Informational; minimal real-world risk | Logged; addressed in next maintenance window |
| INFO | Dependency versions, best practice suggestions | No action required |

---

## Merge Gate Rules

```
CRITICAL findings: 0 permitted → CI fails hard
HIGH findings:     0 unacknowledged → CI fails
                   acknowledged HIGH with security sign-off → CI passes with warning
MEDIUM findings:   all must have triage ticket created → CI passes with warning
LOW findings:      logged; CI passes unconditionally
```

**Acknowledgment process**: Add finding ID to `security/acknowledged.yaml` with
justification, owner, and target fix date. PR must include updated `acknowledged.yaml`
when acknowledging HIGH findings.

---

## False Positive Management

1. Open a false positive issue with finding ID and evidence
2. Security skill reviews and approves within 2 business days
3. Approved false positives added to tool-specific suppress list
4. Suppress list reviewed quarterly; stale suppressions removed

---

## Scan Results Storage

All scan results are stored:
- As CI artifacts (retained 180 days)
- In the vulnerability registry (retained indefinitely)
- Summary counts published to the observability dashboard

Results feed the weekly security posture report in compliance-governance.