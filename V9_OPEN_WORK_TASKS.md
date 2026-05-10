# V9 Open Work Task Plan (Repo-Verified)

Generated from analysis of `APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md` against the current repository filesystem.

## Snapshot

- Total backlog phases analyzed: **33** (Phase 93–125)
- Referenced deliverable paths detected in backlog code blocks: **198**
- Existing deliverable paths: **2**
  - `core/master-data-management`
  - `core/runtime-economics`
- Missing deliverable paths: **196**

## Execution Order Task List

### Wave V9-W1 — Repo Truth & Contract Foundation

- [ ] **Phase 93: Backlog Truth Checker**
  - [ ] Implement `scripts/extract_backlog_paths.py` (path extraction by phase/backlog file)
  - [ ] Implement `scripts/validate_backlog_truth.py` (non-zero exit on missing required assets)
  - [ ] Implement `scripts/generate_repo_truth_report.py` (markdown + JSON report generation)
  - [ ] Add `reports/repo_truth_report.md` generation target
  - [ ] Add ignore support via `.backlog-truth-ignore.yaml`
  - [ ] Add tests for parsing, suppression rules, and stale-claim detection

- [ ] **Phase 94: V9 Universal Skill Contract**
  - [ ] Create `schemas/skill-manifest-v9.schema.json`
  - [ ] Create `references/skill-contract-v9.md`
  - [ ] Implement `scripts/validate_skill_contracts.py`
  - [ ] Implement `scripts/migrate_frontmatter_to_manifest.py`
  - [ ] Migrate all skill-like directories containing `SKILL.md` to V9 manifest/frontmatter compatibility
  - [ ] Add test coverage for required/optional field enforcement

- [ ] **Phase 95: Skill Inventory Generator**
  - [ ] Implement `scripts/generate_skill_inventory.py`
  - [ ] Generate `reports/skill_inventory.{json,md,csv}` deterministically
  - [ ] Validate inventory fields (domain/subdomain, budgets, governance, I/O, telemetry/evals)

### Wave V9-W2 — Token Efficiency & Orchestration Hardening

- [ ] **Phase 96: Progressive Disclosure Standard**
  - [ ] Create `references/progressive-disclosure-standard.md`
  - [ ] Create `schemas/context-loading.schema.json`
  - [ ] Implement `scripts/check_context_budget.py`
  - [ ] Enforce context/token-level checks in CI/local gates

- [ ] **Phase 97: Skill Router & Routing Collision Audit**
  - [ ] Create `core/skill-router/`
  - [ ] Create `skills/routing-collision-analysis/`
  - [ ] Implement `scripts/detect_skill_overlap.py`
  - [ ] Generate `reports/routing_collision_report.md`
  - [ ] Add manifest guidance fields: `use_when`, `do_not_use_when`

- [ ] **Phase 98: Semantic Cache & Context Reuse Layer**
  - [ ] Create `core/semantic-cache/`
  - [ ] Create `skills/context-reuse-optimization/`
  - [ ] Create `references/semantic-cache-policy.md`
  - [ ] Add token-savings telemetry hooks

- [ ] **Phase 99: Dependency Graph & Orchestration Map**
  - [ ] Implement `scripts/generate_dependency_graph.py`
  - [ ] Generate `reports/skill_dependency_graph.json`
  - [ ] Generate `reports/skill_dependency_graph.mmd`
  - [ ] Generate `reports/orchestration_map.md`

### Wave V9-W3 — Enterprise Data & Ontology Foundation

- [ ] **Phase 100: Canonical Enterprise Entity Model**
  - [ ] Create `core/canonical-entity-model/`
  - [ ] Create `core/business-event-model/`
  - [ ] Create `core/data-contract-registry/`
  - [ ] Create `schemas/entities/` and JSON schemas for all required entities
  - [ ] Create `schemas/events/` and cross-link entity usage
  - [ ] Create `references/enterprise-ontology.md`

- [ ] **Phase 101: Business Event Model**
  - [ ] Add event schemas for all required events (`invoice.created`, `workflow.completed`, `business_policy.violation`, etc.)
  - [ ] Ensure actor/timestamp/source/confidence/lineage/policy context in every event schema

