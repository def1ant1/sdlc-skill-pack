# APOTHEON — HARDENING AND ERROR HANDLING BACKLOG

**Status:** RELEASE HARDENING PLAN  
**Purpose:** Improve runtime reliability, error handling, observability, recovery, safe degradation, connector resilience, local app robustness, and production-readiness across Apotheon skills, planners, workflows, schedules, connectors, and local Docker services.

---

## 1. Goals

This backlog hardens the platform so workflows can run repeatedly and safely in local, scheduled, and Temporal modes.

Target outcomes:

```text
structured errors
predictable failure behavior
safe dry-runs
idempotent writes
retry and backoff policies
circuit breakers
workflow checkpointing
schedule misfire handling
connector degradation
local app health reporting
clear operator recovery steps
actionable diagnostics
```

---

## 2. Cross-Cutting Error Taxonomy

Create:

```text
schemas/error-envelope.schema.json
references/error-handling-standard.md
scripts/validation/validate_error_contracts.py
```

Required error envelope:

```yaml
error_id:
correlation_id:
workflow_run_id:
schedule_run_id:
skill:
step:
severity: info | warning | error | critical
category:
  validation | config | auth | network | rate_limit | timeout | dependency | connector | data_quality | schema | governance | hitl | model | memory | schedule | runtime | security | unknown
retryable:
user_action_required:
message:
technical_detail:
root_cause_hint:
remediation:
source_exception:
created_at:
```

Acceptance criteria:

- All runtime/planner/scheduler/connector failures use the standard envelope.
- User-facing errors include next-step remediation.
- Logs include correlation IDs.
- Tests validate representative errors.

---

## 3. Runtime Hardening

Create or update:

```text
scripts/runtime/error_types.py
scripts/runtime/error_handler.py
scripts/runtime/retry_policy.py
scripts/runtime/circuit_breaker.py
scripts/runtime/idempotency.py
scripts/runtime/recovery.py
```

Required capabilities:

- typed exception hierarchy
- retry policy by error category
- exponential backoff with jitter
- max retry caps
- circuit breaker for unhealthy connectors/apps
- idempotency keys for external actions
- checkpoint and resume support
- partial failure reporting
- safe cancellation
- timeout handling
- operator recovery guidance

Acceptance criteria:

- Retryable failures retry only when safe.
- Non-retryable failures fail fast with clear remediation.
- L3/high-risk actions are never retried if the retry could duplicate side effects.
- Dry-run never performs side effects.

---

## 4. Workflow Execution Hardening

Update:

```text
scripts/runtime/execute_workflow.py
scripts/runtime/skill_activity.py
scripts/runtime/temporal_worker.py
```

Requirements:

- Validate workflow plan before execution.
- Validate step outputs against expected schemas when present.
- Persist workflow run state after each step.
- Record failed step, skipped steps, and resumable state.
- Support `--resume <run_id>`.
- Support `--continue-on-warning`.
- Support `--fail-fast`.
- Support `--max-step-runtime`.
- Support `--error-report path`.

Acceptance criteria:

- Failed workflow writes run record and error report.
- Resume can continue from last successful checkpoint.
- Partial outputs are preserved.
- Tests cover failing middle step, timeout, invalid plan, and failed schema validation.

---

## 5. Planner Hardening

Update all planners:

```text
scripts/orchestration/plan_workflow.py
scripts/orchestration/plan_gtm_workflow.py
scripts/orchestration/plan_business_workflow.py
scripts/orchestration/plan_customer_workflow.py
scripts/orchestration/plan_finance_workflow.py
scripts/orchestration/plan_inventory_workflow.py
scripts/orchestration/plan_legal_workflow.py
scripts/orchestration/plan_data_security_workflow.py
```

Requirements:

- Validate objective is non-empty and actionable.
- Validate selected skills exist.
- Detect missing dependencies.
- Detect ambiguous routing.
- Output deterministic JSON.
- Include missing-skill warnings without crashing when in planning mode.
- Fail clearly when a required skill is unavailable.
- Emit `planner_diagnostics` in output.

Acceptance criteria:

- Planner output always validates or exits nonzero.
- Missing skill errors name the missing skill and likely remediation.
- Planner tests cover ambiguous objectives and missing skills.

---

## 6. Schedule Hardening

Create or update:

```text
scripts/schedules/validate_schedule.py
scripts/schedules/preview_schedule.py
scripts/schedules/run_due_schedules.py
scripts/schedules/schedule_state.py
schemas/workflow-schedule.schema.json
schemas/schedule-run-record.schema.json
```

Requirements:

- Validate cron/timezone/interval/event trigger.
- Detect invalid workflow references.
- Enforce concurrency policy: `forbid`, `replace`, or `allow`.
- Handle misfires: `skip`, `run_once`, or `catch_up`.
- Store schedule run history.
- Use locks to avoid duplicate runs.
- Support dry-run and no-external-call mode.
- Produce schedule diagnostics.

Acceptance criteria:

- Frozen-time tests prove deterministic next-run calculation.
- Duplicate scheduled runs are blocked when concurrency is `forbid`.
- Misfires are recorded and handled according to policy.

---

## 7. Connector Hardening

Update connector base and all connectors:

```text
scripts/connectors/base_connector.py
scripts/connectors/health_check.py
scripts/connectors/local_apps/
```

Requirements:

- Standard timeout handling.
- Standard auth failure handling.
- Rate-limit detection.
- Pagination error recovery.
- Partial-page recovery.
- Circuit breaker state.
- Schema drift detection.
- Read-only mode by default.
- Write-action idempotency key.
- HITL enforcement for writes.
- Safe redaction of secrets from logs.

Acceptance criteria:

- Connector health reports distinguish auth, network, schema, app-down, and permission errors.
- No connector logs secrets.
- Write attempts without approval fail closed.

---

## 8. Local Open-Source App Hardening

Create or update:

```text
local_apps/README.md
local_apps/docker-compose.local-apps.yml
local_apps/manifests/*.yaml
scripts/local_apps/check_app_health.py
scripts/local_apps/generate_local_app_report.py
```

Requirements:

- Health checks for app, database, worker, queue, and API where applicable.
- Startup dependency ordering.
- Clear port conflict reporting.
- Volume existence checks.
- Backup readiness checks.
- Upgrade/migration warnings.
- `.env` validation.
- Resource usage warnings.

Acceptance criteria:

- Report identifies unhealthy containers and likely cause.
- App readiness report distinguishes running container from usable API.
- Missing env vars fail with clear remediation.

---

## 9. Data Validation and Schema Hardening

Create or update:

```text
scripts/validation/validate_json_schema.py
scripts/validation/validate_canonical_entities.py
scripts/validation/validate_event_schemas.py
scripts/validation/validate_connector_mappings.py
```

Requirements:

- Validate canonical entity examples.
- Validate event payload examples.
- Validate connector mapping files.
- Validate workflow outputs where schemas exist.
- Detect unknown fields when strict mode is enabled.
- Detect missing required lineage/source fields.

Acceptance criteria:

- Invalid canonical mappings fail CI.
- Workflow output validation reports exact field path and expected type.

---

## 10. Governance and Safety Hardening

Create or update:

```text
scripts/governance/validate_policy_links.py
scripts/governance/validate_hitl_for_actions.py
scripts/governance/validate_high_risk_boundaries.py
```

Requirements:

- High-risk skills must reference governance docs.
- External actions require HITL policy.
- Financial/legal/tax/HR/trading/security/logistics/materials actions must be approval-gated.
- Professional-boundary language required in outputs for regulated domains.
- Policy violations fail closed.

Acceptance criteria:

- Tests prove high-risk write actions cannot run without approval.
- Governance errors include policy reference and remediation.

---

## 11. Observability and Diagnostics

Create or update:

```text
scripts/reports/generate_runtime_diagnostics.py
reports/runtime_diagnostics.md
reports/runtime_diagnostics.json
references/observability-standard.md
```

Required telemetry:

```text
workflow_run_started
workflow_run_completed
workflow_run_failed
step_started
step_completed
step_failed
retry_scheduled
circuit_opened
connector_unhealthy
schedule_misfire
hitl_required
policy_violation
schema_validation_failed
```

