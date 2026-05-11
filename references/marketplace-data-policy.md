# Marketplace Data Policy

## Policy boundaries

1. Only source definitions that pass legal review, robots validation, and terms-of-service automation review may be activated.
2. Access to restricted categories (e.g., health, minors, financial account data) is disallowed unless separately approved by governance and legal stakeholders.
3. Captured data must contain lineage tags (`dataset`, `entity_type`, `run_id_prefix`) to support traceability.

## Rate limits and throttling

* Source-specific `max_requests_per_minute` is mandatory.
* Burst handling must be capped with `burst_limit`, with `cooldown_seconds` enforced between bursts.
* Exceeding source rate limits should move ingestion to degraded mode and trigger alerts.

## Proxy rules

* Only managed datacenter proxy pools are allowed.
* Residential proxy usage is prohibited.
* Proxy routing must be deterministic per source for auditability.

## Violation behavior

* Any source failing policy validation must be blocked from scheduler activation.
* Violations are logged with source id, reason, and timestamp.
* Repeated violations require governance sign-off before re-enablement.
