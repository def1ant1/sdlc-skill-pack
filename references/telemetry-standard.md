# Telemetry Standard

## Correlation IDs
All runtime and business telemetry events must include a non-empty `correlation_id` to support cross-domain tracing.

## Event Categories
- `runtime`: execution, token/cost, latency, routing, retries.
- `business`: ROI, conversion, policy outcomes, revenue impact.

## Contract
Events should conform to `schemas/telemetry-event.schema.json`.

## Enforcement
Use `scripts/validate_telemetry_events.py` to validate event streams and reject events without `correlation_id` for runtime/business categories.
