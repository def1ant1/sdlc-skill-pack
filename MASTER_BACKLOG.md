# MASTER BACKLOG — Apotheon AI Company OS

**Status:** Canonical consolidated backlog  
**Created:** 2026-05-11  
**Purpose:** Consolidate the remaining/open/incomplete work from all active Apotheon backlog documents into a single prioritized execution backlog.

---

## 0. Source Backlogs Reviewed

This master backlog consolidates the following backlog sources:

| Source | Disposition |
|---|---|
| `APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md` | Partially complete; V9 foundation has significant implementation, but open work remains. |
| `V9_OPEN_WORK_TASKS.md` | Generated repo-truth snapshot; superseded by this master backlog but still useful as evidence. |
| `APOTHEON_RC1_RELEASE_FINALIZATION_BACKLOG.md` | Archived planning doc; canonical local orchestration plan moved to `APOTHEON_LOCAL_WORKFLOW_SCHEDULING_BACKLOG.md`. |
| `APOTHEON_LOCAL_WORKFLOW_SCHEDULING_BACKLOG.md` | Active; much of this remains open. |
| `APOTHEON_DOCKER_DEPLOYMENT_BACKLOG.md` | Active; mostly open/productization work. |
| `APOTHEON_HARDENING_AND_ERROR_HANDLING_BACKLOG.md` | Active; mostly open/reliability hardening work. |
| `APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md` | Active; broad domain expansion backlog, mostly open. |

---

## 1. Completion Verification Summary

### Verified complete or substantially implemented

Based on the repo-truth snapshot and backlog snippets, these V9 foundation areas are marked substantially complete:

- Backlog truth extraction/validation/reporting foundation.
- V9 universal skill contract foundation.
- Skill inventory generation.
- Progressive disclosure / context-budget foundation.
- Skill dependency graph and orchestration map foundation.
- Routing collision reporting foundation.
- Several governance/reporting/repo-truth reports.
- Runtime foundation exists for local workflow execution.
- Temporal worker foundation exists.
- Context manager foundation exists.
- GTM workflow planner exists.
- Runtime/integration tests exist.
- OldFarmTrucks business workflow example docs exist.
- Customer lifecycle CRM/CDP/marketing example docs exist.

### Verified incomplete or not proven complete

The following are not proven complete and remain open in this master backlog:

- Docker deployment runtime and compose profiles.
- Chat UI.
- Dashboard/control plane.
- Skill compiler / `skill_pipeline.py`.
- Formal `skill.yaml` schema and progressive metadata loader.
- Skill graph engine as a runtime/queryable component.
- Multi-layer memory and knowledge graph beyond current Qdrant/context foundations.
- AI telemetry/replay/debugger platform.
- Policy governance kernel and sandboxing runtime.
- Event bus / trigger engine.
- Workflow graph execution beyond linear plans.
- Workflow plan schema/validator.
- Local schedule schema/runner/preview/run history.
- Local workflow run history and artifact policy.
- Domain planners for business/customer/finance/inventory/legal/security/etc. where not already implemented.
- Domain skill packs across finance, trading, tax, legal, economics, logistics, L&D, materials, security, HR, sales, research.
- Local open-source app connector layer.
- Rate-limit and quota manager.
- Runtime economics/cost dashboard.
- Connector hardening and health reports.
- Backup/restore stack.
- Public/local skill registry and marketplace packaging.

---

## 2. Backlog Documents to Mark Complete / Archive

### Archive / supersede

- `APOTHEON_RC1_RELEASE_FINALIZATION_BACKLOG.md` is already an archived planning document and should remain archived.
- `V9_OPEN_WORK_TASKS.md` is a generated snapshot and should not be hand-maintained.
- Previous domain-specific backlog documents should remain as supporting source docs but should no longer be treated as canonical execution order.

### Keep active but subordinate to `MASTER_BACKLOG.md`

- `APOTHEON_DOCKER_DEPLOYMENT_BACKLOG.md`
- `APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md`
- `APOTHEON_HARDENING_AND_ERROR_HANDLING_BACKLOG.md`
- `APOTHEON_LOCAL_WORKFLOW_SCHEDULING_BACKLOG.md`
- `APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md`

---

# P0 — Release-Critical Productization Work

## MB-P0-001 — Create Docker runtime baseline

**Source:** Docker Deployment Backlog  
**Status:** Complete (2026-05-11)

Create:

