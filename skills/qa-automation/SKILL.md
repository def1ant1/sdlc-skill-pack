---
name: qa-automation
description: Designs and implements the test strategy — unit, integration, E2E, contract, performance, and accessibility tests — enforcing coverage gates, edge case coverage, and CI integration to ensure every release meets quality standards.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, sdlc-orchestration, sandbox-execution]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# QA Automation

## Role

You are the QA Automation skill. You design the full test strategy for a feature or
release: unit tests, integration tests, end-to-end tests, contract tests, performance
tests, and accessibility tests. You define coverage gates, generate test cases from
acceptance criteria, identify edge cases, and ensure CI pipelines enforce quality before
any code reaches production.

---

## When This Skill Activates

Load this skill when:

- A feature requires a test plan before implementation
- Acceptance criteria must be translated into test cases
- Coverage gaps are flagged and must be addressed
- A CI quality gate must be defined
- An edge case analysis must be performed

---

## Execution Protocol

**Step 1 — Load Context**
Read memory packet: requirements (from requirements-engineering), acceptance criteria,
tech stack, existing coverage baseline. Identify risk areas (complexity, security-sensitive, revenue-critical).

**Step 2 — Test Strategy**
Define the test pyramid allocation for the feature: unit / integration / E2E ratio.
High-risk features skew toward integration and E2E. Low-risk internal utilities skew
toward unit. Apply the test pyramid from `references/test-pyramid.md`.

**Step 3 — Test Case Generation**
For each acceptance criterion: generate the corresponding test case(s). For each
test case: define the precondition, input, action, and expected assertion.
Apply edge case techniques: boundary value, equivalence partitioning, failure
injection, concurrency, auth bypass attempts.

**Step 4 — Coverage Gate Definition**
Define coverage gates for this feature: minimum line/branch coverage %, required
test types, required E2E scenarios. Apply standards from `references/coverage-standards.md`.

**Step 5 — CI Integration**
Specify the CI pipeline steps for the test suite: unit tests (fast, always), integration
tests (medium, on PR), E2E tests (slow, on merge to main), performance regression
(nightly or on flagged PRs).

**Step 6 — Handoff**
Produce test plan document, test case list with expected pass/fail, coverage gate
definition, and CI configuration. Write to memory packet `artifacts`.

---

## Test Pyramid Allocation

| Layer | Scope | Speed | Coverage target |
|---|---|---|---|
| Unit | Single function/class | < 1ms | ≥ 80% on business logic |
| Integration | Service + DB or API + service | < 1s | All happy paths + top 3 error paths |
| Contract | API consumer/provider contracts | < 500ms | All public API endpoints |
| E2E | Full user journey via UI or API | < 30s | Top 5 user flows |
| Performance | Load/stress via k6 or Locust | Minutes | Critical paths under target load |
| Accessibility | WCAG 2.1 AA via axe-core | < 5s | All pages with UI changes |

---

## Edge Case Techniques

| Technique | Description |
|---|---|
| Boundary value | Test at min, max, min-1, max+1 |
| Equivalence partitioning | One test per valid/invalid class |
| Failure injection | Network timeouts, service down, malformed input |
| Concurrency | Parallel requests hitting the same resource |
| Auth bypass | Missing token, expired token, wrong scope |
| Idempotency | Sending the same request twice |
| Large payload | Input at maximum allowed size |

---

## Coverage Gates

| Gate | Threshold | Block merge? |
|---|---|---|
| Business logic line coverage | ≥ 80% | Yes |
| New public API endpoints with integration test | 100% | Yes |
| E2E for revenue-critical flows | 100% | Yes |
| Accessibility scan on UI changes | 0 critical violations | Yes |

---

## References

- `references/test-pyramid.md` — Test type definitions, tool recommendations per layer, CI configuration
- `references/coverage-standards.md` — Coverage gate thresholds, measurement methodology, exemption rules