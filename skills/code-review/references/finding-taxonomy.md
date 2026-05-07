# Finding Taxonomy

## Finding Format

```
[SEVERITY] [CATEGORY] Description of the issue. (path/to/file.ext:line_number)

Explanation: Why this is a problem and what harm it causes.
Recommendation: Concrete fix with example if applicable.
References: Link to standard, policy, or documentation.
```

---

## Severity Definitions

### FAIL — Blocks Merge

The code cannot be merged in its current state. The reviewer must provide:
- Clear description of the violation
- Specific recommendation for the fix
- Reference to the rule being violated

Examples:
```
[FAIL] [SECURITY] User input passed directly to SQL query. (src/db/accounts.go:47)
Explanation: String interpolation in query allows SQL injection; an attacker can
  exfiltrate or modify any data in the database.
Recommendation: Use parameterized queries: db.Query("SELECT ... WHERE id = ?", id)
References: OWASP Top 10 A03:2021, api-design-standards.md §Auth
```

### WARN — Must Acknowledge

The code may merge if the author explicitly acknowledges the finding and either:
(a) commits to fixing it in the same sprint, or
(b) documents why it is acceptable in this context.

```
[WARN] [PERFORMANCE] Query inside loop will produce N+1 queries as account list grows. (src/service/invoice.go:112)
Explanation: Fetching invoice count per account in a loop; with 1,000 accounts this
  produces 1,001 DB calls.
Recommendation: Batch query: SELECT account_id, COUNT(*) FROM invoices GROUP BY account_id
  then join in memory.
```

### NOTE — Optional Improvement

Informational; no action required. May be silently closed or addressed in a future PR.

```
[NOTE] [STANDARDS] This helper function is only used in one place; consider inlining
  to reduce indirection. (src/util/format.go:23)
```

---

## Category Reference

| Code | Category | Scope |
|---|---|---|
| SECURITY | Security | Auth, injection, secrets, crypto, input validation |
| CORRECTNESS | Correctness | Logic, error handling, null safety, race conditions |
| PERFORMANCE | Performance | Queries, memory, computation, I/O |
| COVERAGE | Test Coverage | Missing tests, flaky tests, coverage drops |
| STANDARDS | Standards | Naming, format, documentation, conventions |
| ARCHITECTURE | Architecture | Layering, dependencies, coupling, design |

---

## Finding Quality Standards

A high-quality finding is:

1. **Specific**: Names the exact file and line number
2. **Explained**: States the harm or risk, not just the rule violated
3. **Actionable**: Provides a concrete recommendation or example fix
4. **Referenced**: Links to the relevant standard, policy, or documentation

A low-quality finding that violates these standards may be escalated to the reviewer
for revision before the author is expected to act on it.

---

## Response Protocol for Authors

| Finding Type | Required Author Response |
|---|---|
| FAIL | Fix the issue; update PR; request re-review |
| WARN | Acknowledge in PR comment with fix plan or justification; reviewer must sign off |
| NOTE | Optional; may close with `noted, no action` or address the suggestion |

---

## Escalation

If author and reviewer disagree on a finding's severity:

1. Tag a third reviewer (senior engineer or tech lead)
2. Third reviewer's classification is final
3. If still unresolved: escalate to Architecture Review Board
4. All FAIL-level security findings require security skill sign-off before override

---

## Common Patterns by Category

### SECURITY — Frequently Missed

- JWT decoded without signature verification
- Authorization checked on resource collection but not individual resource
- File path traversal (`../`) not prevented
- CORS wildcard (`*`) on authenticated endpoints
- Logging user-controlled input (log injection risk)

### CORRECTNESS — Frequently Missed

- Error from goroutine not propagated
- Context cancellation not checked in long loops
- Integer overflow in count multiplication
- Slice mutation in returned value (caller unexpectedly sees change)

### PERFORMANCE — Frequently Missed

- `SELECT *` instead of selecting required columns
- Missing `LIMIT` on list endpoint query
- Synchronous HTTP call without timeout
- Large slice/map copied by value across function boundary