# APOTHEON — LOCAL WORKFLOW AND SCHEDULING BACKLOG

**Status:** LOCAL ENABLEMENT PLAN  
**Target environment:** Developer laptop first, then Temporal/server deployment  
**Purpose:** Define the remaining work to make Apotheon workflows, recurring schedules, dry-run validation, and local execution reliable against the skill project.

---

## 1. Reassessment Summary

The repo has strong foundations for local workflow execution and testing:

- `scripts/runtime/execute_workflow.py` exists.
- `scripts/runtime/temporal_worker.py` exists.
- `scripts/runtime/context_manager.py` exists.
- `scripts/orchestration/plan_gtm_workflow.py` exists.
- Runtime and integration tests exist for workflow execution.
- Example business workflow docs now exist for OldFarmTrucks.com and customer lifecycle use cases.
- Domain planner tests appear to exist under `tests/scripts/test_domain_workflow_planners.py`.
- Repo truth reports exist under `reports/`.

The remaining local-development gap is to make workflow planning, workflow execution, schedule definition, schedule dry runs, schedule execution, observability, and regression testing work as an operator-friendly local loop.

---

## 2. Local Workflow Goals

The project should support these local workflows without requiring cloud credentials unless explicitly requested:

```text
1. Plan a workflow from a natural-language objective.
2. Validate the workflow plan against the skill inventory and governance rules.
3. Dry-run the workflow without LLM/API side effects.
4. Execute the workflow locally with controlled context packets.
5. Save workflow run history locally.
6. Define recurring schedules in YAML.
7. Preview upcoming scheduled runs.
8. Run due schedules locally.
9. Produce execution reports.
10. Promote selected workflows to Temporal schedules later.
```

---

# P0 — Local Workflow Contract and Plan Validation

## Task 1 — Standardize workflow plan schema

Create or update:

```text
schemas/workflow-plan.schema.json
references/workflow-plan-standard.md
scripts/validation/validate_workflow_plan.py
```

Required workflow plan fields:

```yaml
workflow_id:
name:
objective:
domain:
mode: dry_run | local | temporal
risk_level: low | medium | high | critical
requires_human_approval:
created_at:
planner:
canonical_entities:
systems:
steps:
  - order:
    skill:
    purpose:
    inputs:
    outputs:
    dependencies:
    governance:
      hitl_required:
      policy_refs:
    context_loading:
    expected_artifacts:
success_metrics:
reports:
failure_policy:
```

Acceptance criteria:

- `python scripts/validation/validate_workflow_plan.py path/to/plan.json` validates plans.
- All planners output this schema.
- Tests cover invalid skill names, missing policies, duplicate order numbers, and circular dependencies.

---

## Task 2 — Add workflow plan registry

Create:

```text
workflows/examples/
workflows/library/
workflows/generated/.gitkeep
scripts/workflows/register_workflow.py
scripts/workflows/list_workflows.py
```

Acceptance criteria:

- Example workflows can be committed under `workflows/examples/`.
- Generated local plans go under `workflows/generated/` and are ignored unless intentionally committed.
- Registry can list workflow name, domain, risk level, planner, and schedule status.

---

## Task 3 — Add OldFarmTrucks workflow examples as executable plans

Create example JSON/YAML plans:

```text
workflows/examples/oldfarmtrucks-launch-readiness.json
workflows/examples/oldfarmtrucks-weekly-operating-review.json
workflows/examples/oldfarmtrucks-market-scarcity-scan.json
workflows/examples/oldfarmtrucks-customer-lifecycle.json
workflows/examples/oldfarmtrucks-customer-360.json
```

Acceptance criteria:

- Each example validates against `workflow-plan.schema.json`.
- Each example uses existing skills or explicitly marks missing skills as backlog gaps.
- Each example can be dry-run locally.

---

# P0 — Local Domain Planners

## Task 4 — Verify and complete business/customer/finance/inventory planners

Required planners:

```text
scripts/orchestration/plan_business_workflow.py
scripts/orchestration/plan_customer_workflow.py
scripts/orchestration/plan_finance_workflow.py
scripts/orchestration/plan_inventory_workflow.py
```

Acceptance criteria:

- Each supports `--dry-run`.
- Each supports `--json`.
- Each supports `--output path`.
- Each validates skills against generated skill inventory.
- Each fails gracefully when a needed skill is missing.
- Each emits workflow plans that pass `validate_workflow_plan.py`.

