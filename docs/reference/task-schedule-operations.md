# Task & Schedule Operations

## Chat schedule commands
- `apotheon schedules create <schedule_id> <mode> <target>` creates governed schedule defaults.
- `apotheon schedules pause <schedule_id>` disables execution.
- `apotheon schedules archive <schedule_id>` disables and archives schedule.

## Recurring run task generation
When `generate_task: true` is set on a schedule, `scripts/scheduling/run_due_schedules.py`
creates a follow-up task artifact in `runtime/tasks/` per executed run.

## Task model
Tasks support conversation/plan/workflow/skill-gap origins, dependencies, acceptance criteria,
and assignee semantics (`user|role|queue|unassigned`).

## Schedule model
Schedules support cron/interval/event triggers and workflow/report/condition actions with governed approvals.