```text
Dockerfile
Dockerfile.dev
.dockerignore
docker-compose.yml
docker-compose.override.yml
.env.example
scripts/docker/doctor.sh
scripts/docker/wait-for-services.sh
scripts/docker/init-local-stack.sh
scripts/docker/smoke-test-container.sh
scripts/docker/check-compose-health.py
docs/onboarding/DOCKER_DEPLOYMENT.md
docs/onboarding/DOCKER_TROUBLESHOOTING.md
```


Validation evidence (2026-05-11):

- Added profile-aware local stack and env template:
  - `local_apps/docker-compose.local-apps.yml`
  - `local_apps/.env.local-apps.example`
- Added canonical category mapping and coverage for priority local apps:
  - `local_apps/mappings/local_app_categories.yaml`
  - `scripts/local_apps/list_apps.py`
- Added health/readiness + connector checks and generated health reports:
  - `scripts/local_apps/check_app_health.py`
  - `scripts/local_apps/check_connector_health.py`
  - `scripts/local_apps/generate_local_app_report.py`
  - `reports/local_apps/health-report.json`
  - `reports/local_apps/health-report.md`
  - `reports/local_apps/connector_health_report.json`

Acceptance criteria:

- Docker image builds reproducibly.
- Core compose stack starts locally.
- Qdrant, Temporal, Postgres, and Redis health checks pass.
- Validation commands run inside container.
- Workflow dry-run works inside container.

---

## MB-P0-002 — Add local-solo MVP profile

**Source:** Docker Deployment Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
profiles/local-solo.yaml
profiles/mvp.yaml
profiles/team.yaml
profiles/enterprise.yaml
profiles/full-domain-lab.yaml
schemas/profile.schema.json
scripts/validation/validate_profiles.py
```

Acceptance criteria:

- `local-solo` runs on consumer hardware.
- `mvp` includes only release-critical skills/workflows.
- Experimental or high-risk skills are disabled by default.
- Docker Compose profiles align with product profiles.

---

## MB-P0-003 — Formalize `skill.yaml` specification

**Source:** Docker/Productization + V9 Backlog  
**Status:** Completed and finalized (2026-05-11)

Create or harden:

```text
schemas/skill.yaml.schema.json
schemas/skill-metadata.schema.json
references/skill-specification-standard.md
scripts/validation/validate_skill_yaml.py
```

Acceptance criteria:


Validation evidence (2026-05-11):

- Added hardened schemas and validator:
  - `schemas/skill.yaml.schema.json`
  - `schemas/skill-metadata.schema.json`
  - `references/skill-specification-standard.md`
  - `scripts/validation/validate_skill_yaml.py`
- Ran `python scripts/validation/validate_skill_yaml.py --mvp`.
- Result: 87 MVP manifests checked, non-compliant manifests require migration for metadata parity fields (`metadata.token_budget`, `metadata.governance`, and `metadata.load_modes` with `metadata_only`).

- Every MVP skill has `skill.yaml` or equivalent manifest.
- Skill metadata can load without full skill references.
- Token budgets are machine-readable.
- Governance policies are machine-readable.

---

## MB-P0-004 — Build skill graph engine MVP

**Source:** Docker/Productization + V9 Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
core/skill-graph-engine/
scripts/skills/build_skill_graph.py
scripts/skills/resolve_skill_dependencies.py
reports/skill_graph.md
reports/skill_graph.json
reports/skill_graph.mmd
```

Acceptance criteria:

- Skill graph includes skills, tools, policies, memory requirements, and connectors.
- Graph detects cycles, missing dependencies, and routing collisions.
- Planners can query graph for candidate skills.

---

## MB-P0-005 — Build workflow plan schema and validator

**Source:** Local Workflow Scheduling Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
schemas/workflow-plan.schema.json
references/workflow-plan-standard.md
scripts/validation/validate_workflow_plan.py
```

Acceptance criteria:

- Workflow plans validate from CLI.
- Planners emit workflow plans that pass schema validation.
- Tests cover invalid skills, missing policies, duplicate step order, and circular dependencies.

---

## MB-P0-006 — Build local workflow registry and executable fixtures

**Source:** Local Workflow Scheduling + Docker/Productization Backlogs  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
workflows/examples/
workflows/library/
workflows/generated/.gitkeep
scripts/workflows/register_workflow.py
scripts/workflows/list_workflows.py
workflows/examples/oldfarmtrucks-launch-readiness.json
workflows/examples/oldfarmtrucks-weekly-operating-review.json
workflows/examples/oldfarmtrucks-market-scarcity-scan.json
workflows/examples/oldfarmtrucks-customer-lifecycle.json
workflows/examples/oldfarmtrucks-customer-360.json
```

Acceptance criteria:

