# AI Telemetry + Replay MVP

This MVP captures trace events across six stages for each workflow run:

1. planner
2. router
3. memory
4. tool
5. evaluator
6. governor

## Event contract

All AI telemetry events should validate against:

- `schemas/ai-telemetry-event.schema.json`

## Replay narratives

Generate a replay narrative from runtime history:

```bash
python scripts/reports/generate_ai_telemetry_report.py
```

The report includes stage-level coverage and a stage-by-stage path summary suitable for debugging and postmortems.
