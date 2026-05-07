# Connector Contract

Used by `core/connector-hub/SKILL.md` to define the interface every connector must implement,
validation rules, lifecycle states, and canonical error codes.

---

## Connector Types

| Type | Description | Examples | Auth Methods |
|---|---|---|---|
| `api` | External REST or GraphQL API | GitHub API, Stripe, Slack, SendGrid | api-key, oauth2, jwt, mtls |
| `database` | Relational, key-value, or vector database | Postgres, Redis, Qdrant, Neo4j, ClickHouse | credentials, connection-string |
| `mcp` | MCP tool or resource server | Claude Code MCP servers, local tool servers | mcp-auth, local-socket, none |
| `cloud` | Cloud object storage or managed services | S3, GCS, Azure Blob, Cloudflare R2 | iam, oauth2, api-key |
| `local` | Local runtime services and APIs | Ollama REST, DGX Spark APIs, local SQLite | none, path-based |
| `filesystem` | Local filesystem read/write operations | config files, output dirs, asset stores | path-permissions |

---

## Required Contract Fields

Every connector definition MUST include all of the following fields:

| Field | Type | Description |
|---|---|---|
| `connector_id` | string (kebab-case) | Unique identifier; must match `^[a-z0-9]+(-[a-z0-9]+)*$` |
| `connector_type` | enum | One of: `api`, `database`, `mcp`, `cloud`, `local`, `filesystem` |
| `name` | string | Human-readable display name |
| `description` | string (≤500 chars) | What this connector connects to and what it is used for |
| `auth_method` | enum | One of: `none`, `api-key`, `oauth2`, `jwt`, `mtls`, `iam`, `credentials`, `path-based` |
| `endpoint` | string | Base URL, connection string, file path, or socket path |
| `rate_limits` | object | See Rate Limits sub-fields below |
| `retry_policy` | object | See Retry Policy sub-fields below |
| `capabilities` | string[] | Operations supported: one or more of `read`, `write`, `search`, `stream`, `subscribe`, `execute` |
| `health_check` | string | URL, command, or query to verify connectivity |
| `audit_log` | boolean | Whether to log all interactions (required `true` for all `database` and `api` types) |

### Rate Limits Sub-Fields

| Field | Type | Description |
|---|---|---|
| `requests_per_minute` | integer | Max requests per minute (0 = unlimited) |
| `requests_per_day` | integer | Max requests per day (0 = unlimited) |
| `burst_limit` | integer | Max concurrent in-flight requests |

### Retry Policy Sub-Fields

| Field | Type | Description |
|---|---|---|
| `max_retries` | integer | Maximum retry attempts on failure (0–10) |
| `backoff_strategy` | enum | One of: `linear`, `exponential`, `none` |
| `timeout_ms` | integer | Request timeout in milliseconds |

---

## Validation Rules

| Rule ID | Field | Rule | Failure Action |
|---|---|---|---|
| CV-001 | `connector_id` | Must match `^[a-z0-9]+(-[a-z0-9]+)*$` | Reject registration |
| CV-002 | `connector_id` | Must be unique across all registered connectors | Reject registration |
| CV-003 | `connector_type` | Must be one of the 6 defined types | Reject registration |
| CV-004 | `auth_method` | Must be compatible with `connector_type` (see table below) | Reject registration |
| CV-005 | `endpoint` | Must be non-empty; URL connectors must start with `http://` or `https://` | Reject registration |
| CV-006 | `rate_limits` | All three sub-fields required; integers ≥ 0 | Reject registration |
| CV-007 | `retry_policy` | All three sub-fields required; `max_retries` 0–10 | Reject registration |
| CV-008 | `capabilities` | At least one capability required; all values must be from allowed set | Reject registration |
| CV-009 | `audit_log` | Must be `true` for `api` and `database` connector types | Reject registration |
| CV-010 | `health_check` | Must be non-empty | Warn; allow registration |
| CV-011 | `description` | Must be ≤ 500 characters | Reject registration |

### Auth Method Compatibility

| Connector Type | Allowed Auth Methods |
|---|---|
| `api` | api-key, oauth2, jwt, mtls, none |
| `database` | credentials, connection-string |
| `mcp` | mcp-auth, local-socket, none |
| `cloud` | iam, oauth2, api-key |
| `local` | none, path-based |
| `filesystem` | path-permissions, none |

---

## Connector Lifecycle

| State | Description | Transitions |
|---|---|---|
| `registered` | Definition submitted; not yet validated | → validated (on validation pass), → rejected (on validation fail) |
| `validated` | Contract checks passed; not yet used | → active (first successful request) |
| `active` | In use; health check passing | → degraded (3 consecutive failures) |
| `degraded` | 3+ consecutive failures; requests queued | → active (recovery), → retired (manual) |
| `retired` | Decommissioned; all requests rejected | Terminal state |

---

## Error Codes

| Code | Name | Description | Retry? |
|---|---|---|---|
| CONN-001 | `auth_failure` | Authentication rejected by target system | No — fix credentials |
| CONN-002 | `rate_limited` | Request exceeded rate limit | Yes — after backoff |
| CONN-003 | `timeout` | Request exceeded `timeout_ms` | Yes — up to `max_retries` |
| CONN-004 | `connection_refused` | Target host refused connection | Yes — exponential backoff |
| CONN-005 | `not_found` | Resource does not exist at target | No — log and surface |
| CONN-006 | `permission_denied` | Authenticated but not authorized | No — escalate |
| CONN-007 | `validation_failed` | Connector definition failed contract validation | No — fix definition |
| CONN-008 | `degraded_state` | Connector is in `degraded` state; request queued | Auto-retry on recovery |
| CONN-009 | `schema_mismatch` | Response schema does not match declared contract | No — alert and log |
| CONN-010 | `health_check_failed` | Health check returned non-OK status | Trigger degraded transition |