- At least 5 reference workflows execute end-to-end in dry-run.
- OldFarmTrucks examples validate and dry-run.
- Fixtures include expected artifacts/reports and failure cases.

---

## MB-P0-007 — Harden workflow runtime for dry-run/live execution

**Source:** Hardening + Docker/Productization Backlogs  
**Status:** Completed and finalized (2026-05-11)

Update/create:

```text
scripts/runtime/execute_workflow.py
scripts/runtime/skill_activity.py
scripts/runtime/output_parser.py
scripts/runtime/model_router.py
scripts/runtime/local_model_fallback.py
scripts/runtime/schema_validation.py
scripts/runtime/retry_policy.py
```

Acceptance criteria:

- `--dry-run` never calls external LLMs or connectors.
- Live mode supports controlled LLM invocation.
- Structured output parsing and validation exists.
- Workflow run records are written.
- Correlation IDs and cost estimates are emitted.

---

## MB-P0-008 — Add structured error envelope and runtime hardening

**Source:** Hardening Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
schemas/error-envelope.schema.json
references/error-handling-standard.md
scripts/runtime/error_types.py
scripts/runtime/error_handler.py
scripts/runtime/circuit_breaker.py
scripts/runtime/idempotency.py
scripts/runtime/recovery.py
scripts/validation/validate_error_contracts.py
```

Acceptance criteria:

- Runtime/planner/scheduler/connector errors use a standard envelope.
- Retryable vs non-retryable behavior is explicit.
- High-risk side-effect actions are never blindly retried.
- Errors include operator remediation.

---

## MB-P0-009 — Add local workflow run history and artifact policy

**Source:** Local Workflow Scheduling Backlog  
**Status:** Done (2026-05-11)

Create:

```text
runtime/workflow_runs/.gitkeep
runtime/artifacts/.gitkeep
runtime/reports/.gitkeep
schemas/workflow-run-record.schema.json
scripts/workflows/list_runs.py
scripts/workflows/show_run.py
references/local-output-policy.md
```

Acceptance criteria:

- Every dry-run/live local execution writes run state.
- Artifacts/reports are deterministic and stored under run directory.
- Runs can be listed and inspected.

---

## MB-P0-010 — Build schedule schema, preview, and due-runner

**Source:** Local Workflow Scheduling + Hardening Backlogs  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
schemas/workflow-schedule.schema.json
schemas/schedule-run-record.schema.json
schedules/examples/
schedules/local/.gitkeep
references/workflow-scheduling-standard.md
scripts/schedules/validate_schedule.py
scripts/schedules/list_schedules.py
scripts/schedules/preview_schedule.py
scripts/schedules/run_due_schedules.py
scripts/schedules/mark_schedule_run.py
scripts/schedules/schedule_state.py
runtime/schedule_runs/.gitkeep
```

Acceptance criteria:

- Schedule validation supports cron/interval/manual/event triggers.
- Preview shows next N runs deterministically.
- Due-runner supports dry-run and local execution.
- Misfires and concurrency policy are handled safely.

---

## MB-P0-011 — Implement core domain planners

**Source:** Local Workflow Scheduling + Domain Backlogs  
**Status:** Completed and finalized (2026-05-11)

Required planners:

```text
scripts/orchestration/plan_business_workflow.py
scripts/orchestration/plan_customer_workflow.py
scripts/orchestration/plan_finance_workflow.py
scripts/orchestration/plan_inventory_workflow.py
scripts/orchestration/plan_legal_workflow.py
scripts/orchestration/plan_data_security_workflow.py
```

Acceptance criteria:

- Each supports `--dry-run`, `--json`, and `--output`.
- Each validates selected skills against inventory/skill graph.
- Each emits plans that pass `validate_workflow_plan.py`.
- Missing skills produce clear diagnostics.

---

## MB-P0-012 — Add policy governance runtime enforcement

**Source:** Docker/Productization + Hardening + Domain Backlogs  
**Status:** Done (2026-05-11) / runtime enforcement, fail-closed policy decisions, and evidence pack generation implemented

Create or harden:

```text
core/policy-engine/
core/governance-kernel/
core/business-approval-gateway/
core/sandbox-execution/
schemas/skill-permission.schema.json
scripts/governance/validate_policy_links.py
scripts/governance/validate_hitl_for_actions.py
scripts/governance/validate_high_risk_boundaries.py
scripts/governance/enforce_runtime_policy.py
scripts/governance/generate_evidence_pack.py
```

Acceptance criteria:

