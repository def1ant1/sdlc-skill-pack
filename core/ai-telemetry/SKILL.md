# AI Telemetry Core

Defines canonical telemetry events for planner/router/memory/tool/evaluator/governor traces.

## Responsibilities
- Record per-step traces with run and workflow correlation IDs.
- Emit deterministic event types for replay and benchmarking.
- Enforce a schema-first event contract (`schemas/ai-telemetry-event.schema.json`).
