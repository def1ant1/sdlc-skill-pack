---
name: enterprise-integration-hub
description: Provides ERP/CRM/ITSM/HRIS connector framework with bidirectional sync, event streaming, and enterprise authentication for the sovereign AI platform.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['connector-hub', 'event-bus', 'governance']

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

## Role

Central integration layer between the Enterprise OS and external enterprise systems of record.
Manages authenticated connections, bidirectional data sync, event streaming, and webhook
ingestion for ERP (SAP/Oracle), CRM (Salesforce/HubSpot), ITSM (ServiceNow/Jira SM),
and HRIS systems. All enterprise data flowing into the platform passes through this hub
for governance, rate limiting, and audit logging.

## Activation Triggers

- A domain skill requests data from an enterprise system (ERP, CRM, ITSM)
- A persistent agent requires system-of-record data for its standing mandate evaluation
- An enterprise system publishes a webhook event (new deal, incident, contract, hire)
- A bidirectional sync job is due (scheduled or triggered by data change event)
- `governance` requests an audit of enterprise data access patterns
- A connection credential is due for rotation (secrets management schedule)

## Execution Protocol

1. **Connection registry**: Maintain a registry of all enterprise system connections:
   - System type, base URL, auth method (OAuth2, API key, mTLS, SAML)
   - Rate limit budget (requests/minute, daily quota)
   - Data classification for data returned by this system
   - Last successful health check timestamp

2. **Request routing**: On a data request from a domain skill:
   a. Resolve the target system from the request's `system_type` and `entity_type`
   b. Check caller authorization via `zero-trust-runtime`
   c. Apply rate limit check; queue if budget exhausted
   d. Translate the platform's canonical query to the system-specific API call
   e. Cache cacheable responses per the cache TTL policy for this system type

3. **Webhook ingestion**: Receive inbound webhook events from enterprise systems.
   Validate HMAC signatures. Normalize to the platform's canonical event schema.
   Publish to `event-bus` with `source: erp | crm | itsm | hris` tag.

4. **Bidirectional sync**: For write-back operations (creating records in enterprise systems):
   a. Validate the write payload against the target system's field schema
   b. Apply duplicate detection (check if record already exists)
   c. Submit write with idempotency key
   d. Confirm success; update sync state

5. **Audit logging**: Log every read and write with: caller, system, entity_type,
   operation, timestamp, record_count. Feed to compliance evidence collection.

## Output Format

```yaml
integration_result:
  operation: read | write | webhook_ingest | sync
  system: erp | crm | itsm | hris
  entity_type: "opportunity" | "incident" | "invoice" | "employee"
  status: success | rate_limited | auth_failed | system_unavailable
  record_count: 0
  cache_hit: false
  latency_ms: 0
  audit_ref: "EIH-OPS-2026-xxxxx"
```

## References

- `references/` — Connector catalog, canonical entity schema, rate limit policy, webhook signature validation
