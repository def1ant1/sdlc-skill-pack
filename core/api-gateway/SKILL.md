---
name: api-gateway
description: FastAPI-based HTTP/WebSocket gateway providing authentication, rate-limiting, tenant routing, and unified API surface for all Apotheon services.
metadata:
  version: "1.0.0"
  category: control-plane
  owner: platform-team
  maturity: beta
  dependencies:
    - sdlc-orchestration
    - sdlc-memory-token-management
---

# API Gateway Skill

## Purpose

The API Gateway is the single ingress point for all external and internal Apotheon API traffic. It handles:

- **Authentication** — JWT bearer token validation (HS256/RS256), API key verification
- **Authorization** — RBAC enforcement via `require_permission()` dependency
- **Tenant routing** — `org_id` ContextVar injection for all downstream handlers
- **Rate limiting** — per-org sliding window counters (Redis-backed)
- **WebSocket upgrades** — live run status streams at `/ws/runs/{run_id}`
- **Observability** — request latency histograms, error counters, OTel span injection

## Routes

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/v1/workflows` | `workflow:execute` | Submit workflow plan |
| GET | `/v1/workflows` | `workflow:read` | List runs for org |
| GET | `/v1/workflows/{id}` | `workflow:read` | Get run detail |
| POST | `/v1/approvals/{id}/decide` | `hitl:approve` | Approve/reject HITL gate |
| GET | `/v1/memory/search` | `memory:read` | Semantic memory search |
| GET | `/v1/governance/dashboard` | `governance:dashboard` | Policy violation metrics |
| POST | `/v1/cost/estimate` | `cost:estimate` | Pre-flight cost estimate |
| GET | `/metrics` | none (internal) | Prometheus scrape |
| GET | `/health` | none | Liveness probe |
| WS | `/ws/runs/{run_id}` | `workflow:read` | Live run updates |

## Authentication Flow

```
Client → Bearer <JWT>
Gateway → verify_token(jwt) → CurrentUser{user_id, org_id, role, permissions}
Gateway → inject into request.state.user
TenantMiddleware → populate ContextVars (current_org_id, current_user_id)
Handler → require_permission("action") → 403 if not authorized
```

## Rate Limiting

Limits enforced per `org_id`:
- `free` plan: 10 req/min per endpoint
- `starter`: 60 req/min
- `pro`: 300 req/min
- `enterprise`: unlimited

Exceeded limits return `429 Too Many Requests` with `Retry-After` header.

## WebSocket Protocol

Connect: `ws://<host>/ws/runs/{run_id}?token=<jwt>`

Messages (server → client, JSON):
```json
{"event": "step_complete", "step": 2, "skill": "architecture", "status": "completed"}
{"event": "hitl_gate", "step": 3, "skill": "devsecops", "risk_level": "HIGH"}
{"event": "workflow_complete", "run_id": "...", "status": "completed"}
{"event": "error", "detail": "..."}
```

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `JWT_SECRET` | required | HMAC signing secret |
| `JWT_ALGORITHM` | `HS256` | `HS256` or `RS256` |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `RATE_LIMIT_BACKEND` | `memory` | `memory` or `redis` |
| `REDIS_URL` | — | Redis URL for rate limiting |

## Integration Points

- **`app/auth/dependencies.py`** — `get_current_user()`, `require_permission()`
- **`app/middleware/tenant.py`** — ContextVar injection
- **`app/api/v1/*.py`** — domain routers mounted under `/v1`
- **`app/main.py`** — `create_app()` factory that wires all routers

## Error Responses

All errors follow RFC 7807 Problem Details:
```json
{
  "detail": "human-readable message",
  "type": "https://apotheon.dev/errors/unauthorized",
  "status": 401
}
```