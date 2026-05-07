# Integration Connectors

Used by `core/mcp-integrations/SKILL.md` to define the connector registration for each
supported external platform. All connectors must be registered with the Connector Hub
per `docs/schemas/connector-schema.yaml` before use.

---

## GitHub

```yaml
connector_id: github-api
connector_type: api
name: GitHub REST API
auth_method: api-key
endpoint: https://api.github.com
rate_limits:
  requests_per_minute: 60        # Unauthenticated: 10/min; token: 5000/hr → ~83/min
  requests_per_day: 5000
  burst_limit: 10
retry_policy:
  max_retries: 3
  backoff_strategy: exponential
  timeout_ms: 10000
capabilities: [read, write, search]
health_check: https://api.github.com/zen
audit_log: true
```

**Key operations:**
| Operation | Method | Path |
|---|---|---|
| Get repo | GET | `/repos/{owner}/{repo}` |
| List PRs | GET | `/repos/{owner}/{repo}/pulls` |
| Create PR | POST | `/repos/{owner}/{repo}/pulls` |
| Merge PR | PUT | `/repos/{owner}/{repo}/pulls/{pull_number}/merge` |
| Create issue | POST | `/repos/{owner}/{repo}/issues` |
| Trigger workflow | POST | `/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches` |
| Get run status | GET | `/repos/{owner}/{repo}/actions/runs/{run_id}` |

---

## Jira

```yaml
connector_id: jira-api
connector_type: api
name: Jira Cloud REST API
auth_method: api-key           # Basic auth: email:api_token as Base64
endpoint: https://{workspace}.atlassian.net/rest/api/3
rate_limits:
  requests_per_minute: 60
  requests_per_day: 10000
  burst_limit: 5
retry_policy:
  max_retries: 3
  backoff_strategy: exponential
  timeout_ms: 8000
capabilities: [read, write, search]
health_check: https://{workspace}.atlassian.net/rest/api/3/myself
audit_log: true
```

**Key operations:**
| Operation | Method | Path |
|---|---|---|
| Get issue | GET | `/issue/{issueIdOrKey}` |
| Create issue | POST | `/issue` |
| Update status | POST | `/issue/{issueIdOrKey}/transitions` |
| Add comment | POST | `/issue/{issueIdOrKey}/comment` |
| Search issues | GET | `/search?jql={jql}` |

---

## Linear

```yaml
connector_id: linear-api
connector_type: api
name: Linear GraphQL API
auth_method: api-key
endpoint: https://api.linear.app/graphql
rate_limits:
  requests_per_minute: 60
  requests_per_day: 5000
  burst_limit: 10
retry_policy:
  max_retries: 3
  backoff_strategy: exponential
  timeout_ms: 8000
capabilities: [read, write, search]
health_check: https://api.linear.app/graphql    # POST: {"query": "{ viewer { id } }"}
audit_log: true
```

---

## Slack

```yaml
connector_id: slack-api
connector_type: api
name: Slack Web API
auth_method: oauth2
endpoint: https://slack.com/api
rate_limits:
  requests_per_minute: 50       # Tier 3: 50/min for most methods
  requests_per_day: 0           # No daily limit
  burst_limit: 5
retry_policy:
  max_retries: 3
  backoff_strategy: exponential
  timeout_ms: 5000
capabilities: [read, write, subscribe]
health_check: https://slack.com/api/auth.test
audit_log: true
```

**Key operations:**
| Operation | Method | API Method |
|---|---|---|
| Post message | POST | `chat.postMessage` |
| Get channel history | GET | `conversations.history` |
| Create thread reply | POST | `chat.postMessage` (thread_ts) |
| List channels | GET | `conversations.list` |

---

## Sentry

```yaml
connector_id: sentry-api
connector_type: api
name: Sentry REST API
auth_method: api-key
endpoint: https://sentry.io/api/0
rate_limits:
  requests_per_minute: 100
  requests_per_day: 0
  burst_limit: 20
retry_policy:
  max_retries: 3
  backoff_strategy: linear
  timeout_ms: 8000
capabilities: [read]
health_check: https://sentry.io/api/0/
audit_log: true
```

---

## Datadog

```yaml
connector_id: datadog-api
connector_type: api
name: Datadog REST API
auth_method: api-key
endpoint: https://api.datadoghq.com/api/v2
rate_limits:
  requests_per_minute: 300
  requests_per_day: 0
  burst_limit: 30
retry_policy:
  max_retries: 3
  backoff_strategy: exponential
  timeout_ms: 10000
capabilities: [read, search]
health_check: https://api.datadoghq.com/api/v1/validate
audit_log: true
```

---

## Vercel

```yaml
connector_id: vercel-api
connector_type: api
name: Vercel REST API
auth_method: api-key
endpoint: https://api.vercel.com
rate_limits:
  requests_per_minute: 60
  requests_per_day: 0
  burst_limit: 10
retry_policy:
  max_retries: 2
  backoff_strategy: exponential
  timeout_ms: 30000
capabilities: [read, write, execute]
health_check: https://api.vercel.com/v1/user
audit_log: true
```

---

## Cloudflare

```yaml
connector_id: cloudflare-api
connector_type: api
name: Cloudflare REST API v4
auth_method: api-key
endpoint: https://api.cloudflare.com/client/v4
rate_limits:
  requests_per_minute: 1200
  requests_per_day: 0
  burst_limit: 50
retry_policy:
  max_retries: 3
  backoff_strategy: exponential
  timeout_ms: 10000
capabilities: [read, write]
health_check: https://api.cloudflare.com/client/v4/user/tokens/verify
audit_log: true
```