- [ ] **Phase 102: Master Data Management Runtime**
  - [ ] Create `skills/entity-resolution/`
  - [ ] Create `skills/golden-record-management/`
  - [ ] Create `skills/data-quality-scoring/`
  - [ ] Integrate with existing `core/master-data-management/`

### Waves V9-W4 to V9-W7 — Business Skill Pack Buildout

- [ ] **Phase 103–116: Create missing business-domain skills**
  - [ ] Add missing skill directories and baseline `SKILL.md` + V9 manifests for all listed phases
  - [ ] Implement core contracts, context rules, token budgets, governance controls, eval specs, telemetry declarations
  - [ ] Add at least one workflow/example per skill
  - [ ] Add validation tests for each pack (finance, GTM, inventory/product/market, people/vendor/legal/process)

### Wave V9-W8 — Business Governance & Approval Runtime

- [ ] **Phase 117: Business Policy Engine**
  - [ ] Create `core/business-policy-engine/`
  - [ ] Create `schemas/business-policy.schema.json`
  - [ ] Create `references/business-policy-standard.md`

- [ ] **Phase 118: Human Approval Gateway for Business Actions**
  - [ ] Create `core/business-approval-gateway/`
  - [ ] Create `skills/approval-policy-authoring/`
  - [ ] Create `skills/approval-queue-management/`

- [ ] **Phase 119: Business Audit Trail & Evidence Ledger**
  - [ ] Create `core/business-audit-ledger/`
  - [ ] Create `skills/evidence-pack-generation/`
  - [ ] Create `skills/audit-trail-analysis/`

### Wave V9-W9 — Evaluation, Telemetry & Runtime Economics

- [ ] **Phase 120: Skill Evaluation Harness Standard**
  - [ ] Create `schemas/skill-eval.schema.json`
  - [ ] Create `references/skill-evaluation-standard.md`
  - [ ] Implement `scripts/validate_skill_evals.py`

- [ ] **Phase 121: Telemetry Standardization**
  - [ ] Create `schemas/telemetry-event.schema.json`
  - [ ] Create `references/telemetry-standard.md`
  - [ ] Implement `scripts/validate_telemetry_events.py`

- [ ] **Phase 122: Runtime Economics & Token Cost Attribution**
  - [ ] Create `skills/token-cost-analysis/`
  - [ ] Create `skills/roi-estimation/`
  - [ ] Create `reports/runtime_economics_dashboard.schema.json`
  - [ ] Integrate with existing `core/runtime-economics/`

### Wave V9-W10 — Skill Lifecycle, Marketplace & Self-Improvement

- [ ] **Phase 123: Skill Factory V9 Upgrade**
  - [ ] Create `skills/skill-factory-v9/`
  - [ ] Create `skills/skill-gap-detection/`
  - [ ] Create `skills/skill-refactoring/`
  - [ ] Create `skills/skill-composition/`

- [ ] **Phase 124: Marketplace Certification Gate**
  - [ ] Create `skills/marketplace-certification/`
  - [ ] Create `scripts/certify_skill.py`
  - [ ] Create `references/marketplace-certification-v9.md`

- [ ] **Phase 125: Self-Improving Workflow Optimization**
  - [ ] Create `skills/workflow-optimization-loop/`
  - [ ] Create `skills/outcome-feedback-analysis/`
  - [ ] Create `skills/prompt-variant-testing/`
  - [ ] Create `skills/routing-policy-optimization/`

## CI Gate Tasks (Required)

- [ ] Add/verify commands in local validation and CI:
  - `python scripts/validate_backlog_truth.py`
  - `python scripts/validate_skill_contracts.py`
  - `python scripts/check_context_budget.py`
  - `python scripts/generate_skill_inventory.py`
  - `python scripts/generate_dependency_graph.py`
  - `python scripts/detect_skill_overlap.py`
  - `python scripts/validate_skill_evals.py`
  - `python scripts/validate_telemetry_events.py`

## Suggested Implementation Batching

- [ ] **Batch A (P0 infra):** 93, 94, 95, 96, 99, 97
- [ ] **Batch B (P0 ontology+governance):** 100, 101, 117, 118
- [ ] **Batch C (P0 quality+economics):** 120, 121, 122
- [ ] **Batch D (P0 business packs):** 103–105, 107–112
- [ ] **Batch E (P1 expansion):** 102, 106, 113–116, 123–125

