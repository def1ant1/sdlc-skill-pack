# Code Review Criteria

## Review Scope

Every pull request must be reviewed against all criteria in this document before merge.
Reviews produce findings in the format: `[SEVERITY] [CATEGORY] <description> (file:line)`.

Severity levels: `FAIL` (blocks merge) | `WARN` (must acknowledge) | `NOTE` (optional improvement)

---

## 1. Security (Category: SECURITY)

| Criterion | Severity | Description |
|---|---|---|
| Authentication bypass | FAIL | Code path reachable without required auth |
| SQL/NoSQL injection | FAIL | User input interpolated into query strings |
| XSS | FAIL | Unescaped user content rendered as HTML |
| Command injection | FAIL | User input passed to shell or exec |
| Hardcoded secrets | FAIL | Credentials, API keys, tokens in source |
| Insecure deserialization | FAIL | Untrusted data deserialized without validation |
| Missing input validation | FAIL | External input (user, API) not validated at boundary |
| Cryptographic weakness | FAIL | MD5/SHA1 for security; insecure random; hardcoded IV |
| Over-permissioned scope | WARN | Access granted beyond what feature requires |
| Missing rate limiting | WARN | New external-facing endpoint without rate limit |
| Verbose error exposure | WARN | Stack traces or internal paths in error responses |

---

## 2. Correctness (Category: CORRECTNESS)

| Criterion | Severity | Description |
|---|---|---|
| Logic error | FAIL | Code does not implement the specification |
| Off-by-one | FAIL | Incorrect boundary in loop, slice, or comparison |
| Null/nil dereference | FAIL | Unchecked nil access in non-optional path |
| Race condition | FAIL | Concurrent access to shared state without synchronization |
| Incorrect error handling | FAIL | Error silently swallowed; wrong error type returned |
| Missing edge case | WARN | Empty collection, zero value, max value not handled |
| Dead code | NOTE | Unreachable branches; unused variables |
| Incorrect algorithm | FAIL | Wrong data structure or algorithm for the use case |

---

## 3. Performance (Category: PERFORMANCE)

| Criterion | Severity | Description |
|---|---|---|
| N+1 query | FAIL | Query inside a loop that grows with data size |
| Missing index | WARN | Query on column with no index; verified via query plan |
| Unbounded result set | FAIL | DB or API query with no LIMIT on potentially large results |
| Blocking I/O in hot path | WARN | Synchronous network or disk call in request handler |
| Memory leak | FAIL | Resources allocated without corresponding release |
| Redundant computation | NOTE | Expensive calculation repeated where once suffices |

---

## 4. Test Coverage (Category: COVERAGE)

| Criterion | Severity | Description |
|---|---|---|
| No tests for new logic | FAIL | New business logic has zero test coverage |
| Missing edge case test | WARN | Happy path tested but not error, empty, or boundary |
| Flaky test introduced | FAIL | Test result depends on timing, order, or external state |
| Coverage below gate | FAIL | New code drops overall coverage below configured threshold |
| Test against implementation | WARN | Test asserts internal state instead of observable behavior |

---

## 5. Standards (Category: STANDARDS)

| Criterion | Severity | Description |
|---|---|---|
| Naming convention violated | WARN | File, function, or variable name does not follow project conventions |
| Commit message format | WARN | Conventional Commits format not followed |
| OpenAPI spec not updated | FAIL | New endpoint added without corresponding spec update |
| Missing migration | FAIL | Schema change without migration file |
| Environment variable undocumented | WARN | New env var not added to `.env.example` and docs |

---

## 6. Architecture (Category: ARCHITECTURE)

| Criterion | Severity | Description |
|---|---|---|
| Layer violation | FAIL | Business logic in handler; data access in domain |
| Circular dependency | FAIL | Package import cycle introduced |
| Interface not used | WARN | Concrete type used where interface should be (breaks testability) |
| Premature abstraction | NOTE | Utility created for a single use case |
| Cross-service data access | FAIL | Service reads another service's DB directly |

---

## Merge Gate Summary

| Condition | Decision |
|---|---|
| Any FAIL finding present | Block merge |
| 3+ WARN findings unacknowledged | Block merge |
| All FAILs resolved, WARNs acknowledged | Approve |
| NOTE findings only | Approve (no action required) |