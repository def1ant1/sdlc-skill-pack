## 2026-05-12 — MASTER_UX_BACKLOG taskization status updates

- Updated every open/incomplete UX backlog item to include `Taskization: Completed (2026-05-12)` after generating execution tasks.
- This marks backlog-level task creation as completed while leaving each feature item status unchanged until implementation acceptance criteria are met.

## 2026-05-12 — MASTER_UX_BACKLOG open/incomplete task expansion

- Analyzed `MASTER_UX_BACKLOG.md` and generated a consolidated task tracker for every backlog item currently marked open/incomplete.
- Added a new `Open/Incomplete Work Task Tracker (Generated 2026-05-12)` section with actionable checkbox tasks per UX backlog item.
- Included explicit progress expectations per item: design plan, implementation, acceptance validation, and status transition to completed when done.

## 2026-05-12 — Assistant action chip model, generation, explainability, and audit events

- Hardened `schemas/artifacts/assistant-action.schema.json` with an explicit action chip contract and required explainability/reversibility metadata.
- Implemented `scripts/orchestration/assistant_action_chips.py` to generate chip sets from response context + active artifacts and to emit auditable chip-triggered events tied to conversation/message IDs.
- Updated `fixtures/artifacts/assistant_action.json` to include chip + event examples for validation.
- Updated assistant action UX documentation in `docs/architecture/assistant-workspace-ux.md` with chip contract and audit behavior.

## 2026-05-12 — Knowledge curation assistant lifecycle controls

- Added `core/knowledge-curation-assistant/references/knowledge-note-taxonomy.md` and `core/knowledge-curation-assistant/templates/knowledge-note.md` to define note taxonomy, lifecycle, provenance, impact links, and staleness semantics.
- Added `scripts/orchestration/conversation_to_knowledge_notes.py` with propose-only extraction, explicit lifecycle actions (`approve`, `edit`, `reject`, `archive`, `supersede`), conflict/staleness detection, command trigger detection (`remember this`, `don't use that anymore`), and targeted retrieval filters.
- Added `docs/reference/knowledge-curation-policy.md` to document memory curation policy, command semantics, and retrieval safeguards.

## 2026-05-12 — Planner contract + memory-aware intake hardening

- Extended living planner input contract with `planner_inputs` sections for conversation summary, constraints, assumptions, desired outputs, entities, preferences, and prior decisions.
- Added orchestrator-state ingestion (`--orchestrator-state`) and curated-memory answer hydration to prevent re-asking already resolved questions during plan drafting.
- Added `confidence_annotations` to distinguish explicit user-provided details from inferred assumptions.
- Preserved compatibility with current workflow conversion and execution paths by keeping existing plan fields stable while adding non-breaking metadata.

## 2026-05-12 — Artifact model schema pack + conversion rules + validation

- Added `schemas/artifacts/` with a shared envelope schema and dedicated schemas for plan, workflow, skill proposal, task, schedule, knowledge note, decision, approval request, and assistant action artifacts.
- Standardized envelope fields across artifact classes (`id`, `type`, `title`, `status`, source conversation/message IDs, owner, version, content, links).
- Added artifact conversion rules in `schemas/artifacts/conversion-rules.yaml` for plan→task, plan→workflow, conversation→knowledge, and workflow run→decision/lesson flows.
- Added version-tracked fixtures in `fixtures/artifacts/` and validation script `scripts/validation/validate_artifact_schemas.py` to ensure assistant-created artifacts are consistently addressable.
- Added artifact model documentation at `docs/schemas/artifact-model.md`.

## 2026-05-12 — Intake behavior modernization + prompting policy update

- Deprecated mandatory fixed intake sequencing in favor of progressive clarification rules.
- Added a material-uncertainty decision rule: ask only when missing context changes the next safe action.
- Added draft-first response strategy to deliver useful answer/plan/workflow output before refinement questions.
- Added explicit support for user directives like "use your best assumptions" with structured, user-editable assumption objects.
- Published intake behavior and assistant prompting policy documentation and linked it from `docs/index.md`.

