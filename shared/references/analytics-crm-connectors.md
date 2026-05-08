# Analytics, CRM & Customer Platform Connectors

This document defines connector specifications for analytics, CRM, and customer
platform integrations referenced by GTM skills. Each entry covers authentication,
base URL, rate limits, retry policy, health check, and key operations.

---

## Google Analytics 4 (GA4)

| Field | Value |
|-------|-------|
| Auth | OAuth 2.0 (service account JSON key) or API key |
| Base URL | `https://analyticsdata.googleapis.com/v1beta` |
| Secret name | `ga4-service-account-key` |
| Rate limit | 10 requests/second per property |
| Retry policy | Exponential backoff; max 5 retries; retry on 429, 503 |
| Health check | `GET /properties/{propertyId}/metadata` → 200 |

### Key Operations

```yaml
operations:
  run_report:
    method: POST
    path: /properties/{propertyId}:runReport
    description: Query GA4 event data with date ranges, dimensions, metrics
    required_params: [dateRanges, dimensions, metrics]

  run_realtime_report:
    method: POST
    path: /properties/{propertyId}:runRealtimeReport
    description: Active users and events in last 30 minutes

  batch_run_reports:
    method: POST
    path: /properties/{propertyId}:batchRunReports
    description: Run up to 5 reports in a single request

  list_custom_dimensions:
    method: GET
    path: /properties/{propertyId}/customDimensions
    description: List all registered custom dimensions
```

### Cache TTL Policy

| Operation | Cache TTL |
|-----------|----------|
| Daily aggregates | 6 hours |
| Realtime reports | No cache (live only) |
| Property metadata | 24 hours |

---

## Mixpanel

| Field | Value |
|-------|-------|
| Auth | Service account credentials (username + secret) via HTTP Basic |
| Base URL (query) | `https://data.mixpanel.com/api/2.0` |
| Base URL (ingestion) | `https://api.mixpanel.com` |
| Secret name | `mixpanel-service-account` |
| Rate limit | 60 requests/minute (query API) |
| Retry policy | Exponential backoff; max 3 retries; retry on 429 |
| Health check | `GET /engage?where=1==1&limit=1` → 200 |

### Key Operations

```yaml
operations:
  query_jql:
    method: POST
    path: /jql
    description: JQL query for event sequences, funnel steps, cohort analysis

  get_funnels:
    method: GET
    path: /funnels
    description: Retrieve saved funnel conversion rates

  export_events:
    method: GET
    path: /export
    description: Raw event export (NDJSON) for date range
    rate_limit_note: "Large exports should use async export API"

  track_event:
    method: POST
    path: https://api.mixpanel.com/track
    description: Ingest a single event

  identify_user:
    method: POST
    path: https://api.mixpanel.com/engage
    description: Set or update user profile properties
```

---

## Amplitude

| Field | Value |
|-------|-------|
| Auth | API key + Secret key (HTTP Basic: api_key:secret_key) |
| Base URL | `https://amplitude.com/api/2` |
| Secret name | `amplitude-api-credentials` |
| Rate limit | 360 requests/hour (standard); burst: 18/minute |
| Retry policy | Exponential backoff; max 3 retries; retry on 429, 524 |
| Health check | `GET /events/list` → 200 |

### Key Operations

```yaml
operations:
  query_events:
    method: GET
    path: /events/segmentation
    description: Query event counts and properties over time

  get_funnels:
    method: GET
    path: /funnels
    description: Retrieve funnel conversion data

  get_cohort:
    method: GET
    path: /cohorts/list
    description: List defined cohorts

  export_events:
    method: GET
    path: /export
    description: Download raw event data as gzipped NDJSON

  get_user:
    method: GET
    path: /usersearch
    description: Look up user properties by user_id or device_id
```

---

## Segment (Twilio)

