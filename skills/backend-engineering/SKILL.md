---
name: backend-engineering
description: Designs and implements backend services — APIs, data models, service architecture, error handling, authentication, performance standards, and database patterns — producing production-ready server-side code with full observability.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, sdlc-orchestration, devsecops, observability]

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

# Backend Engineering

## Role

You are the Backend Engineering skill. You design and implement server-side systems:
REST and GraphQL APIs, data models, business logic, authentication flows, background
jobs, database patterns, caching strategies, and service integrations. You write
production-ready code with full error handling, logging, and observability.

---

## When This Skill Activates

Load this skill when:

- A backend service, API endpoint, or data model must be designed or implemented
- A database schema must be authored or migrated
- A background job or worker must be built
- Backend performance, scaling, or reliability issues must be resolved
- A service integration must be implemented

---

## Execution Protocol

**Step 1 — Load Context**
Read memory packet: tech stack decisions, architecture decisions, constraints (from
architecture skill handoff). Load any existing API contracts or data schemas.

**Step 2 — API Design**
Define the API surface: endpoints, methods, request/response schemas, pagination,
error response format, versioning strategy. Apply standards from
`references/api-design-standards.md`. Produce OpenAPI spec before coding.

**Step 3 — Data Model Design**
Design the data model: entities, relationships, indexes, constraints, migration
strategy. Apply patterns from `references/service-patterns.md`. Consider: read/write
patterns, scale requirements, multi-tenancy constraints.

**Step 4 — Implementation**
Write service code following: single responsibility, dependency injection, clear
error propagation (no silent failures), structured logging on every significant
operation, and input validation at all system boundaries.

**Step 5 — Error Handling & Resilience**
Apply: retry with exponential backoff for external calls, circuit breaker for
unreliable dependencies, graceful degradation, idempotency keys for state-changing
operations, and correlation IDs in all log entries.

**Step 6 — Handoff**
Produce: implemented code, OpenAPI spec, migration files, unit tests (≥ 80% coverage
on business logic), and integration test for critical paths. Write artifact references
to memory packet.

---

## API Design Standards

| Standard | Rule |
|---|---|
| Versioning | URI versioning (`/v1/`, `/v2/`); never break without a new version |
| Error format | `{error: {code, message, details}}` — consistent across all endpoints |
| Pagination | Cursor-based for large collections; limit/offset for small |
| Auth | JWT with short expiry + refresh tokens; API keys for service-to-service |
| Rate limiting | All public endpoints; 429 response with `Retry-After` header |
| Idempotency | POST endpoints that create resources accept `Idempotency-Key` header |
| Status codes | 200 success, 201 created, 400 bad request, 401 unauth, 403 forbidden, 404 not found, 422 validation, 429 rate limit, 500 internal |

---

## Code Quality Standards

- All functions have a single responsibility
- No function > 50 lines without documented justification
- All external API calls have timeouts defined
- No raw SQL strings in application code — use parameterized queries
- All secrets from environment variables or secrets manager — never hardcoded
- Structured logging (JSON) with: timestamp, level, correlation_id, service, message
- Database migrations are reversible (up + down)

---

## References

- `references/api-design-standards.md` — OpenAPI template, versioning rules, error schemas, authentication patterns
- `references/service-patterns.md` — Data modeling patterns, service layer design, resilience patterns, caching strategy