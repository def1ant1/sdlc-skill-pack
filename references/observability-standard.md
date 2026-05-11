# Observability Standard

All workflow runtime telemetry MUST include:

- `correlation_id` for every event and log line.
- Structured JSON log output when `LOG_FORMAT=json`.
- Coverage for workflow lifecycle, retries, circuit/open health, misfires, HITL, policy failures, and schema failures.
- Failure aggregation by category with remediation guidance in `reports/runtime_diagnostics.md` and `reports/runtime_diagnostics.json`.

Runtime diagnostics are generated via `python scripts/reports/generate_runtime_diagnostics.py`.