Required local test objectives:

```text
Launch OldFarmTrucks.com as a classic truck dealership in 30 days.
Create weekly operating review for OldFarmTrucks.com.
Find acquisition opportunities for classic farm trucks within 300 miles.
Build lifecycle marketing automation for OldFarmTrucks.com.
Build a Customer 360 and CDP unification workflow for OldFarmTrucks.com.
Create a customer health and retention workflow for OldFarmTrucks.com.
Build marketing attribution and revenue intelligence for OldFarmTrucks.com.
```

---

# P0 — Local Schedule System

## Task 5 — Add schedule schema and schedule registry

Create:

```text
schemas/workflow-schedule.schema.json
schedules/examples/
schedules/local/.gitkeep
references/workflow-scheduling-standard.md
scripts/schedules/validate_schedule.py
scripts/schedules/list_schedules.py
```

Schedule schema fields:

```yaml
schedule_id:
name:
workflow_ref:
enabled:
timezone:
trigger:
  type: cron | interval | manual | event
  cron:
  interval_minutes:
  event_name:
next_run_policy:
misfire_policy:
risk_level:
requires_human_approval:
max_runtime_minutes:
concurrency_policy: forbid | replace | allow
notification_policy:
output_policy:
```

Acceptance criteria:

- Schedules validate against schema.
- Schedules can reference workflow files.
- Invalid cron/timezone/concurrency policy fails validation.

---

## Task 6 — Add local scheduler runner

Create:

```text
scripts/schedules/run_due_schedules.py
scripts/schedules/preview_schedule.py
scripts/schedules/mark_schedule_run.py
runtime/schedule_runs/.gitkeep
```

Acceptance criteria:

- `python scripts/schedules/preview_schedule.py schedules/examples/weekly-operating-review.yaml` shows next N runs.
- `python scripts/schedules/run_due_schedules.py --dry-run` shows due workflows without executing side effects.
- `python scripts/schedules/run_due_schedules.py --execute --local` executes due local workflows.
- Schedule run history is stored locally under `runtime/schedule_runs/` or configurable equivalent.
- Concurrency policy is enforced.

---

## Task 7 — Add example schedules for OldFarmTrucks.com

Create:

```text
schedules/examples/oldfarmtrucks-daily-market-scan.yaml
schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
schedules/examples/oldfarmtrucks-weekly-customer-lifecycle.yaml
schedules/examples/oldfarmtrucks-monthly-pricing-model-review.yaml
schedules/examples/oldfarmtrucks-quarterly-strategy-review.yaml
```

Recommended cadence:

```text
Daily 07:00 local — market scarcity/pricing scan
Weekly Monday 09:00 local — operating review
Weekly Wednesday 10:00 local — customer lifecycle review
Monthly first business day 09:00 local — pricing model review
Quarterly first Monday 10:00 local — strategy review
```

Acceptance criteria:

- All schedules validate.
- All referenced workflows exist and validate.
- `preview_schedule.py` can show upcoming runs.
- `run_due_schedules.py --dry-run` works on laptop without external credentials.

---

# P0 — Local Execution, State, and Reports

## Task 8 — Add local workflow run history

Create:

```text
runtime/workflow_runs/.gitkeep
scripts/workflows/list_runs.py
scripts/workflows/show_run.py
schemas/workflow-run-record.schema.json
```

Run record should include:

```yaml
run_id:
workflow_id:
workflow_version:
schedule_id:
mode:
status:
started_at:
completed_at:
steps_completed:
steps_failed:
artifacts:
reports:
token_usage:
estimated_cost:
governance_events:
errors:
```

Acceptance criteria:

- Every local execution writes a run record.
- Dry runs are recorded separately from real local runs.
- Runs can be listed and inspected.

---

## Task 9 — Add local artifact and report output policy

Create:

```text
runtime/artifacts/.gitkeep
runtime/reports/.gitkeep
references/local-output-policy.md
```

Acceptance criteria:

- Workflow outputs are deterministic and stored under a predictable run directory.
- Reports include workflow objective, skill chain, generated artifacts, skipped side effects, and governance approvals needed.
- Generated local artifacts are ignored by git unless explicitly promoted.

---

## Task 10 — Add workflow execution dry-run mode hardening

Update:

```text
scripts/runtime/execute_workflow.py
scripts/runtime/skill_activity.py
```

Acceptance criteria:

- `--dry-run` never calls external LLMs or external connectors.
- `--dry-run` produces placeholder artifacts and validates routing.
- `--dry-run` reports which side effects would have occurred.
- `--dry-run` validates governance/HITL requirements.

---

# P1 — Temporal Schedule Promotion

## Task 11 — Promote local schedules to Temporal schedules

Create:

```text
scripts/schedules/promote_to_temporal.py
scripts/schedules/list_temporal_schedules.py
references/temporal-schedule-promotion.md
```

Acceptance criteria:

- Local YAML schedule can be converted into a Temporal schedule definition.
- Promotion requires validation and human confirmation.
- Temporal schedule metadata preserves schedule ID, workflow ref, risk level, and approval rules.

---

# P1 — Operator Experience

## Task 12 — Add local operator CLI

Create or update CLI support:

```text
cli.py
scripts/local_operator.py
```

Desired commands:

```bash
apotheon workflows list
apotheon workflows plan business "..."
apotheon workflows validate workflows/examples/oldfarmtrucks-launch-readiness.json
apotheon workflows run workflows/examples/oldfarmtrucks-launch-readiness.json --dry-run
apotheon schedules list
apotheon schedules preview schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
apotheon schedules run-due --dry-run
apotheon runs list
apotheon runs show <run_id>
```

Acceptance criteria:

- Commands work on laptop from clean checkout.
- Errors include next-step suggestions.
- Docs include copy/paste examples.

---

# P1 — Local Observability

## Task 13 — Add local workflow dashboard/report

Create:

```text
scripts/reports/generate_local_ops_report.py
reports/local_ops_report.md
reports/local_ops_report.json
```

Report should include:

- Recent workflow runs
- Due schedules
- Failed schedules
- Long-running workflows
- Governance approvals pending
- Token/cost estimates
- Most-used skills
- Missing skills encountered by planners

Acceptance criteria:

- Report is generated from local run/schedule data.
- No external dependencies required.

---

# P1 — Workflow Regression Test Harness

## Task 14 — Add workflow fixture tests

Create:

```text
tests/workflows/test_example_workflows_validate.py
tests/schedules/test_example_schedules_validate.py
tests/schedules/test_run_due_schedules.py
tests/runtime/test_dry_run_no_external_calls.py
```

Acceptance criteria:

- All example workflows validate.
- All example schedules validate.
- Dry-run execution does not call external APIs.
- Scheduler preview/run-due logic is deterministic under frozen time.

---

# 3. Suggested Local Test Matrix

Run these locally after implementation:

```bash
python scripts/generate_skill_inventory.py --root .
python scripts/orchestration/plan_business_workflow.py \
  "Launch OldFarmTrucks.com as a classic truck dealership in 30 days" \
  --dry-run --json --output workflows/generated/oldfarmtrucks-launch.json
python scripts/validation/validate_workflow_plan.py workflows/generated/oldfarmtrucks-launch.json
python scripts/runtime/execute_workflow.py --plan workflows/generated/oldfarmtrucks-launch.json --dry-run
python scripts/schedules/validate_schedule.py schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
python scripts/schedules/preview_schedule.py schedules/examples/oldfarmtrucks-weekly-operating-review.yaml --count 5
python scripts/schedules/run_due_schedules.py --dry-run
python scripts/reports/generate_local_ops_report.py
pytest tests/workflows tests/schedules tests/runtime -q
```

---

# 4. Recommended First Local Schedules

Start with these because they validate the highest-value business loop without risky side effects:

1. Weekly operating review
2. Daily market scan dry run
3. Weekly customer lifecycle review
4. Monthly pricing model review
5. Quarterly strategy review

Do not enable external side effects until:

- dry-run reports are stable,
- governance policies are linked,
- customer communication approvals are enforced,
- scraping policy is enforced,
- schedule run history is reliable.

---

# 5. Release Criteria for Local Workflow/Schedule Enablement

This backlog is complete when:

- Domain planners produce valid workflow plans.
- Example workflows validate and dry-run.
- Example schedules validate and preview.
- Due schedules can be dry-run locally.
- Local workflow run history is recorded.
- Local reports are generated.
- No dry-run path calls external services.
- OldFarmTrucks short-term and long-term workflows are included in tests.