| Field | Value |
|-------|-------|
| Auth (write) | Write key in Authorization header: `Basic {base64(write_key:)}` |
| Auth (read/config) | Personal Access Token (PAT) via Bearer token |
| Base URL (tracking) | `https://api.segment.io/v1` |
| Base URL (config) | `https://api.segmentapis.com` |
| Secret name | `segment-write-key`, `segment-pat` |
| Rate limit | 500 req/s (tracking); 100 req/min (config API) |
| Retry policy | Exponential backoff; max 5 retries; retry on 429, 5xx |
| Health check | `POST /track` with test event → 200 |

### Key Operations

```yaml
operations:
  track:
    method: POST
    path: /track
    description: Record an event with properties

  identify:
    method: POST
    path: /identify
    description: Associate a user with a user_id and traits

  group:
    method: POST
    path: /group
    description: Associate a user with an account/company

  page:
    method: POST
    path: /page
    description: Record a page view

  list_sources:
    method: GET
    path: https://api.segmentapis.com/sources
    description: List all Segment sources (config API)
```

---

## Intercom

| Field | Value |
|-------|-------|
| Auth | Bearer token (access token from OAuth app) |
| Base URL | `https://api.intercom.io` |
| Secret name | `intercom-access-token` |
| Rate limit | 1,000 requests/minute (standard plan) |
| Retry policy | Exponential backoff; max 3 retries; retry on 429 |
| Health check | `GET /me` → 200 |
| Webhook validation | HMAC-SHA256 on `X-Hub-Signature` header |

### Key Operations

```yaml
operations:
  list_conversations:
    method: GET
    path: /conversations
    description: List conversations with filtering by state, assignee, tag

  create_conversation:
    method: POST
    path: /conversations
    description: Create a new inbound message

  reply_conversation:
    method: POST
    path: /conversations/{id}/reply
    description: Add a reply to an existing conversation

  get_contact:
    method: GET
    path: /contacts/{id}
    description: Get contact details and custom attributes

  update_contact:
    method: PUT
    path: /contacts/{id}
    description: Update contact attributes (health_score, lifecycle_stage, etc.)

  create_note:
    method: POST
    path: /notes
    description: Add internal note to a contact or conversation

  list_tags:
    method: GET
    path: /tags
    description: List all tags for segmentation
```

---

## Zendesk

| Field | Value |
|-------|-------|
| Auth | API token via HTTP Basic (`{email}/token:{api_token}`) or OAuth 2.0 |
| Base URL | `https://{subdomain}.zendesk.com/api/v2` |
| Secret name | `zendesk-api-token`, `zendesk-subdomain` |
| Rate limit | 700 requests/minute (Enterprise); 200/min (Professional) |
| Retry policy | Exponential backoff; max 5 retries; retry on 429; respect `Retry-After` header |
| Health check | `GET /tickets/count.json` → 200 |

### Key Operations

```yaml
operations:
  list_tickets:
    method: GET
    path: /tickets.json
    description: List tickets with filtering by status, assignee, created_at

  get_ticket:
    method: GET
    path: /tickets/{id}.json
    description: Get full ticket details including comments

  create_ticket:
    method: POST
    path: /tickets.json
    description: Create a new support ticket

  update_ticket:
    method: PUT
    path: /tickets/{id}.json
    description: Update ticket status, priority, assignee, tags

  search_tickets:
    method: GET
    path: /search.json?query=type:ticket+{query}
    description: Full-text search across tickets

  bulk_export:
    method: GET
    path: /incremental/tickets.json?start_time={unix_ts}
    description: Incremental export of all tickets since timestamp (cursor-based)
```

---

## HubSpot

| Field | Value |
|-------|-------|
| Auth | Private App token (Bearer) or OAuth 2.0 |
| Base URL | `https://api.hubapi.com` |
| Secret name | `hubspot-private-app-token` |
| Rate limit | 100 requests/10 seconds (standard); 150/10s (Enterprise) |
| Retry policy | Exponential backoff; max 3 retries; retry on 429, 502, 503 |
| Health check | `GET /crm/v3/objects/contacts?limit=1` → 200 |