## 2026-05-12 — Assistant Workspace app surface + synchronized UX panels

- Added `apps/assistant-workspace/streamlit_app.py` as the new primary app surface over existing chat/workflow/memory experiences.
- Implemented persistent panel layout: Conversation, Working Plan, Artifacts, and Knowledge / Memory using one shared session context object.
- Added in-app navigation model for Assistant Home, Plan Builder, Workflow Studio, Skill Library, Knowledge Base, and Task & Schedule Center.
- Implemented chat-driven synchronization hooks so plan/artifact/knowledge panes update immediately from conversation actions.
- Added `docs/architecture/assistant-workspace-ux.md` and linked it in `docs/index.md`.

## 2026-05-12 — MB-ECOM-P3-001/002 network graph + commerce simulator completion

- Added `core/commerce-network-graph/` with reliability history, pricing history, and fraud/risk correlation signal definitions tied to organizational memory primitives.
- Added network-graph skills: `vendor-network-analysis`, `supplier-reputation-analysis`, and `reseller-relationship-mapping`.
- Added `core/commerce-simulator/` with mandatory dry-run-only simulation controls and side-effect isolation guidance.
- Added simulation skills: `pricing-strategy-simulation`, `marketplace-scenario-analysis`, and `fulfillment-simulation`.
- Documented required simulator scenario modeling for demand shocks, fee changes, logistics delays, and inventory turnover.

## 2026-05-12 — MB-ECOM-P0-010 regional arbitrage + negotiation + finance-tax integration completion

- Added 13 ecommerce extension skills across regional-demand/arbitrage analysis, negotiation support, and finance-tax integration domains.
- Standardized logistics-impact-aware opportunity scoring requirements across new regional arbitrage skills.
- Added explicit no-autonomous-commitment controls and mandatory HITL approval boundaries across all negotiation-support skills.
- Added tax/jurisdiction professional-review flags and accounting-entity linkage requirements (`account_id`, `invoice_id`, `payment_id`, `order_id`, `marketplace_payout_id`) for finance-tax outputs.
- Added `docs/workflows/ecommerce-arbitrage-negotiation-finance-tax.md` to document governance and output contract requirements.

## 2026-05-11 — MB-ECOM-P0-005 ecommerce fulfillment/logistics completion

- Added 8 fulfillment/logistics skills under `skills/`: `ecommerce-fulfillment`, `shipping-carrier-selection`, `package-dimension-optimization`, `freight-and-pallet-analysis`, `warehouse-slotting-analysis`, `pick-pack-optimization`, `returns-routing-analysis`, and `shipping-sla-risk-analysis`.
- Standardized shipping recommendation contracts to require explicit `cost`, `delivery_time`, and `sla_risk` outputs with assumptions and confidence context.
- Integrated fulfillment decisioning guidance with canonical ecommerce ontology entities (`FulfillmentOrder`, `InventoryLot`, and order/listing references).
- Enforced mandatory approval gates for shipping purchases and all external side effects (labels, bookings, charges, and return-routing commitments).


## 2026-05-11 — MB-ECOM-P0-001 canonical ecommerce ontology + entities

- Added 11 canonical ecommerce entity schemas under `schemas/entities/` for marketplace, listing, supplier, catalog, inventory, fulfillment, shipment tracking, pricing snapshots, fee profiles, condition reports, and acquisition opportunities.
- Added normalized key/linkage model (`canonical_keys`, `links`) across all ecommerce entities to support cross-marketplace joins and reconciliation.
- Added condition grading + refurbishment fields and acquisition confidence/risk modeling fields for used/refurbished/collector workflows.
- Added `references/ecommerce-ontology.md` with canonical definitions, relationship diagram, and sample payloads.

## 2026-05-11 — MB-P3-005 documentation completion refresh

