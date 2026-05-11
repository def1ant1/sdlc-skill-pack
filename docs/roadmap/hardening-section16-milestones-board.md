# Hardening Program Board — Section 16 Milestones

**Source:** `APOTHEON_HARDENING_AND_ERROR_HANDLING_BACKLOG.md` Section 16.  
**Cadence:** Weekly review every Monday in engineering planning until all milestones are `Done`.  
**Tracking fields:** owner, dependencies, phase-exit checks, and evidence artifacts.

## Milestone Plan (Epics / Sprints)

| Milestone | Sprint Window | Owner | Depends On | Scope (Section 16 translation) |
|---|---|---|---|---|
| M1: Error Contract Baseline | Sprint 1 | Platform Runtime Lead | None | Error envelope schema + validation standard |
| M2: Runtime Resilience Primitives | Sprint 1-2 | Runtime Reliability Lead | M1 | Error handler, retry, circuit breaker, idempotency |
| M3: Workflow Checkpoint/Resume | Sprint 2 | Workflow Engine Lead | M1, M2 | Checkpointing, failure recording, resume semantics |
| M4: Planner Diagnostics + Validation | Sprint 3 | Planning Systems Lead | M3 | Deterministic validated planner outputs with diagnostics |
| M5: Schedule Misfire/Concurrency Controls | Sprint 3-4 | Scheduling Lead | M3 | Concurrency policies, misfire handling, locks, history |
| M6: Connector Fail-Closed + Redaction | Sprint 4 | Integrations Lead | M2, M5 | Connector error handling, auth/network/schema distinction, secret redaction |
| M7: Governance Fail-Closed Validators | Sprint 4-5 | Governance Lead | M6 | High-risk action denial without approval |
| M8: Local App Health/Readiness | Sprint 5 | Local Platform Lead | M6 | Container/API/schema/auth-aware health and readiness checks |
| M9: Runtime Diagnostics Reporting | Sprint 5-6 | Observability Lead | M4, M5, M8 | Structured runtime diagnostics reports |
| M10: Backup/Restore Dry-Run | Sprint 6 | Data Reliability Lead | M3, M9 | Backup creation + restore dry-run safety |
| M11: Failure Injection + Dry-Run Safety Tests | Sprint 6-7 | QA Automation Lead | M10 | Failure injection and side-effect safety coverage |
| M12: Operator Experience + Doctor | Sprint 7 | Developer Experience Lead | M11 | Troubleshooting docs, runbooks, `apotheon doctor` |

## Foundational Sequencing Guardrail

Early-phase work is explicitly gated so no downstream module starts before all three foundations are accepted:

- M1 error envelope contract,
- M2 runtime primitives (retry/circuit/idempotency/error handling),
- M3 workflow checkpoint/failure/resume.

Any milestone M4+ entering implementation must show approved evidence links for M1-M3 in the weekly review.

## Milestone Exit Criteria + Artifact Checks

### M1: Error Contract Baseline
- Exit criteria:
  - Error envelope schema is present and valid.
  - Error handling standard is documented and adopted for new runtime errors.
  - Contract validation script passes in CI.
- Evidence / traceability:
  - `schemas/error-envelope.schema.json`
  - `references/error-handling-standard.md`
  - `scripts/validation/validate_error_contracts.py`

### M2: Runtime Resilience Primitives
- Exit criteria:
  - Typed exception hierarchy and centralized handler merged.
  - Retry policy includes category-aware safe retry behavior.
  - Circuit breaker and idempotency protections are wired to external actions.
- Evidence / traceability:
  - `scripts/runtime/error_types.py`
  - `scripts/runtime/error_handler.py`
  - `scripts/runtime/retry_policy.py`
  - `scripts/runtime/circuit_breaker.py`
  - `scripts/runtime/idempotency.py`
  - `scripts/runtime/recovery.py`

### M3: Workflow Checkpoint/Resume
- Exit criteria:
  - Failed workflows write structured run records and error reports.
  - `--resume <run_id>` resumes from last successful checkpoint.
  - Timeout and partial-failure behavior are covered by tests.
- Evidence / traceability:
  - `scripts/runtime/execute_workflow.py`
  - `scripts/runtime/skill_activity.py`
  - `scripts/runtime/temporal_worker.py`