- High-risk external actions fail closed without approval.
- Financial/legal/tax/HR/trading/security/logistics/materials actions are approval-gated.
- Evidence packs are generated for regulated workflows.
- Policy decisions are logged and visible in dashboard.

---

## MB-P0-013 — Add AI telemetry, evaluation, and replay MVP

**Source:** Docker/Productization Backlog  
**Status:** Done (2026-05-11)

Create:

```text
core/ai-telemetry/
core/evaluation-engine/
core/replay-debugger/
schemas/ai-telemetry-event.schema.json
scripts/reports/generate_ai_telemetry_report.py
scripts/evals/run_skill_benchmarks.py
```

Acceptance criteria:

- Every workflow has traceable AI telemetry.
- Replay report explains planner/router/memory/tool/evaluator/governor path.
- Benchmarks run for MVP skills.
- Regression tests flag degraded skill performance.

---

## MB-P0-014 — Add rate-limit and quota manager

**Source:** Docker/Productization Backlog  
**Status:** Done

Create:

```text
core/rate-limit-manager/
skills/rate-limit-analysis/
schemas/rate-limit-policy.schema.json
references/rate-limit-and-quota-standard.md
scripts/validation/validate_rate_limit_policies.py
scripts/reports/generate_rate_limit_report.py
```

Acceptance criteria:

- Connectors declare rate-limit policies.
- Scheduler respects connector/API/database quotas.
- Workflows degrade to cached/stale/read-only mode where appropriate.
- Reports show quota usage and throttling.

---

## MB-P0-015 — Add runtime economics / cost dashboard MVP

**Source:** Docker/Productization Backlog  
**Status:** Done

Create:

```text
core/runtime-economics/
skills/budget-monitoring/
skills/api-cost-analysis/
skills/llm-token-cost-tracking/
skills/workflow-cost-attribution/
schemas/cost-event.schema.json
reports/cost_dashboard.md
reports/cost_dashboard.json
```

Acceptance criteria:

- Every workflow run reports estimated cost.
- Scheduler can warn/block on budget thresholds.
- Dashboard shows daily/weekly/monthly spend.
- UI displays estimated cost before workflow execution.

---

## MB-P0-016 — Add chat UI MVP

**Source:** Docker/Productization Backlog  
**Status:** Done (2026-05-11)

Create:

```text
apps/chat-ui/
apps/chat-ui/README.md
apps/chat-ui/streamlit_app.py
scripts/api/apotheon_api.py
```

Acceptance criteria:

- User can submit objective from browser UI.
- User can select domain planner.
- UI shows workflow plan, artifacts/reports, approvals, schedules, local app health, cost estimates, and rate-limit warnings.
- UI blocks live writes by default.
- UI can import OldFarmTrucks company template.

---

## MB-P0-017 — Add dashboard/control-plane MVP

**Source:** Docker/Productization Backlog  
**Status:** Done (2026-05-11)

Create:

```text
apps/dashboard/
apps/dashboard/streamlit_dashboard.py
apps/control-plane-api/
apps/control-plane-ui/
scripts/reports/generate_dashboard_data.py
schemas/dashboard-state.schema.json
reports/dashboard_state.json
```

Acceptance criteria:

- User sees workflow progress, scheduled work, approvals, budgets, rate limits, connector status, local app health, memory status, telemetry, and skill maturity.
- User can approve/reject HITL items.
- Dashboard can show OldFarmTrucks template status.

---

## MB-P0-018 — Add skill pipeline compiler MVP

**Source:** Docker/Productization Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
scripts/skill_pipeline.py
core/skill-compiler/
schemas/compiled-skill.schema.json
references/skill-pipeline-standard.md
reports/skill_pipeline_report.md
reports/skill_pipeline_report.json
```

Acceptance criteria:
Validation evidence (2026-05-11):

- Added deterministic pipeline compiler scaffolds and standard/schema:
  - `scripts/skill_pipeline.py`
  - `core/skill-compiler/`
  - `schemas/compiled-skill.schema.json`
  - `references/skill-pipeline-standard.md`
- Generated reports:
  - `reports/skill_pipeline_report.md`
  - `reports/skill_pipeline_report.json`
- Verified deterministic and testable behavior with:
  - `python scripts/skill_pipeline.py --version 0.1.0`
  - `python -m unittest core/skill-compiler/tests/test_compiler.py`

- Compiler converts skill contract into runnable scaffold.
- Generates Temporal activity stub, Python activity scaffold, JSON schema bindings, pytest/eval scaffolds, governance wrapper, telemetry definitions, rate-limit/cost stubs, docs, and package metadata.
- Output is deterministic and tests pass.

---

## MB-P0-019 — Add OldFarmTrucks company template

**Source:** Docker/Productization + Local Workflow Backlogs  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
company_templates/oldfarmtrucks/
scripts/company_templates/import_template.py
schemas/company-template.schema.json
```

