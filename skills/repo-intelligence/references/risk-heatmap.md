# Risk Heatmap

Used by `skills/repo-intelligence/SKILL.md` to compute a composite risk score per file
and produce a prioritized list of the highest-risk files in the repository.

---

## Risk Score Formula

```
risk_score = (complexity_score * 0.40)
           + (churn_score * 0.35)
           + (coverage_gap_score * 0.25)
```

All component scores are normalized to 0–100 before weighting.

---

## Component Score Definitions

### Complexity Score (weight: 40%)

| Cyclomatic Complexity | Score |
|---|---|
| 1–5 | 10 |
| 6–10 | 30 |
| 11–15 | 60 |
| 16–25 | 80 |
| > 25 | 100 |

Use the **maximum** function complexity in the file (not the average).

### Churn Score (weight: 35%)

Commits touching the file in the last 90 days:

| Commits in 90 Days | Score |
|---|---|
| 0–2 | 10 |
| 3–5 | 25 |
| 6–10 | 50 |
| 11–20 | 75 |
| > 20 | 100 |

High churn + high complexity = highest risk combination.

### Coverage Gap Score (weight: 25%)

| Test Coverage | Score |
|---|---|
| 90–100% | 0 |
| 75–89% | 20 |
| 50–74% | 50 |
| 25–49% | 75 |
| 0–24% | 100 |
| No test data | 60 (assumed partial) |

---

## Risk Level Classification

| Composite Score | Risk Level | Recommended Action |
|---|---|---|
| 80–100 | Critical | Immediate test coverage + refactoring sprint |
| 60–79 | High | Add tests before next feature work; schedule refactor |
| 40–59 | Medium | Monitor; add tests on next touch |
| 20–39 | Low | No action required |
| 0–19 | Minimal | Clean file |

---

## Heatmap Interpretation

The heatmap is most useful when read as a prioritization tool — not an indictment.
A file with a high risk score is not necessarily broken; it is where bugs are most
likely to be introduced and hardest to catch.

**Highest-value actions (risk-adjusted ROI):**
1. Add tests to Critical files — reduces coverage gap score immediately
2. Refactor functions with complexity > 25 — usually achievable in a small PR
3. Investigate high-churn + high-complexity files — often indicate architectural problems
4. Audit external packages in high-risk modules — dependency vulnerabilities amplify file risk

---

## Output: Risk Heatmap Table

```
Risk Heatmap
────────────
Repository: [name]
Period:     [analysis date range]

Rank | File                    | Risk  | Complexity | Churn | Coverage Gap
-----|-------------------------|-------|------------|-------|-------------
1    | [path/to/file.py]       | 91    | 100 (CC=28)| 85    | 80 (15%)
2    | [path/to/other.ts]      | 78    | 80 (CC=19) | 75    | 75 (30%)
...

Highest-Risk Modules (aggregate):
  [module/]: avg risk [score] across [N] files
```