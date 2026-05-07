# Complexity Scoring

## Cyclomatic Complexity

Cyclomatic complexity measures the number of independent paths through source code.
Computed per function/method.

**Formula**: `CC = E - N + 2P`
Where E = edges in control flow graph, N = nodes, P = connected components.

| CC Score | Complexity | Risk | Action |
|---|---|---|---|
| 1–5 | Low | Low | No action |
| 6–10 | Moderate | Low-Medium | Document logic |
| 11–15 | High | Medium | Refactor recommended |
| 16–25 | Very High | High | Refactor required before review |
| > 25 | Critical | Critical | Block merge; must decompose |

**Thresholds by context**:
- New code: CC must be ≤ 15 to merge
- Existing code: CC > 25 creates a P2 tech debt item
- Test code: CC up to 20 acceptable (test logic is legitimately complex)

---

## Cognitive Complexity

Cognitive complexity measures how difficult code is to understand. Unlike cyclomatic
complexity, it penalizes nesting more than linear sequences.

Tools: `sonar-scanner`, `lizard`, or `semgrep` with cognitive complexity rules.

| Cognitive CC | Label | Action |
|---|---|---|
| 0–10 | Simple | No action |
| 11–20 | Manageable | Add documentation |
| 21–35 | Difficult | Refactor recommended |
| > 35 | Very difficult | Block merge |

---

## File-Level Complexity

| Metric | Threshold | Action |
|---|---|---|
| Lines of code per file | > 500 LOC | Consider splitting |
| Functions per file | > 20 | Consider splitting |
| Number of imports/deps | > 15 | Review coupling |
| Max nesting depth | > 4 | Refactor nested logic |

---

## Complexity Trend Monitoring

Track per-service weekly:

```
SERVICE: account-service — Complexity Report (Week of YYYY-MM-DD)
================================================================
Functions above CC threshold (> 15): N
  - service/invoice.go:ProcessInvoice: CC=23 [HIGH]
  - domain/account.go:ValidateTransfer: CC=18 [HIGH]

Average CC (all functions): X.X
Average cognitive CC: X.X
Files above 500 LOC: N

TREND: [Improving | Stable | Degrading]
  CC avg: X.X (was X.X last week, X.X 4 weeks ago)
```

---

## Complexity-to-Coverage Correlation

Files with high complexity require higher test coverage:

| CC Score | Required Coverage |
|---|---|
| ≤ 5 | ≥ 70% |
| 6–10 | ≥ 80% |
| 11–15 | ≥ 90% |
| > 15 | ≥ 95% (or refactor) |

This ensures that complex code is thoroughly tested even if the overall coverage
target would not require it.