- Updated top-level docs and onboarding runbooks to align with current CLI/runtime paths.
- Refreshed API/examples documentation with runnable commands for profiles, schedules, approvals/governance, and diagnostics.
- Added required docs assets for architecture/tutorial/demo/navigation consistency.
- Updated docs index/navigation and marked MB-P3-005 complete in `MASTER_BACKLOG.md`.

## 2026-05-11 — MB-P2-007 multi-domain pack completion

- Completed MB-P2-007 by adding 28 domain skills across economics, logistics, materials, and data-security under `skills/` with standardized manifests/routing/evals.
- Enforced economic output requirements for source timestamps and scenario ranges in all economics skill contracts.
- Enforced mandatory approvals for logistics bookings, payments, and shipping-document actions.
- Enforced safety-critical/professional-review flags for materials recommendations.
- Enforced approval gates plus evidence-preservation requirements for security mutations.
- Updated governance documentation for runtime enforcement and professional-review boundaries.

## 2026-05-11 — HR/L&D governance + MB-P2-006 completion

- Completed MB-P2-006 by adding `skills/hr-learning-development-pack` with explicit coverage for HR and L&D capabilities, support-only operation, and high-impact human review gates.
- Added explicit protections preventing use of sensitive/protected attributes in scoring and ranking, including fairness checks and proxy-feature scan requirements.
- Added L&D outcome tracking and certification workflow fixtures for dry-run/offline validation.
- Updated HR governance policy and added dedicated L&D fairness/employment-impact governance documentation.

## 2026-05-11 — MB-P2-005 trading research pack completion

- Completed MB-P2-005 skill list with 20 trading/portfolio/arbitrage research skills under `skills/` and normalized safety sections.
- Enforced hypothesis labeling requirements (assumptions, risk factors, time horizon, invalidation criteria) and explicit prohibitions on autonomous trading plus manipulative/evasive guidance.
- Added offline fixture bundle for dry-run-compatible trading research validation under `tests/fixtures/trading-research/`.
- Added governance policy baseline in `docs/governance/trading-research-governance.md` and linked financial controls to trading research boundaries.
- Expanded safety/governance/backtesting coverage in `tests/skills/test_trading_research_safety.py`.


## 2026-05-11 — Customer lifecycle pack MB-P2-002 completion

- Completed MB-P2-002 customer-domain phase-pack governance by adding canonical customer/lead/opportunity/campaign/ticket entity coverage and explicit lifecycle taxonomy in `skills/sales-marketing-customer-phase-pack/`.
- Enforced consent, suppression, communication-preference checks, and approval requirements for outbound communication unless an explicit policy-permitted automation path exists.
- Added lifecycle workflow fixtures/diagnostics under `workflows/fixtures/oldfarmtrucks/` and updated customer lifecycle documentation baseline in `docs/examples/customer-lifecycle-crm-cdp-marketing-workflows.md`.


## 2026-05-11 — Finance pack MB-P2-001 completion

- Completed all MB-P2-001 finance/accounting skills with standardized finance output sections: observed data, calculations, assumptions, and recommendations.
- Enforced explicit approval gates for payment, accounting-book mutation, and tax-facing actions across the full finance skill set.
- Standardized governance-aware eval coverage for calculation correctness and approval/policy compliance on all MB-P2-001 skills.
- Added integration fixtures for forecasting, close, reconciliation, and controls in `tests/fixtures/finance-pack/`.
- Added regression tests to assert documentation, eval, and fixture completeness for the MB-P2-001 finance pack.

## 2026-05-11 — MB-ECOM-P0-004 sourcing and acquisition intelligence completion

- Added 8 ecommerce sourcing skills under `skills/`: `product-sourcing-intelligence`, `supplier-discovery`, `local-liquidation-analysis`, `auction-opportunity-analysis`, `wholesale-price-comparison`, `product-condition-estimation`, `product-authenticity-risk-analysis`, and `acquisition-priority-scoring`.
- Standardized supplier/opportunity scoring model requirements across these skills with margin, velocity, fraud/counterfeit risk, and confidence components plus weighted acquisition-priority scoring guidance.
- Enforced recommendation contract requirements for explicit rationale, assumptions, and multi-factor risk profiles on acquisition recommendations.
- Enforced mandatory HITL approval gates for all purchase action pathways (bids, deposits, POs, and payments).