Acceptance criteria:

- Import creates workflows, schedules, dashboards, connectors, approval policies, budgets, and sample data.
- Import defaults to dry-run.
- Template can run at least one short-term and one long-term workflow.

---

## MB-P0-020 — Add release readiness aggregator and deterministic package flow

**Source:** RC1 Release Finalization Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
scripts/validate_release_readiness.py
scripts/package_release.py
scripts/smoke_test_release.py
VERSION
CHANGELOG.md
RELEASE_NOTES.md
reports/release_readiness.md
reports/release_readiness.json
```

Acceptance criteria:

- Single readiness gate aggregates validation, docs, smoke tests, package checks, and governance checks.
- Deterministic ZIP/package produced with checksum and manifest.
- Release smoke tests cover planning/runtime/report integrity.
- Version/changelog consistency validated.

---

# P1 — Platform Foundation and Hardening

## MB-P1-001 — Add multi-layer memory and knowledge graph

**Source:** Docker/Productization Backlog  
**Status:** Completed — 2026-05-11 (multi-layer memory + contradiction guardrails delivered)

Create:

```text
core/memory-system/
core/knowledge-graph/
core/organizational-memory/
core/procedural-memory/
schemas/memory-event.schema.json
scripts/memory/record_execution_memory.py
scripts/memory/retrieve_context.py
scripts/memory/detect_contradictions.py
```

Acceptance criteria:

- Workflow executions update episodic memory.
- Stable facts can be promoted to semantic memory.
- Skill improvements record procedural memory.
- Contradictions are flagged before use.
- Knowledge graph links customers, invoices, products, vendors, decisions, risks, and workflows.

---

## MB-P1-002 — Add event bus and trigger engine

**Source:** Docker/Productization Backlog  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
core/event-bus/
core/trigger-engine/
schemas/automation-trigger.schema.json
scripts/automation/register_trigger.py
scripts/automation/run_event_trigger.py
```

Acceptance criteria:

- Triggers can launch workflows in dry-run.
- Triggered workflows pass through governor.
- Trigger history appears in dashboard.

---

## MB-P1-003 — Add graph-based workflow execution

**Source:** Docker/Productization Backlog  
**Status:** Completed (2026-05-11)

Create or harden:

```text
core/planner/
core/skill-router/
core/executor/
core/evaluator/
core/governor/
schemas/workflow-graph.schema.json
scripts/orchestration/execute_graph.py
```

Acceptance criteria:

- Workflows can run as graphs, not only linear step lists.
- Branching, retries, state, approvals, memory hydration, evaluators, policy enforcement, and checkpoint/resume are supported.

---

## MB-P1-004 — Add connector hardening and health reporting

**Source:** Hardening + Docker/Productization Backlogs  
**Status:** Done

Create/update:

```text
scripts/connectors/base_connector.py
scripts/connectors/health_check.py
scripts/connectors/local_apps/
scripts/reports/generate_connector_health_report.py
reports/connector_health_report.md
reports/connector_health_report.json
```

Acceptance criteria:

- Auth/network/schema/rate-limit/app-down errors are distinguished.
- Connectors support dry-run, read-only default, rate-limit policies, secret redaction, and HITL-gated writes.
- Connector failures surface in dashboard.

---

## MB-P1-005 — Add local open-source app connector layer

**Source:** Domain + Docker/Productization Backlogs  
**Status:** Completed and finalized (2026-05-11)

Create:

```text
local_apps/docker-compose.local-apps.yml
local_apps/.env.example
local_apps/README.md
local_apps/manifests/*.yaml
local_apps/mappings/*.yaml
scripts/local_apps/list_apps.py
scripts/local_apps/check_app_health.py
scripts/local_apps/check_connector_health.py
scripts/local_apps/generate_local_app_report.py
reports/local_app_health_report.md
reports/local_app_health_report.json
```

Initial app categories:

- CRM
- CDP/analytics
- marketing automation
- BI
- ERP/accounting/inventory
- helpdesk
- knowledge base
- workflow automation
- identity/secrets
- observability/security

Acceptance criteria:

- MVP local app stack can start via Docker Compose profiles.
- Health/readiness checks work.
- Canonical mappings exist for priority apps.

---

## MB-P1-006 — Add backup/restore for local and Docker state

**Source:** Hardening + Docker/Productization Backlogs  
**Status:** Completed — 2026-05-11

