# Dependency Analysis

## Dependency Health Metrics

| Metric | Description | Alert Threshold |
|---|---|---|
| Outdated packages | Packages more than 2 major versions behind | > 5 packages |
| Known vulnerabilities | CVEs in any direct or transitive dependency | Any CRITICAL or HIGH |
| Unused dependencies | Packages declared but not imported anywhere | Any |
| Circular dependencies | Package A imports B which imports A | Any |
| Deep dependency tree | Transitive dependency depth | > 10 levels |

---

## Dependency Classification

### Direct vs Transitive

- **Direct**: Explicitly declared in `go.mod`, `package.json`, `requirements.txt`, etc.
- **Transitive**: Pulled in by direct dependencies; not explicitly declared

Security responsibility: Direct dependencies are your responsibility to update.
Transitive vulnerabilities must be resolved by either updating the direct dependency
that pulls them in or explicitly overriding.

---

## Update Strategy

| Dependency Type | Update Cadence | Trigger |
|---|---|---|
| Security patches (CVE) | Immediate (within 48h for CRITICAL) | CVE announcement |
| Minor version (bug fixes) | Monthly | Scheduled maintenance |
| Major version (breaking changes) | Planned (requires testing) | Tech debt sprint |
| Dev/test-only dependencies | Quarterly | Scheduled maintenance |

---

## Dependency Risk Scoring

Score each direct dependency on three axes:

```
popularity_score   = log10(weekly_downloads) / 10        # 0–1
maintenance_score  = 1 if updated < 6 months else 0.5
                    if updated < 12 months else 0
vulnerability_score = 1 - (critical_cves * 0.3 + high_cves * 0.1)

risk_score = 1 - (popularity_score * 0.3 + maintenance_score * 0.4 + vulnerability_score * 0.3)
# risk_score 0.0 = safe; 1.0 = very risky
```

Flag any dependency with risk_score > 0.6 for replacement evaluation.

---

## Dependency Report Format

```
DEPENDENCY ANALYSIS — <service> — YYYY-MM-DD
=============================================
Total dependencies:     N direct, N transitive
Vulnerable:             N (CRITICAL: N, HIGH: N, MEDIUM: N)
Outdated (major):       N packages
Unused:                 N packages

HIGH RISK DEPENDENCIES
  [package@version] | Risk: 0.75 | Reason: No update in 18 months + 2 HIGH CVEs
    CVE-YYYY-NNNN: [description] — Fix available in v2.3.1
    Action: Upgrade to v2.3.1 | Owner: Platform team | Due: YYYY-MM-DD

OUTDATED DIRECT DEPENDENCIES
  [package]: v1.2.3 → v3.0.0 | Breaking changes | Migration guide: [URL]

UNUSED DEPENDENCIES
  [package]: imported in go.mod but no import statements found
    Action: Remove from go.mod

CIRCULAR DEPENDENCIES
  [package A] → [package B] → [package A]
    Action: Introduce interface to break cycle
```

---

## Approved License List

Dependencies must use one of these licenses:

| License | Permitted Use |
|---|---|
| MIT | All (permissive) |
| Apache 2.0 | All (permissive with patent grant) |
| BSD-2/3-Clause | All (permissive) |
| ISC | All (permissive) |
| MPL 2.0 | Permitted with source disclosure for modified files |
| LGPL | Library use permitted; do not modify LGPL code |
| GPL / AGPL | Requires legal review before use |
| Commercial / proprietary | Requires procurement and legal sign-off |

Any dependency with a non-approved license requires legal-ops review before inclusion.