# Changelog


## 2026-05-12 — Workspace-primary phased execution plan, gates, and migration notes

- Added phased execution plan to workspace architecture docs: P0 (orchestrator/intake/artifacts), P1 (plan+knowledge+tasks), P2 (chips+preview+approvals), and P3 (conversational skill creation).
- Defined release gates per phase spanning schema validation, routing quality checks, interruption handling, approval safety, and UX acceptance criteria.
- Added migration notes for legacy chat/workflow entrypoints to the workspace-primary operating model.
- Added telemetry checkpoints for adoption, completion rates, clarification-rate reduction, approval latency/safety, and interruption recovery quality.
- Updated onboarding to recommend Assistant Workspace as the default operator entrypoint.

## 2026-05-11 — MB-ECOM-P0-003 pricing intelligence engine completion

- Added `core/pricing-intelligence/` package with reusable normalization logic for marketplace price/fee/shipping/tax standardization and profitability calculations.
- Added new marketplace skills: `marketplace-price-normalization`, `marketplace-fee-analysis`, `marketplace-profitability-analysis`, `dynamic-margin-analysis`, and `competitor-pricing-intelligence`.
- Added `reports/marketplace_pricing_report.md` with channel-level and SKU-level sample analyses including net margin and confidence scoring outputs.

## 2026-05-11 — MB-P3-005 docs/demo/onboarding milestone

- Published unified documentation navigation in `docs/index.md` and added quickstart/onboarding flow updates.
- Added documentation assets: architecture diagram page, OldFarmTrucks tutorial, demo video script, API index, and marketplace/memory guide.
- Added docs quality gate `scripts/docs/validate_docs_integrity.py` with automated test coverage.

All notable changes to the Apotheon AI Company OS are documented here.


## [8.0.33] — 2026-05-11 — VS Code DX Workflow Hardening (MB-P3-004)

- Improved `extensions/vscode/` with command-palette developer flows for manifest validation, workflow dry-run launch, runtime diagnostics generation, skill maturity reporting, and company template import.
- Added local compiler/runtime config for extension automation, including configurable Python command execution for repository scripts.
- Added `.devcontainer/devcontainer.json` for reproducible extension development with Python + Node setup and post-create install bootstrap.
- Added extension-facing and onboarding documentation in `extensions/vscode/README.md` and `docs/onboarding/VSCODE_EXTENSION_DEVELOPER.md`, and linked developer flow guidance from `docs/onboarding/getting-started.md`.


## [8.0.32] — 2026-05-11 — Commercial/Open-Core Boundary Docs Publication (MB-P3-003)

- Added `COMMERCIAL.md` clarifying current OSS-local capabilities versus potential future hosted/cloud/enterprise feature tiers.
- Added `LICENSE_REVIEW.md` with release-oriented licensing and boundary verification checklist guidance.
- Added `docs/commercial/open-core-boundary.md` as canonical boundary reference and linked it from top-level README documentation links and onboarding (`docs/onboarding/getting-started.md`).

## [8.0.31] — 2026-05-11 — Evolution Improvement Workflow + Review Gate (MB-P3-002)

- Added evolution automation scripts in `scripts/evolution/` to generate PR-ready patch/test/eval proposals from failed workflow evidence and enforce no auto-apply/auto-merge defaults.
- Added `.github/workflows/evolution-review.yml` requiring an explicit human-approval marker for evolution-related pull requests.
- Added `docs/workflows/improvement-workflow.md` documenting the end-to-end evolution improvement path and approval gates.

## [8.0.30] — 2026-05-11 — Skill Registry Skeleton + Validation Flow (MB-P3-001)

