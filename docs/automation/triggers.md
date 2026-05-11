# Automation Triggers

Automation triggers connect event types to workflow plans.

## Register a trigger

```bash
python scripts/automation/register_trigger.py --trigger runtime/automation/example_trigger.json
```

Trigger payloads follow `schemas/automation-trigger.schema.json`.

## Run triggers for an event

```bash
python scripts/automation/run_event_trigger.py --event-type invoice.created --event-payload runtime/automation/example_event.json
```

Execution is governance-gated via `scripts/governance/enforce_runtime_policy.py` before launching `scripts/runtime/execute_workflow.py`.

Trigger execution history is written to `runtime/automation/trigger_history.jsonl` and consumed by `scripts/reports/generate_dashboard_data.py` for dashboard reporting.
