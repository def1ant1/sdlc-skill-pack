# Changelog

All notable changes to the Apotheon AI Company OS are documented here.


## [8.0.27] — 2026-05-11 — Local App Connector Layer + Readiness Reports (MB-P1-005)

- Expanded `local_apps/` with profile-based compose startup, local env template, readiness docs, and canonical priority app mappings for MVP categories.
- Added local app inventory and connector health tooling via `scripts/local_apps/list_apps.py` and `scripts/local_apps/check_connector_health.py`.
- Generated local app health artifacts in `reports/local_apps/` with JSON/Markdown readiness outputs for operational review.

## [8.0.26] — 2026-05-11 — Connector Hardening + Health Reporting (MB-P1-004)

- Hardened connector safety in `scripts/connectors/base_connector.py` + `scripts/connectors/health_check.py` with explicit failure-type classification (`auth`, `network`, `schema`, `rate-limit`, `app-down`), read-only defaults, HITL-gated writes, and redacted error surfaces.
- Added `scripts/reports/generate_connector_health_report.py` to publish connector health exports and generated `reports/connector_health_report.md` + `reports/connector_health_report.json` for dashboard ingestion.
- Updated `scripts/reports/generate_dashboard_data.py` and onboarding runbooks to surface connector-failure breakdowns and operator workflows.

## [8.0.25] — 2026-05-11 — Graph Workflow Executor (MB-P1-003)

- Added graph execution foundations across `core/planner/`, `core/skill-router/`, `core/executor/`, `core/evaluator/`, and `core/governor/` with branching, retry semantics, approval gates, memory hydration checks, evaluator hooks, and governance enforcement primitives.
- Added `schemas/workflow-graph.schema.json` and `scripts/orchestration/execute_graph.py` to define and run checkpointable workflow graphs with resume-ready state output.
- Added orchestration tests for branch correctness and approval/checkpoint state transitions in `tests/orchestration/test_execute_graph.py`.


## [8.0.24] — 2026-05-11 — Event Bus + Trigger Engine (MB-P1-002)

- Added event bus and trigger-engine scaffolding in `core/event-bus/` and `core/trigger-engine/` for local event publishing, trigger registration, matching, and history persistence.
- Added `schemas/automation-trigger.schema.json` and automation scripts `scripts/automation/register_trigger.py` + `scripts/automation/run_event_trigger.py` to support trigger registration, governance checks, and dry-run workflow launch execution.
- Extended dashboard data generation in `scripts/reports/generate_dashboard_data.py` with `trigger_history` rollups derived from `runtime/automation/trigger_history.jsonl`.

## [8.0.23] — 2026-05-11 — Multi-layer Memory + Knowledge Graph (MB-P1-001)

- Added multi-layer memory foundations in `core/memory-system/`, `core/organizational-memory/`, and `core/procedural-memory/` plus graph domain scaffolding in `core/knowledge-graph/`.
- Added `schemas/memory-event.schema.json` to standardize episodic/semantic/organizational/procedural memory events and graph entity references.
- Added `scripts/memory/record_execution_memory.py` with episodic capture, stable fact promotion to semantic memory, procedural memory recording, and local graph updates.
- Added `scripts/memory/detect_contradictions.py` and integrated contradiction blocking in `scripts/memory/retrieve_context.py` before retrieved context is eligible for downstream use.

## [8.0.22] — 2026-05-11 — Release Readiness Gate + Packaging Manifest (MB-P0-020)

- Unified release gate in `scripts/validate_release_readiness.py` to aggregate release report generation, artifact consistency validation, Section 15 governance gates, and offline smoke tests.
- Hardened deterministic packaging in `scripts/package_release.py` with required `VERSION`/`RELEASE_NOTES.md` inclusion and generated checksum + manifest (`.sha256`, `.manifest.json`) for each ZIP build.
- Finalized release artifacts (`VERSION`, `CHANGELOG.md`, `RELEASE_NOTES.md`) and updated release-process docs with the single release readiness flow.

## [8.0.21] — 2026-05-11 — OldFarmTrucks Company Template Import (MB-P0-019)

- Added importable template payload at `company_templates/oldfarmtrucks/template.json` with workflows, schedules, dashboards, connectors, approvals, budgets, and sample data.