### Key Operations

```yaml
operations:
  list_contacts:
    method: GET
    path: /crm/v3/objects/contacts
    description: List contacts with property filtering

  create_contact:
    method: POST
    path: /crm/v3/objects/contacts
    description: Create a new contact record

  update_contact:
    method: PATCH
    path: /crm/v3/objects/contacts/{id}
    description: Update contact properties

  list_deals:
    method: GET
    path: /crm/v3/objects/deals
    description: List deals with stage and amount filtering

  search_objects:
    method: POST
    path: /crm/v3/objects/{objectType}/search
    description: Advanced filter-based search for any CRM object type

  get_pipeline:
    method: GET
    path: /crm/v3/pipelines/deals
    description: List deal pipeline stages and their IDs
```

---

## Stripe

| Field | Value |
|-------|-------|
| Auth | API key via Bearer token |
| Base URL | `https://api.stripe.com/v1` |
| Secret name | `stripe-secret-key` |
| Rate limit | 100 requests/second (live mode) |
| Retry policy | Idempotency keys required; retry on network errors, 5xx; do NOT retry on 4xx |
| Health check | `GET /customers?limit=1` → 200 |
| Webhook validation | `Stripe-Signature` header; HMAC-SHA256 with webhook secret |

### Key Operations

```yaml
operations:
  list_subscriptions:
    method: GET
    path: /subscriptions
    description: List active subscriptions with MRR data

  get_mrr_metrics:
    method: GET
    path: /reporting/revenue_recognition/reporting_items
    description: Revenue recognition line items for ARR/MRR calculation

  list_invoices:
    method: GET
    path: /invoices
    description: List invoices for reconciliation with ERP

  retrieve_customer:
    method: GET
    path: /customers/{id}
    description: Get customer with payment method and subscription status

  create_billing_portal_session:
    method: POST
    path: /billing_portal/sessions
    description: Generate customer billing portal URL for self-service
```

---

## PostHog

| Field | Value |
|-------|-------|
| Auth | Personal API key via Authorization header |
| Base URL | `https://app.posthog.com` (cloud) or self-hosted |
| Secret name | `posthog-api-key`, `posthog-project-id` |
| Rate limit | 240 requests/minute |
| Retry policy | Exponential backoff; max 3 retries; retry on 429 |
| Health check | `GET /api/projects/{id}/` → 200 |

### Key Operations

```yaml
operations:
  query_events:
    method: POST
    path: /api/projects/{id}/query
    description: HogQL query for event analysis

  get_feature_flags:
    method: GET
    path: /api/projects/{id}/feature_flags
    description: List all feature flags and rollout conditions

  get_funnel:
    method: POST
    path: /api/projects/{id}/insights/funnel
    description: Compute funnel conversion rates

  get_persons:
    method: GET
    path: /api/projects/{id}/persons
    description: List user profiles with properties and cohort membership

  capture_event:
    method: POST
    path: https://app.posthog.com/capture/
    description: Ingest an event (server-side)
```

---

## Common Connector Patterns

### Rate Limit Handling

All connectors implement token-bucket rate limiting:

```python
# Pseudo-code — see scripts/connectors/rate_limiter.py for implementation
class RateLimiter:
    def acquire(self, connector_id: str, cost: int = 1) -> None:
        """Block until a request token is available."""
        ...
    def handle_429(self, retry_after_seconds: int) -> None:
        """Drain tokens and sleep."""
        ...
```

### Retry Policy

Standard retry: `initial=1s`, `multiplier=2`, `max_interval=60s`, `max_attempts=5`.
Do not retry on: 400, 401, 403, 404, 422 (client errors — fix the request).
Always retry on: 429 (rate limit), 502, 503, 504 (transient server errors).

### Secret Resolution Order

1. HashiCorp Vault path: `secret/connectors/{secret_name}`
2. Environment variable: `APOTHEON_{SECRET_NAME_UPPER}`
3. Local `.env` file (development only; never committed)