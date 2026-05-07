# Test Pyramid

## Overview

The test pyramid defines the allocation of test types, coverage expectations, and
execution strategy. More tests at the base (unit); fewer at the top (E2E). Each
layer has a clear scope and must not substitute for layers below it.

```
          /\
         /E2E\          5%  — critical user journeys only
        /------\
       /  Perf  \       5%  — load, latency, throughput
      /----------\
     /  Contract  \     10% — service boundary contracts
    /--------------\
   / Integration    \   20% — cross-component, DB, queues
  /------------------\
 /   Unit Tests        \ 60% — business logic, pure functions
/----------------------\
```

---

## Layer Definitions

### Unit Tests (60%)

**Scope**: Single function, class, or module. No external dependencies — all I/O mocked.

**What to test**:
- All business logic branches
- Error handling paths
- Boundary values (empty, max, zero)
- Pure transformations and calculations

**What NOT to test**:
- Framework internals
- Database queries directly
- Third-party library behavior

**Speed target**: < 10ms per test. Full unit suite < 30s.

**Coverage gate**: 80% line coverage on `src/domain/` and `src/service/` packages.

---

### Integration Tests (20%)

**Scope**: Multiple components working together, including real DB, real message queue
(in Docker), but not external APIs.

**What to test**:
- Repository layer against real database
- Service layer with real dependencies wired
- Message producer → consumer flow
- Migration correctness (run against empty DB)

**Infrastructure**: Docker Compose with real Postgres, Redis, and queue broker.
Tests must be hermetic: clean up after themselves; never depend on execution order.

**Speed target**: Individual test < 2s. Full integration suite < 5 min.

---

### Contract Tests (10%)

**Scope**: Service boundaries. Consumer-driven contract tests (Pact or equivalent).

**What to test**:
- Every API endpoint: request schema, response schema, error shapes
- Every event schema a service produces or consumes
- Bi-directional: consumer defines expectations; provider verifies

**Gate**: New endpoint or event type → contract test required before merge.

---

### Performance Tests (5%)

**Scope**: Load, latency, and throughput under realistic conditions.

**What to test**:
- P95/P99 latency under target load (RPS per SLO)
- Throughput ceiling (max sustainable RPS before degradation)
- Resource consumption under load (CPU, memory, connection pool)

**Tools**: k6 or Locust. Tests defined as code; run in CI on merge to main.

**Thresholds** (from SLO):
- User-facing endpoints: P95 ≤ 500ms at 100% target RPS
- Internal APIs: P95 ≤ 200ms
- Background workers: throughput ≥ target RPS

---

### End-to-End Tests (5%)

**Scope**: Critical user journeys across the full stack (UI + API + DB).

**What to test** (only the most critical paths):
- Sign up → activate → first value moment
- Core transactional flow (purchase, submit, etc.)
- Auth: login, logout, token refresh, session expiry
- Critical error recovery (retry on failure, graceful degradation)

**Tools**: Playwright (web), Cypress (alternative), or custom API sequence tests.

**Speed target**: Full E2E suite < 15 min. Run on merge to main and pre-release.

---

## Coverage Gates

| Package Type | Coverage Gate | Enforcement |
|---|---|---|
| Domain / business logic | ≥ 80% line | CI blocks merge below gate |
| Service / orchestration | ≥ 75% line | CI blocks merge below gate |
| Repository / data access | ≥ 70% line | CI blocks merge below gate |
| Handler / adapter | ≥ 60% line | CI warns; does not block |
| Generated code | Excluded | No gate |

---

## Test Data Management

- Unit tests: hard-coded minimal fixtures
- Integration tests: seeded via migration-compatible fixtures; rolled back after test
- E2E tests: dedicated test tenant/account; never test against production data
- PII in test data: always synthetic; never copy from production
- Fixtures are code-reviewed like production code