- Added registry scaffold in `skill_registry/` with README, starter index, and entry template for contributor onboarding.
- Added registry tooling in `scripts/registry/` for CI validation, packaging, lockfile generation, and opt-in publishing (disabled by default).
- Added package/lockfile schemas in `schemas/skill-package.schema.json` and `schemas/skill-lockfile.schema.json`.
- Added contribution templates and governance docs (`skills/CONTRIBUTING.md`, issue templates, PR template, `CODE_OF_CONDUCT.md`) and wired registry validation into `.github/workflows/validate.yml`.


## [8.0.29] — 2026-05-11 — MVP Domain Cognition Modules + Skill Rubrics (MB-P1-007)

- Added `docs/cognition/modules/mvp-domain-cognition-modules.md` with cognition content for sales, finance/accounting, legal/tax, security, HR, knowledge/research, GTM, SDLC, and operations, including principles, heuristics, frameworks, evaluators, anti-pattern detectors, examples, policy boundaries, and memory hooks.
- Added rubric and domain-reference documentation in `docs/cognition/references/self-check-rubric.md` and `docs/reference/domain-cognition-modules.md` to standardize self-check and memory capture behavior.
- Integrated domain cognition self-check sections into relevant domain skills: sales, finance/accounting, legal/tax, security, knowledge/research, GTM, SDLC, and operations skill definitions under `skills/*/SKILL.md`.

## [8.0.28] — 2026-05-11 — Local + Docker Backup/Restore Hardening (MB-P1-006)

- Added local backup/restore tooling in `scripts/backup/backup_local_state.py` and `scripts/backup/restore_local_state.py` with manifest + checksum outputs, dry-run restore preview, and post-restore checksum validation.
- Added Docker stack backup/restore scripts in `scripts/docker/backup-stack.sh` and `scripts/docker/restore-stack.sh` including archive checksum generation and dry-run recovery preview flow.
- Added backup/restore standards and operator guidance in `references/local-backup-restore-standard.md`, `docs/onboarding/DOCKER_BACKUP_RESTORE.md`, and runbook updates for recovery validation and secret handling approvals.

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

- Added a skill maturity framework with explicit MVP thresholds (>70% at L3+, >50% at L4+) and enforced L5 for high-risk critical MVP skills via `scripts/grade_skill_maturity.py`, plus certification evidence reporting via `scripts/certify_skill.py`.


## [8.0.22] — 2026-05-11 — MB-P2-003 Supply-Chain Skill Pack Completion

### Added
- Expanded `inventory-product-market-phase-pack` coverage for demand planning, SKU margin analysis, stockout risk, supplier/vendor risk, procurement routing, and scarcity/arbitrage support.
- Added explicit scraping policy controls requiring robots checks, terms checks, rate-limit enforcement, and operator approval for restricted data collection.

### Changed
- Hardened approval gates for purchase, listing publication, and vendor outreach actions.
- Updated OldFarmTrucks market scarcity workflow fixtures for acquisition/pricing dry-run validation and richer expected artifacts.

- Completed MB-P2-004 legal/tax/entity/regulatory intelligence hardening by enforcing decision-support-only boundaries, authoritative citation policy, structured jurisdiction/authority/effective-date/retrieval-verification/confidence/review fields, and filing/submission approval gates in the legal operations phase pack.
- Added legal-tax governance policy documentation and MB-P2-004 policy tests for citation, schema-field, and action-gating controls.

## 2026-05-11 — MB-ECOM-P0-002 marketplace ingestion and scraping governance

- Added `core/marketplace-ingestion/` with source adapter contract + sample marketplace adapters that preserve retrieval lineage.
- Added `core/scraping-governor/` governance interceptors to enforce legal approval, robots/TOS allowability, and throttle sanity before ingestion.
- Added `schemas/marketplace-source.schema.json` requiring legal metadata, robots/TOS handling declarations, throttling constraints, proxy controls, and lineage fields.
- Added `scripts/marketplaces/validate_source_policy.py` to fail non-compliant source definitions.
- Added `references/marketplace-data-policy.md` and refreshed marketplace/governance docs with policy boundaries, rate limits, proxy rules, and violation behavior.


