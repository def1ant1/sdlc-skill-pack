# Data Scraping Policy

## Purpose
Ensure collection of external web data is lawful, respectful, and operationally safe.

## Policy
- Collect data only where terms of service and applicable law permit.
- Respect robots directives, rate limits, and anti-abuse controls.
- Do not collect credentials, protected personal data, or content behind authentication without explicit authorization.
- Attribute sources and maintain collection metadata (timestamp, URL, method, consent/legal basis where relevant).

## Required Controls
- Pre-collection legality and ToS check.
- Throttling, retry limits, and failure-safe stop conditions.
- Data quality and provenance logging for downstream use.

## Marketplace extension enforcement
- Every marketplace source must declare legal ownership, jurisdiction, review ticket, and explicit approval state.
- Robots and ToS checks must be time-stamped and preserved in source metadata.
- Source definitions must include hard throttle limits (`max_requests_per_minute`, `burst_limit`, `cooldown_seconds`) and a declared user-agent.
- Residential proxies are prohibited; only managed datacenter proxy pools are permitted.
- Non-compliant source definitions are blocked by `scripts/marketplaces/validate_source_policy.py` and should not be scheduled.

## Violation behavior
- Enforcement is fail-closed: ingest jobs are denied when legal, robots, ToS, or throttle controls are missing or invalid.
- Violations must be logged with source identifier, reason, and timestamp for audit traceability.
- Repeated violations require governance review before source reactivation.
