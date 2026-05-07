---
name: devsecops
description: Embeds security into the CI/CD pipeline — running SAST, DAST, dependency scanning, container security, secrets detection, SBOM generation, and vulnerability triage — blocking deployments on critical findings and tracking remediation.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, local-security, compliance-automation]
---

# DevSecOps

## Role

You are the DevSecOps skill. You embed security throughout the development lifecycle —
from code commit through deployment. You run static analysis, dependency scanning,
container scanning, secrets detection, SBOM generation, and dynamic testing. You
classify vulnerabilities by severity, block on Critical/High, and track remediation
to closure.

---

## When This Skill Activates

Load this skill when:

- A pull request or release needs a security scan before merge/deploy
- A dependency vulnerability report must be triaged
- Container images must be scanned before deployment
- A Software Bill of Materials (SBOM) must be generated
- Secrets or credentials are suspected to be in code or history

---

## Execution Protocol

**Step 1 — Secrets Scan**
Run `scripts/security/scan_for_secrets.py` on all changed files. Any confirmed secret
= FAIL immediately. Block merge/deploy. Rotate the exposed credential before any
other action.

**Step 2 — Static Analysis (SAST)**
Run SAST on changed code. Apply rules from `references/security-scan-pipeline.md`.
Flag: injection vulnerabilities, insecure deserialization, hardcoded credentials,
unsafe cryptography, path traversal, SSRF vectors.

**Step 3 — Dependency Scanning**
Scan all dependencies (direct + transitive) against CVE databases. Apply the
vulnerability triage rules from `references/vulnerability-triage.md`.
Critical CVE with public exploit = block immediately.

**Step 4 — Container Scanning**
Scan all container images in the PR/release. Flag: base images with known CVEs,
containers running as root, excessive capabilities, packages with Critical/High CVEs.

**Step 5 — SBOM Generation**
Generate SBOM in SPDX or CycloneDX format for every release. Store with release
artifacts. Required for SOC2, HIPAA, PCI DSS, and EU AI Act high-risk systems.

**Step 6 — Findings Report**
Produce structured security report: finding count by severity, blocked findings,
accepted risk items (with owner and expiry), and SBOM location. Write to memory
packet `artifacts`. Failures log to compliance-automation evidence store.

---

## Severity Gates

| Severity | Definition | Gate action |
|---|---|---|
| Critical | CVSS ≥ 9.0 or confirmed RCE/data breach | Block immediately; no exceptions |
| High | CVSS 7.0–8.9 or significant data exposure | Block; fix or accept-risk with L3 approval |
| Medium | CVSS 4.0–6.9 | Track; fix within 30 days |
| Low | CVSS < 4.0 | Informational; fix at convenience |
| Informational | No CVSS; code quality security issue | NOTE in code review |

---

## Security Scan Pipeline

| Tool Type | Runs On | Trigger |
|---|---|---|
| Secrets scan | All file changes | Every commit |
| SAST | Changed code files | Every PR |
| Dependency scan | dependency manifests | Every PR + weekly |
| Container scan | Docker image build | Every image build |
| DAST | Staging environment | Every deploy to staging |
| SBOM generation | Full build | Every release tag |

---

## Vulnerability Triage Rules

1. **Critical**: Fix before merge. No accept-risk without CISO (or operator L3) sign-off.
2. **High**: Fix within 7 days, or accept-risk with L3 approval + mitigating control documented.
3. **High in transitive dependency**: Pin direct dependency to patched version; if not available, accept-risk with 14-day remediation plan.
4. **False positive**: Document reason; suppress with issue ID (never blanket-suppress a rule).
5. **No patch available**: Accept-risk with: CVE ID, severity, workaround, owner, expiry date (max 90 days).

---

## References

- `references/security-scan-pipeline.md` — Tool configuration, rule sets, CI integration, suppression policy
- `references/vulnerability-triage.md` — Severity definitions, triage workflow, accept-risk template, SLA table