Acceptance criteria:

- Every workflow run has correlation ID.
- Logs are structured JSON when `LOG_FORMAT=json`.
- Reports summarize recent failures by category and remediation.

---

## 12. Backup, Recovery, and State Hardening

Create:

```text
scripts/backup/backup_local_state.py
scripts/backup/restore_local_state.py
references/local-backup-restore-standard.md
```

Scope:

```text
runtime/workflow_runs
runtime/schedule_runs
runtime/artifacts
runtime/reports
Qdrant collections
local app volumes
PostgreSQL dumps where applicable
configuration snapshots excluding secrets
```

Acceptance criteria:

- Backup produces manifest and checksum.
- Restore supports dry-run preview.
- Secrets are not included in backups unless explicitly encrypted and approved.

---

## 13. Chaos and Failure Injection Tests

Create:

```text
tests/hardening/test_retry_policy.py
tests/hardening/test_circuit_breaker.py
tests/hardening/test_workflow_resume.py
tests/hardening/test_schedule_misfire.py
tests/hardening/test_connector_failures.py
tests/hardening/test_no_secret_leakage.py
tests/hardening/test_dry_run_no_side_effects.py
```

Failure scenarios:

```text
connector timeout
rate limit
invalid credentials
schema drift
missing skill
invalid workflow plan
failed middle workflow step
schedule misfire
duplicate schedule run
Qdrant unavailable
Temporal unavailable
local app unhealthy
model API failure
malformed model output
policy violation
approval timeout
```

Acceptance criteria:

- Failures are deterministic under tests.
- Expected failures produce structured errors and remediation.
- No dry-run test performs network write or side effect.

---

## 14. Operator Experience Hardening

Update CLI/docs:

```text
cli.py
docs/onboarding/LOCAL_LAPTOP_SETUP_RUNBOOK.md
docs/onboarding/TROUBLESHOOTING.md
docs/onboarding/OPERATOR_RUNBOOK.md
```

Required operator commands:

```bash
apotheon doctor
apotheon diagnostics
apotheon workflows resume <run_id>
apotheon schedules repair
apotheon connectors check
apotheon local-apps check
apotheon backup create
apotheon backup restore --dry-run
```

Acceptance criteria:

- `apotheon doctor` runs local environment checks and explains failures.
- Troubleshooting docs map common errors to fixes.

---

## 15. Release Acceptance Criteria

This hardening backlog is complete when the Section 15 release gate runner passes:

```bash
python scripts/validate_section15_release_gates.py
```

CI enforcement:

- `.github/workflows/validate.yml` runs this gate on push/PR.
- `.github/workflows/validate.yml` runs this gate again for release `published`/`prereleased` events.
- Release tagging/promotion is blocked by nonzero exit from any Section 15 gate.

Machine-verifiable gate checklist:

```text
[ ] Error envelope schema exists and is used
[ ] Runtime retry/circuit/idempotency modules exist
[ ] Workflow execution writes failure records and supports resume
[ ] Planners emit diagnostics and validate outputs
[ ] Schedules handle misfires and concurrency safely
[ ] Connectors fail closed and never leak secrets
[ ] Local app health/readiness reports distinguish container/API/schema/auth failures
[ ] High-risk actions are blocked without approval
[ ] Runtime diagnostics reports are generated
[ ] Backup and restore dry-run exist
[ ] Failure injection tests pass
[ ] Dry-run side-effect tests pass
[ ] Operator runbook and troubleshooting docs exist
```

---

## 16. Recommended Implementation Order

Implementation board and milestone tracking are published at:

- `docs/roadmap/hardening-section16-milestones-board.md`

1. Error envelope schema and standard.
2. Runtime error handler, retry policy, circuit breaker, idempotency.
3. Workflow checkpoint/failure/resume support.
4. Planner diagnostics and validation.
5. Schedule misfire/concurrency handling.
6. Connector failure handling and secret redaction.
7. Governance fail-closed validators.
8. Local app health/readiness checks.
9. Runtime diagnostics reports.
10. Backup/restore dry-run.
11. Failure injection tests.
12. Operator troubleshooting docs and `apotheon doctor`.