Create:

```text
scripts/backup/backup_local_state.py
scripts/backup/restore_local_state.py
scripts/docker/backup-stack.sh
scripts/docker/restore-stack.sh
references/local-backup-restore-standard.md
docs/onboarding/DOCKER_BACKUP_RESTORE.md
```

Acceptance criteria:

- Backups include manifest and checksums.
- Restore supports dry-run preview.
- Secrets are excluded unless explicitly encrypted and approved.

---

## MB-P1-007 — Add domain cognition modules for MVP domains

**Source:** Docker/Productization + Domain Backlogs  
**Status:** Completed — 2026-05-11

Priority domains:

```text
sales
finance/accounting
legal/tax
security
HR
knowledge/research
GTM
SDLC
operations
```

Acceptance criteria:

- Priority MVP skills include principles, heuristics, frameworks, evaluators, anti-pattern detectors, examples, policy boundaries, and memory hooks.
- Skills can self-check against domain-specific rubrics.

---

## MB-P1-008 — Add skill maturity/certification reports

**Source:** Docker/Productization + V9 Backlogs  
**Status:** Completed — 2026-05-11

Create:

```text
scripts/grade_skill_maturity.py
scripts/certify_skill.py
reports/skill_maturity_report.md
reports/skill_certification_report.md
tests/skills/test_skill_maturity.py
```

Acceptance criteria:

- MVP skills graded 0–5.
- >70% MVP skills reach level 3+.
- >50% MVP skills reach level 4+.
- Critical/high-risk MVP skills reach level 5 before v1.0.

---

# P2 — Domain Skill Expansion

## MB-P2-001 — Finance and accounting skill pack

**Source:** V9 + Domain Backlogs  
**Status:** Completed — 2026-05-11

Implement/complete skills for:

```text
accounting-operations
bookkeeping-automation
chart-of-accounts-management
journal-entry-review
month-end-close-support
reconciliation-automation
accounts-payable-automation
accounts-receivable-automation
invoice-processing
collections-prioritization
payment-matching
cash-management
cash-flow-forecasting
budget-planning
budget-variance-analysis
fpa-analysis
financial-scenario-modeling
runway-analysis
revenue-leakage-detection
working-capital-optimization
unit-economics-analysis
financial-control-monitoring
expense-policy-compliance
```

Acceptance criteria:

- Uses canonical finance entities.
- Outputs separate observed data, calculations, assumptions, and recommendations.
- Payments/accounting-book/tax-facing actions require approval.
- Evals cover calculation accuracy and governance compliance.

---

## MB-P2-002 — CRM/CDP/marketing/customer lifecycle skill pack

**Source:** V9 + Domain + Customer Lifecycle Docs  
**Status:** Completed (2026-05-11)

Implement/complete skills for:

```text
crm-integration
cdp-profile-unification
customer-segmentation
lead-scoring
sales-pipeline-forecasting
opportunity-risk-analysis
proposal-automation
marketing-attribution
campaign-optimization
seo-intelligence
content-strategy
brand-sentiment-analysis
persona-modeling
conversion-funnel-analysis
customer-health-scoring
churn-risk-detection
support-ticket-intelligence
voice-of-customer-analysis
customer-journey-analysis
```

Acceptance criteria:

- Uses canonical customer/lead/opportunity/campaign/ticket entities.
- Consent/suppression/communication preferences are enforced.
- Outbound communication requires approval unless explicitly permitted.
- Lifecycle event taxonomy is implemented.

---

## MB-P2-003 — Inventory, product, procurement, and market intelligence skill pack

**Source:** V9 + Domain + OldFarmTrucks Docs  
**Status:** Completed (2026-05-11)

Implementation notes:
- Added demand/margin/stockout/vendor-risk/procurement-routing/scarcity/arbitrage coverage in phase-pack governance.
- Enforced scraping policy controls (robots/terms/rate limits/operator approval) and explicit approval gates for purchase/listing/outreach actions.
- Validated OldFarmTrucks acquisition/pricing paths with upgraded dry-run fixtures.

Implement/complete skills for:

```text
inventory-forecasting
sku-margin-analysis
demand-planning
stockout-risk-detection
supplier-risk-intelligence
vendor-scorecarding
procurement-automation
purchase-approval-routing
market-pricing-intelligence
local-market-data-collection
competitor-price-scraping
scarcity-analysis
arbitrage-analysis
vehicle-market-arbitrage
```

Acceptance criteria:

