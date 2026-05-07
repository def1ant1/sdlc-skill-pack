# Developer Experience Survey Template

## Survey Overview

The DX survey runs quarterly. It takes < 2 minutes to complete. All responses are
anonymous. Results are reviewed by Engineering leadership and actions tracked publicly.

---

## Core Survey Questions (5 Questions)

**Q1 — Overall satisfaction**
"How satisfied are you with your development environment and tools?"
Scale: 1 (Very dissatisfied) → 5 (Very satisfied)

**Q2 — Productivity**
"How often does your development environment or tooling slow you down or interrupt your work?"
Scale: 1 (Daily — constant friction) → 5 (Rarely — environment is smooth)

**Q3 — Onboarding (new hires only, first 90 days)**
"How easy was it to get productive in your first month?"
Scale: 1 (Very difficult) → 5 (Very easy)

**Q4 — Top friction**
"What is the single biggest friction point in your development workflow?"
Free text (required)

**Q5 — Top improvement**
"If you could change one thing about our development experience, what would it be?"
Free text (optional)

---

## SPACE Framework Assessment (Monthly, Management)

Measured by engineering leadership from telemetry and system metrics:

### S — Satisfaction

| Metric | Source | Cadence |
|---|---|---|
| DX survey score (Q1) | Survey | Quarterly |
| Engineering eNPS | HR survey | Semi-annual |
| Voluntary attrition rate | HR | Monthly |

### P — Performance

| Metric | Source | Cadence |
|---|---|---|
| PR merge rate (PRs merged / PRs opened) | GitHub | Monthly |
| Code review turnaround (median hours) | GitHub | Monthly |
| Deployment success rate | CI/CD | Weekly |

### A — Activity

| Metric | Source | Cadence |
|---|---|---|
| Commits per engineer per week | GitHub | Monthly |
| Features shipped per sprint | Jira/Linear | Sprint |
| Test coverage trend | CI | Per deploy |

### C — Communication

| Metric | Source | Cadence |
|---|---|---|
| PR review response time (median hours) | GitHub | Monthly |
| Incident response time | PagerDuty | Monthly |
| Async decision cycle time | Notion/Confluence | Quarterly |

### E — Efficiency

| Metric | Source | Cadence |
|---|---|---|
| Cycle time (commit → deploy) | CI/CD | Weekly |
| CI pipeline pass rate | CI/CD | Weekly |
| Build time (local unit tests) | Developer reports | Quarterly |
| Rework rate (PRs re-opened or reverted) | GitHub | Monthly |

---

## Scoring and Reporting

**Survey score**:
- Each of Q1–Q3: average of all responses (1–5 scale)
- Overall DX score: weighted average (Q1: 40%, Q2: 40%, Q3: 20%)

**Trend tracking**:
```
Quarter  | Q1 Score | Q2 Score | Overall | Top Friction (theme)
---------|----------|----------|---------|-------------------
Q1 2026  | 3.8      | 3.6      | 3.7     | Slow CI (15 min avg)
Q2 2026  | 4.1      | 3.9      | 4.0     | Flaky tests
```

**Action requirement**:
- Overall score ≥ 4.0: publish results; no required action
- Overall score 3.5–3.9: publish results + improvement plan (1 item per quarter)
- Overall score < 3.5: escalate to VP Engineering; dedicated improvement sprint

---

## Friction Categorization

Free-text responses from Q4 are categorized into:

| Category | Examples |
|---|---|
| Build / CI speed | "CI takes 20 min", "local builds are slow" |
| Environment setup | "hard to set up locally", "env vars undocumented" |
| Test quality | "flaky tests", "tests take too long" |
| Documentation | "docs outdated", "can't find API reference" |
| Tooling | "IDE integration broken", "linter too slow" |
| Process | "too many reviews required", "PRs get stuck" |
| Dependencies | "waiting on other team", "unclear API contracts" |