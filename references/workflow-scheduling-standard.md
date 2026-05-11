# Workflow Scheduling Standard

Defines local schedule registry schema, deterministic preview behavior, due-run execution (dry-run/live), concurrency policies (`forbid|replace|allow`), and misfire handling (`skip|run_once|catch_up`).

## Commands
- `python scripts/schedules/validate_schedule.py`
- `python scripts/schedules/list_schedules.py`
- `python scripts/schedules/preview_schedule.py --count 5`
- `python scripts/schedules/run_due_schedules.py --dry-run`
- `python scripts/schedules/mark_schedule_run.py --schedule-id <id> --run-at <iso>`

## Runtime State
- Locks: `runtime/schedule_state/locks/`
- Run records: `runtime/schedule_runs/<schedule_id>/<run_id>.json`

Run records must validate against `schemas/schedule-run-record.schema.json`.