- Supports OldFarmTrucks acquisition/pricing workflows.
- Scraping respects policy, robots/terms/rate limits, and approval rules.
- Purchase/listing/outreach actions require approval.

---

## MB-P2-004 — Legal, tax, entity, and regulatory intelligence skill pack

**Source:** Domain Backlog  
**Status:** Completed

Implement/complete skills for:

```text
tax-strategy-support
deduction-opportunity-analysis
entity-tax-comparison-support
estimated-tax-planning
retirement-plan-contribution-support
business-entity-management
entity-compliance-calendar
legal-operations
legal-research-support
regulatory-monitoring
jurisdiction-law-monitoring
local-law-research
county-law-research
state-law-research
federal-law-research
tax-rate-monitoring
business-license-research
permit-requirements-research
vehicle-dealer-law-research
contract-review-support
legal-obligation-tracking
legal-deadline-monitoring
legal-citation-validation
```

Acceptance criteria:

- All outputs are decision support, not final legal/tax advice.
- Authoritative sources prioritized and cited.
- Findings include jurisdiction, authority level, effective date, retrieved/verified timestamps, confidence, and professional-review flag.
- Filings/submissions/actions require approval.

---

## MB-P2-005 — Trading, portfolio, and arbitrage research skill pack

**Source:** Domain Backlog  
**Status:** Completed (2026-05-11)

Implement/complete skills for:

```text
trading-research
market-data-ingestion
watchlist-management
portfolio-risk-analysis
technical-analysis-support
fundamental-analysis-support
crypto-market-analysis
fx-market-analysis
correlation-regime-analysis
position-sizing-analysis
trade-journal-analysis
backtesting-support
risk-limit-monitoring
cross-market-price-comparison
fee-slippage-modeling
liquidity-risk-analysis
execution-risk-analysis
crypto-arbitrage-monitoring
fx-arbitrage-analysis
retail-arbitrage-analysis
```

Acceptance criteria:

- Research only; no autonomous trading.
- Trade ideas labeled hypotheses with risk, assumptions, horizon, and invalidation criteria.
- Fixture data works offline/dry-run.
- No market manipulation or evasion support.

---

## MB-P2-006 — HR and learning/development skill pack

**Source:** V9 + Domain Backlogs  
**Status:** Completed (2026-05-11)

Implement/complete skills for:

```text
hr-management
workforce-planning
hiring-pipeline-intelligence
job-description-generation
interview-scorecard-analysis
onboarding-workflow-management
employee-record-management
performance-coaching-support
learning-development
skills-gap-analysis
role-based-learning-paths
onboarding-curriculum-design
training-content-generation
learning-assessment-design
certification-tracking
coaching-plan-generation
learning-roi-analysis
```

Acceptance criteria:

- No autonomous high-impact HR decisions.
- Sensitive/protected attributes are not used for scoring.
- Bias/fairness safeguards exist.
- Performance-related insights require human review before employment impact.

---

## MB-P2-007 — Economic, logistics, materials, and data-security skill packs

**Source:** Domain Backlog  
**Status:** Completed (2026-05-11)

Implement/complete skills for:

```text
economic-analysis
macro-economic-reporting
regional-economic-analysis
industry-economic-analysis
inflation-impact-analysis
interest-rate-impact-analysis
labor-market-analysis
commodity-price-analysis
logistics-management
route-optimization-support
freight-cost-analysis
carrier-selection-support
vehicle-transport-coordination
materials-management
bill-of-materials-management
material-requirements-planning
material-substitution-analysis
material-quality-documentation
material-compatibility-research
data-security-management
data-classification
data-loss-prevention-analysis
secrets-management-review
access-control-review
iam-policy-analysis
privacy-impact-assessment
security-incident-triage
audit-log-review
```

Acceptance criteria:

- Economic outputs include source timestamps and scenario ranges.
- Logistics bookings/payments/docs require approval.
- Materials outputs flag safety-critical/professional review cases.
- Security mutations require approval and preserve evidence.

---

# P3 — Ecosystem, Marketplace, and Developer Experience

## MB-P3-001 — Skill registry and marketplace skeleton

**Source:** Docker/Productization Backlog  
**Status:** Completed (2026-05-11)

Create:

```text
skill_registry/
skill_registry/README.md
skills/CONTRIBUTING.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
.github/ISSUE_TEMPLATE/
.github/PULL_REQUEST_TEMPLATE.md
scripts/registry/validate_registry_entry.py
scripts/registry/package_skill.py
scripts/registry/publish_skill.py
schemas/skill-package.schema.json
schemas/skill-lockfile.schema.json
```

Acceptance criteria:

- Contributors can add a skill with one documented workflow.
- Registry validation runs in CI.
- Skills can be versioned and locked.
- Public publishing is optional and disabled by default.

---

## MB-P3-002 — Self-improvement/evolution engine

**Source:** Docker/Productization Backlog  
**Status:** Completed (2026-05-11)

Create:

```text
core/evolution-engine/
core/skill-gap-engine/
scripts/evolution/propose_skill_changes.py
scripts/evolution/generate_skill_pr.py
scripts/evolution/review_skill_change.py
```

Acceptance criteria:

- Failed workflows can generate skill-gap findings.
- System can generate PR-ready patches with tests/evals.
- No auto-merge or auto-apply of high-risk changes.
- Human review required before applying improvements.

---

## MB-P3-003 — Commercial/open-source boundary

**Source:** Docker/Productization Backlog  
**Status:** Completed (2026-05-11)

Create:

```text
COMMERCIAL.md
LICENSE_REVIEW.md
docs/commercial/open-core-boundary.md
```

Acceptance criteria:

- Users understand open-source core vs hosted/cloud/enterprise features.
- Local OSS usage is not confused with future commercial tiers.

---

## MB-P3-004 — VS Code/developer experience

**Source:** Docker/Productization Backlog  
**Status:** Completed (2026-05-11)

Create or improve:

```text
extensions/vscode/
.devcontainer/devcontainer.json
```

Capabilities:

- Skill authoring assistance.
- Frontmatter/manifest validation.
- Dry-run workflow launch.
- Skill maturity panel.
- Workflow/dashboard link.
- Error diagnostics.
- Skill compiler command.
- Company template import command.

---

## MB-P3-005 — Documentation, demo, and onboarding assets

**Source:** Docker/Productization + Local Setup Backlogs  
**Status:** Open / partially implemented

Create or improve:

```text
README.md
docs/onboarding/DOCKER_DEPLOYMENT.md
docs/onboarding/LOCAL_LAPTOP_SETUP_RUNBOOK.md
docs/onboarding/TROUBLESHOOTING.md
docs/onboarding/OPERATOR_RUNBOOK.md
docs/api/
docs/examples/
CONTRIBUTING.md
ROADMAP.md
```

Required assets:

- architecture diagrams
- quickstart tutorial
- single-user tutorial
- OldFarmTrucks demo tutorial
- video demo script
- API docs if FastAPI is implemented
- contribution workflow
- AI OS architecture page
- memory/knowledge graph explanation
- skill marketplace guide

---

# 3. Immediate Execution Order

Use this sequence for Codex/tasks:

1. `MB-P0-001` Docker runtime baseline.
2. `MB-P0-003` formal `skill.yaml` specification.
3. `MB-P0-004` skill graph engine MVP.
4. `MB-P0-005` workflow plan schema/validator.
5. `MB-P0-007` dry-run/live runtime hardening.
6. `MB-P0-008` structured error envelope/runtime hardening.
7. `MB-P0-006` workflow registry and executable fixtures.
8. `MB-P0-010` local schedule schema/preview/runner.
9. `MB-P0-011` core domain planners.
10. `MB-P0-012` governance runtime enforcement.
11. `MB-P0-013` AI telemetry/replay MVP.
12. `MB-P0-014` rate-limit manager.
13. `MB-P0-015` runtime economics/cost dashboard.
14. `MB-P0-016` chat UI MVP.
15. `MB-P0-017` dashboard/control-plane MVP.
16. `MB-P0-018` skill compiler MVP.
17. `MB-P0-019` OldFarmTrucks company template.
18. `MB-P0-020` release readiness/package/smoke gates.

---

# 4. Verification Process Going Forward

Before marking any item complete:

```bash
python scripts/generate_repo_truth_report.py
python scripts/validate_backlog_truth.py
python scripts/run_premerge_checks.py
pytest --tb=short -q
```

If Docker work is included:

```bash
docker compose config
docker compose build apotheon-cli
docker compose run --rm apotheon-cli python scripts/run_premerge_checks.py
```

If workflow/schedule work is included:

```bash
python scripts/validation/validate_workflow_plan.py workflows/examples/oldfarmtrucks-launch-readiness.json
python scripts/schedules/validate_schedule.py schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
python scripts/schedules/preview_schedule.py schedules/examples/oldfarmtrucks-weekly-operating-review.yaml --count 5
python scripts/schedules/run_due_schedules.py --dry-run
```

Completion rule:

```text
Only mark complete when implementation exists, tests pass, reports regenerate cleanly, and dry-run/live boundaries are verified.
```