## [8.0.27] — 2026-05-12 — Ecommerce Listing Ops + Inventory/Catalog + Dashboard

- Added seven listing operations skills with draft-mode outputs and publish approval gates.
- Added catalog/inventory components covering normalization, multi-channel sync, deduplication, SKU relationship analysis, bundles, and reorder threshold analysis.
- Added ecommerce analytics surface via `apps/ecommerce-dashboard/` and profitability/operations reports.
- Standardized required metrics (gross/net margin, sell-through, aging, return rate, shipping/fee ratio, conversion, CAC) with marketplace and SKU segmentation in generated artifacts.

## 2026-05-12 — MB-P3-007 conversation orchestrator state machine + adaptive intake

- Added `core/conversation-orchestrator/` with explicit state model: `idle`, `exploring`, `drafting_plan`, `refining_plan`, `creating_workflow`, `executing_workflow`, `awaiting_approval`, `curating_knowledge`, `scheduling_task`, and `reviewing_results`.
- Implemented transition logic driven by utterances, approvals, corrections, and interruption directives (`pause`, `switch`, `forget`, `resume`).
- Added context tracking for active goal, active artifacts, and resolved questions to prevent repetitive intake.
- Added `references/conversation-state-machine.md`, `references/adaptive-intake-policy.md`, and `templates/conversation-artifact-events.md`.
- Updated orchestration engine documentation with conversation state-machine details.


## 2026-05-12 — Conversation intent router + policy-safe dispatch integration

- Added `scripts/orchestration/route_conversation_intent.py` with explicit message/context input contract and structured routing output contract (`confidence`, `requires_question`, `missing_information`, candidate skills/workflows, and `knowledge_actions`).
- Added support for intent classes: Q&A, brainstorm, create plan/workflow/skill, run skill, schedule task, curate/retrieve knowledge, clarifying question, request approval, and governed execution.
- Integrated policy-safe dispatch hooks to SDLC and GTM planners, runtime executor path references, skill-gap detection, and memory retrieval actions.
- Updated API docs with runnable routing examples.

## 2026-05-12 — Conversation-to-plan pipeline + living Plan Builder + approved-scope converters

- Added `scripts/orchestration/conversation_to_plan.py` to produce human-readable structured plans from conversation input with Plan Builder coverage for objectives, assumptions, phases, tasks, risks, dependencies, required skills, and per-step approvals.
- Added living-plan operations for collapse/expand, priority reorder, assumption edits, individual step approvals, and version diff history.
- Added `scripts/orchestration/plan_to_workflow.py` and `scripts/orchestration/plan_to_tasks.py` to convert approved plan scope into executable workflow/task forms.
- Added plan workspace documentation for users and developers under `docs/plan-workspace/`.

## 2026-05-12 — Task scheduler + governed schedule lifecycle

- Added `core/task-scheduler/` model primitives for task and schedule records with origin/dependency/assignee and approval semantics.
- Added new root `schemas/task.schema.json` and expanded `schemas/schedule.schema.json` to support governed action + approval contracts.
- Integrated scheduling runtime to generate recurring follow-up tasks (`runtime/tasks/`) from due run execution when `generate_task: true`.
- Extended chat CLI schedule lifecycle commands (`create`, `pause`, `archive`) on top of existing preview/run/repair flows.
- Added operational documentation: `docs/reference/task-schedule-operations.md`.

## 2026-05-12 — Workflow dry-run preview + Approval Center + unified approval routing

- Added dry-run preview UX in `apps/assistant-workspace/streamlit_app.py` for Assistant Home/Workflow Studio with step previews, gate visibility, side-effect classes, and missing-input detection before execution.
- Added Approval Center UI with pending queue views, risk reason, policy context, and decision actions (`approve`, `reject`, `edit`, `request detail`).
- Integrated approval decisions with runtime pause/resume audit trails via explicit event recording.
- Unified scheduled and direct execution entrypoints so both route through the same approval and evidence pathways.
- Updated workspace UX and governance runtime docs to reflect the new approval-routing parity contract.
