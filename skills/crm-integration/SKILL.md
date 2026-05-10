---
name: crm-integration
description: Manages Salesforce/HubSpot pipeline data, contact synchronization, and opportunity analysis via the enterprise-integration-hub.
metadata:
  version: "0.1.0"
  category: connectivity
  owner: platform
  maturity: draft
  dependencies: ['enterprise-integration-hub']

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

CRM integration skill. Provides high-level pipeline management, contact sync, and
opportunity analytics on top of `enterprise-integration-hub` for Salesforce and HubSpot.
Enables `revenue-operations-agent` and GTM skills to access authoritative sales data
without building direct CRM connections.

## Activation Triggers

- `revenue-operations-agent` requires pipeline data for its monitoring heartbeat
- A new opportunity is created or stage-changed in CRM (webhook event)
- A contact or account record requires sync from an enterprise system of record
- `cfo-agent` requests revenue actuals for financial reconciliation
- An operator requests a pipeline or territory analysis

## Execution Protocol

1. **Pipeline data pull**: Query CRM for open opportunities:
   - Fields: opportunity_id, name, stage, amount, close_date, owner, account, last_activity_date
   - Apply filters: stage NOT IN [Closed Won, Closed Lost]
   - Compute derived fields: days_in_stage, activity_recency_days, days_to_close_date

2. **Deal risk scoring**: For each opportunity, compute:
   - `stage_age_score`: days in current stage / median_days_for_stage (>1.5 = at risk)
   - `activity_score`: last_activity_date recency (> 7 days = degraded engagement)
   - `composite_risk_score = 0.6 × stage_age_score + 0.4 × activity_score`

3. **Contact sync**: Sync contact changes between CRM and other enterprise systems
   (HRIS for employee contacts, ITSM for customer contacts) via `enterprise-integration-hub`.
   Apply deduplication: match on email, then name+company.

4. **Opportunity updates**: Write-back operations (stage updates, close date changes)
   require caller authorization via `zero-trust-runtime` (CRM write scope).
   Apply optimistic locking: check last-modified-at before writing to prevent overwrites.

## Output Format

```yaml
crm_result:
  operation: pipeline_pull | contact_sync | opportunity_update | risk_score
  system: salesforce | hubspot
  opportunities:
    total: 0
    at_risk_count: 0
    total_pipeline_usd: 0
  status: success | auth_failed | rate_limited
  audit_ref: "CRM-OPS-2026-xxxxx"
```

## Quality Gates

- Pipeline data must include `retrieved_at` timestamp for staleness tracking
- Write-back operations must confirm with ETag/version check before committing

## References

- `references/` — CRM field mapping, deal risk scoring formula, contact dedup rules
