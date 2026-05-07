# API Design Standards

## Core Principles

1. **OpenAPI-first**: Write the spec before writing code. The spec is the contract.
2. **Resource-oriented**: Design around resources (nouns), not actions (verbs).
3. **Stable contracts**: Never break a published contract without a versioned migration path.
4. **Explicit over implicit**: All inputs, outputs, and errors fully documented in the spec.

---

## URL Structure

```
/{version}/{resource}/{id}/{sub-resource}

Examples:
  GET    /v1/accounts
  POST   /v1/accounts
  GET    /v1/accounts/{account_id}
  PATCH  /v1/accounts/{account_id}
  DELETE /v1/accounts/{account_id}
  GET    /v1/accounts/{account_id}/invoices
  POST   /v1/accounts/{account_id}/invoices
```

**Rules**:
- `{version}` is `v1`, `v2`, etc. — always present
- Resource names are plural nouns in kebab-case: `user-profiles`, `api-keys`
- IDs are URL path parameters, not query strings
- Actions that don't map to CRUD use sub-resources: `POST /v1/invoices/{id}/send`

---

## HTTP Method Semantics

| Method | Semantics | Idempotent | Body |
|---|---|---|---|
| GET | Read resource(s) | Yes | None |
| POST | Create resource | No | Required |
| PUT | Replace resource fully | Yes | Required |
| PATCH | Update resource partially | No | Required (JSON Merge Patch or JSON Patch) |
| DELETE | Remove resource | Yes | None |

---

## Response Envelope

All responses use a consistent envelope:

```json
{
  "data": { ... },          // the resource or result
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601",
    "version": "v1"
  }
}
```

For collections:

```json
{
  "data": [ ... ],
  "meta": {
    "request_id": "uuid",
    "total": 1234,
    "page": 1,
    "page_size": 50,
    "next_cursor": "opaque-token"
  }
}
```

---

## Error Format

All errors use RFC 7807 (Problem Details):

```json
{
  "type": "https://errors.apotheon.ai/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/v1/accounts/req_abc123",
  "errors": [
    {"field": "email", "code": "invalid_format", "message": "..."}
  ]
}
```

---

## Standard HTTP Status Codes

| Code | When to Use |
|---|---|
| 200 OK | Successful GET, PATCH, or PUT |
| 201 Created | Successful POST that created a resource |
| 204 No Content | Successful DELETE or action with no response body |
| 400 Bad Request | Malformed request syntax |
| 401 Unauthorized | Missing or invalid auth token |
| 403 Forbidden | Valid auth but insufficient permissions |
| 404 Not Found | Resource does not exist |
| 409 Conflict | Resource state conflict (e.g., duplicate) |
| 422 Unprocessable | Valid syntax but business rule violation |
| 429 Too Many Requests | Rate limit exceeded; include `Retry-After` header |
| 500 Internal Server Error | Unexpected server error; never expose stack traces |

---

## Pagination

Use cursor-based pagination for all list endpoints:

```
GET /v1/accounts?page_size=50&cursor=<opaque>
```

- `page_size`: default 50, max 200
- `cursor`: opaque token; never expose page numbers or offsets
- Response includes `next_cursor`; omit if no more pages

---

## Versioning

- Major version in URL path (`/v1/`, `/v2/`)
- Minor/patch changes via `Accept-Version` header (optional, prefer URL versioning)
- Deprecation notice: `Deprecation` and `Sunset` headers; minimum 6-month deprecation window
- Breaking changes require a new major version

---

## Authentication & Authorization

- All endpoints: `Authorization: Bearer {token}` (OAuth2 / JWT)
- Token introspection via local-security skill
- Scope-based authorization: token must include required scope for each endpoint
- Service-to-service: mTLS + short-lived service tokens

---

## Rate Limits

| Tier | Requests/min | Burst |
|---|---|---|
| Free | 60 | 10 |
| Pro | 600 | 100 |
| Enterprise | 6,000 | 500 |
| Internal service | 10,000 | 1,000 |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`