### M4: Planner Diagnostics + Validation
- Exit criteria:
  - Planner outputs are deterministic and validate or fail nonzero.
  - Missing skill/dependency diagnostics include remediation hints.
  - Planner outputs include `planner_diagnostics`.
- Evidence / traceability:
  - `scripts/orchestration/plan_workflow.py`
  - `scripts/orchestration/plan_gtm_workflow.py`
  - `scripts/orchestration/plan_business_workflow.py`
  - `scripts/orchestration/plan_customer_workflow.py`
  - `scripts/orchestration/plan_finance_workflow.py`
  - `scripts/orchestration/plan_inventory_workflow.py`
  - `scripts/orchestration/plan_legal_workflow.py`
  - `scripts/orchestration/plan_data_security_workflow.py`

### M5: Schedule Misfire/Concurrency Controls
- Exit criteria:
  - Concurrency policies `forbid|replace|allow` enforced.
  - Misfire policies `skip|run_once|catch_up` recorded and enforced.
  - Duplicate-run prevention lock behavior proven by tests.
- Evidence / traceability:
  - `scripts/schedules/validate_schedule.py`
  - `scripts/schedules/preview_schedule.py`
  - `scripts/schedules/run_due_schedules.py`
  - `scripts/schedules/schedule_state.py`
  - `schemas/workflow-schedule.schema.json`
  - `schemas/schedule-run-record.schema.json`

### M6: Connector Fail-Closed + Redaction
- Exit criteria:
  - Health reports distinguish auth/network/schema/app-down/permission failures.
  - Connector write actions require explicit approval and idempotency key.
  - Logs are verified to redact secrets.
- Evidence / traceability:
  - `scripts/connectors/base_connector.py`
  - `scripts/connectors/health_check.py`
  - `scripts/connectors/local_apps/`

### M7: Governance Fail-Closed Validators
- Exit criteria:
  - High-risk actions fail closed without explicit approval artifacts.
  - Governance violation errors use standard error envelope.
- Evidence / traceability:
  - `scripts/governance/` (approval validators + enforcement hooks)

### M8: Local App Health/Readiness
- Exit criteria:
  - Readiness checks distinguish container, API, schema, auth, and dependency failures.
  - Preflight checks include env, port, volume, and migration warnings.
- Evidence / traceability:
  - `local_apps/README.md`
  - `local_apps/docker-compose.local-apps.yml`
  - `local_apps/manifests/*.yaml`
  - `scripts/local_apps/check_app_health.py`
  - `scripts/local_apps/generate_local_app_report.py`

### M9: Runtime Diagnostics Reporting
- Exit criteria:
  - Runtime diagnostics reports are generated for failure and warning paths.
  - Reports include correlation IDs and remediation hints.
- Evidence / traceability:
  - `scripts/runtime/` (diagnostics/report emitters)

### M10: Backup/Restore Dry-Run
- Exit criteria:
  - Backup artifact creation is reproducible and documented.
  - Restore `--dry-run` executes with no side effects and reports risks.
- Evidence / traceability:
  - `scripts/backup/` (backup + restore dry-run tooling)

### M11: Failure Injection + Dry-Run Safety Tests
- Exit criteria:
  - Failure-injection suite passes on CI.
  - Dry-run tests prove no irreversible side effects.
- Evidence / traceability:
  - `tests/` and `scripts/validate_section15_release_gates.py`

### M12: Operator Experience + Doctor
- Exit criteria:
  - `apotheon doctor` and diagnostics commands run and provide actionable output.
  - Runbook/troubleshooting mapping exists for top failure modes.
- Evidence / traceability:
  - `cli.py`
  - `docs/onboarding/LOCAL_LAPTOP_SETUP_RUNBOOK.md`
  - `docs/onboarding/TROUBLESHOOTING.md`
  - `docs/onboarding/OPERATOR_RUNBOOK.md`

## Weekly Review Workflow (Until Closure)

1. Monday review checks each milestone for status (`Not Started`, `In Progress`, `Blocked`, `Done`).
2. Every `In Progress` item must link at least one active PR and one artifact check.
3. Any blocked item must include unblock owner and target date.
4. M4+ milestones cannot proceed without approved M1-M3 evidence links.
5. Program closes only when M12 is done and Section 15 release gate passes:
   - `python scripts/validate_section15_release_gates.py`
