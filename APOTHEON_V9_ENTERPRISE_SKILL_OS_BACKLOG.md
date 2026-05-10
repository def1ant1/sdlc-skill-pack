---
last_updated: 2026-05-10
---

# APOTHEON AI COMPANY OS — V9 ENTERPRISE SKILL OS BACKLOG

**Version:** 9.0.0  
**Status:** READY FOR CODEX IMPLEMENTATION  
**Owner:** Apotheon.ai  
**Purpose:** Convert the existing SDLC/autonomy skill platform into a comprehensive enterprise business operating system with verified implementation, standardized skill contracts, token-efficient orchestration, business-domain skills, enterprise data management, governance, and scalability.

---

## 0. Codex Execution Instructions

Codex must not assume backlog documentation is accurate. For every phase below:

1. Inspect the actual repository filesystem.
2. Verify whether each referenced `core/`, `skills/`, `agents/`, `workflows/`, `scripts/`, `tests/`, and `references/` path exists.
3. Create or update files only where implementation is missing or incomplete.
4. Preserve existing good work and migrate rather than rewrite unnecessarily.
5. Add validation scripts and tests for every new standard.
6. Update this backlog with completion checkboxes only after tests pass.

Definition of done for all phases:

- Every new skill has a valid `SKILL.md`.
- Every new skill has a machine-readable `manifest.yaml` or equivalent frontmatter conforming to the V9 contract.
- Every new skill has explicit context-loading rules and token budget.
- Every new skill has input/output contracts.
- Every new skill has telemetry, governance, evaluation, and failure-mode definitions.
- Every new skill has at least one example workflow or usage scenario.
- Validation scripts pass locally.

---

# 1. V9 Strategic Goal

Transform the repository from an advanced AI/SDLC/runtime skill platform into a complete enterprise skill operating system that supports:

- Business operations
- Marketing
- Sales
- Customer success
- Accounting
- Finance
- FP&A
- Procurement
- Vendor management
- Inventory
- Product operations
- Data collection and analysis
- Market intelligence
- People/HR operations
- Legal/compliance operations
- Executive reporting
- IT/DevOps/CI/CD/SRE
- API integrations
- Applied psychology and stakeholder intelligence
- Orchestration, memory, telemetry, governance, scalability, and token efficiency

---

# 2. Verified Gaps Driving V9

The current repo is strong in runtime, SDLC, AI engineering, distributed execution, governance, and safety. However, the verified gap analysis identified these remaining issues:

1. Business operating function coverage is thin relative to platform ambition.
2. Finance/accounting/inventory/product/procurement skills are not implemented at comparable depth.
3. Enterprise skill contract fields are not consistently present across all skills.
4. Progressive disclosure and token budget policy are not enforced repo-wide.
5. Existing backlog documentation may be stale relative to actual files.
6. Cross-skill dependency and routing-collision detection are missing or incomplete.
7. Business-domain ontology and canonical enterprise entity models are missing or incomplete.
8. Business-action governance is not yet distinct enough from technical permissioning.
9. Evaluation harnesses are not uniformly defined per skill.
10. Runtime cost attribution and token economy need repo-wide instrumentation.

---

# 3. Implementation Waves

| Wave | Theme | Priority | Outcome |
|---|---|---:|---|
| V9-W1 | Repo Truth & Contract Foundation | P0 | Make documentation, filesystem, and skill contracts verifiable |
| V9-W2 | Token Efficiency & Orchestration Hardening | P0 | Reduce token usage and improve routing/scalability |
| V9-W3 | Enterprise Data & Ontology Foundation | P0 | Create canonical entities and business event contracts |
| V9-W4 | Finance & Accounting Skill Pack | P0 | Add CFO-grade operating skills |
| V9-W5 | Sales, Marketing & Customer Skill Pack | P0 | Add GTM/revenue/customer intelligence skills |
| V9-W6 | Inventory, Product & Market Intelligence Skill Pack | P0 | Add supply/product/market operations skills |
| V9-W7 | People, Vendor, Legal & Operations Skill Pack | P1 | Add organizational operating skills |
| V9-W8 | Business Governance & Approval Runtime | P0 | Add business-action policy enforcement |
| V9-W9 | Evaluation, Telemetry & Runtime Economics | P0 | Make quality/cost/outcomes measurable |
| V9-W10 | Skill Lifecycle, Marketplace & Self-Improvement | P1 | Improve skill creation, certification, evolution |

---

# V9-W1 — Repo Truth & Contract Foundation

## Phase 93 — Backlog Truth Checker

**Priority:** P0  
**Gap:** Backlog files can claim phases/skills are complete while actual repo files differ.

### Deliverables

Create:

```text
scripts/validate_backlog_truth.py
scripts/extract_backlog_paths.py
scripts/generate_repo_truth_report.py
reports/repo_truth_report.md
```

### Requirements

- Parse all backlog files matching `*BACKLOG*.md`.
- Extract every referenced path matching:
  - `core/...`
  - `skills/...`
  - `agents/...`
  - `workflows/...`
  - `scripts/...`
  - `tests/...`
  - `references/...`
- Verify whether each path exists.
- Verify each skill directory has required files.
- Detect stale claims such as "DONE" but missing implementation.
- Output a markdown report and JSON report.

### Acceptance Criteria

- `python scripts/validate_backlog_truth.py` exits nonzero on missing required files.
- Report groups findings by backlog file, phase, path, and severity.
- False positives can be suppressed through `.backlog-truth-ignore.yaml`.

---

## Phase 94 — V9 Universal Skill Contract

**Priority:** P0  
**Gap:** Skills lack a consistent machine-readable operating contract.

### Deliverables

Create:

```text
schemas/skill-manifest-v9.schema.json
references/skill-contract-v9.md
scripts/validate_skill_contracts.py
scripts/migrate_frontmatter_to_manifest.py
```

### Required Contract Fields

```yaml
name:
type: core | skill | agent | workflow
domain:
subdomain:
version:
owner:
maturity:
dependencies:
activation_triggers:
required_context:
optional_context:
input_contract:
output_contract:
memory_policy:
token_budget:
context_loading:
governance_level:
human_approval_required:
execution_mode:
latency_target:
cost_target:
determinism_level:
telemetry_events:
eval_metrics:
security_classification:
integration_targets:
data_contracts:
failure_modes:
fallbacks:
```

### Acceptance Criteria

- Every `core/*`, `skills/*`, and `agents/*` directory containing `SKILL.md` has a valid V9 manifest or equivalent frontmatter.
- `python scripts/validate_skill_contracts.py` passes.
- Missing optional fields receive explicit `null` or empty-list values, not implicit absence.
- ✅ Implemented: backlog truth extraction/validation/reporting scripts and tests.
- ✅ Implemented: V9 schema, migration, inventory generation, and reports.

---

## Phase 95 — Skill Inventory Generator

**Priority:** P0

### Deliverables

Create:

```text
scripts/generate_skill_inventory.py
reports/skill_inventory.json
reports/skill_inventory.md
reports/skill_inventory.csv
```

### Requirements

Inventory must include:

- Skill name
- Type
- Domain/subdomain
- Maturity
- Dependencies
- Inputs/outputs
- Token budget
- Governance level
- Human approval requirement
- Telemetry events
- Evaluation metrics
- Integration targets
- Missing required assets

### Acceptance Criteria

- Inventory regenerates deterministically.
- Inventory can be used by Codex or Claude Code to select skills without loading entire repository context.

---

# V9-W2 — Token Efficiency & Orchestration Hardening

## Phase 96 — Progressive Disclosure Standard

**Priority:** P0

### Deliverables

Create:

```text
references/progressive-disclosure-standard.md
schemas/context-loading.schema.json
scripts/check_context_budget.py
```

### Required Context Levels

```yaml
context_loading:
  default_level: L1
  l1_max_tokens: 1200
  l2_max_tokens: 6000
  l3_max_tokens: 20000
  l1_files:
    - SKILL.md frontmatter
    - manifest.yaml
  l2_files:
    - workflows/*.yaml
    - templates/*.md
    - contracts/*.yaml
  l3_files:
    - references/*.md
    - examples/*
    - research/*
```

### Acceptance Criteria

- Every skill declares `context_loading`.
- CI fails when default context exceeds the declared token budget.
- References are not loaded by default unless specifically requested.

---

## Phase 97 — Skill Router & Routing Collision Audit

**Priority:** P0

### Deliverables

Create or update:

```text
core/skill-router/
skills/routing-collision-analysis/
scripts/detect_skill_overlap.py
reports/routing_collision_report.md
```

### Requirements

- Detect overlapping activation triggers.
- Detect duplicate capabilities.
- Detect circular dependencies.
- Detect ambiguous domain ownership.
- Recommend primary/secondary skill routing.

### Acceptance Criteria

- A routing collision report is generated.
- Each collision has a recommended remediation.
- Skill manifests include `use_when` and `do_not_use_when` guidance.

---

## Phase 98 — Semantic Cache & Context Reuse Layer

**Priority:** P0

### Deliverables

Create or update:

```text
core/semantic-cache/
skills/context-reuse-optimization/
references/semantic-cache-policy.md
```

### Requirements

- Cache deterministic intermediate outputs.
- Support cache invalidation by data lineage, TTL, and source revision.
- Avoid repeated retrieval/generation for repeated workflows.
- Track token savings.

### Acceptance Criteria

- Cache policy defines safe/unsafe cacheable outputs.
- Telemetry includes estimated tokens saved.

---

## Phase 99 — Dependency Graph & Orchestration Map

**Priority:** P0

### Deliverables

Create:

```text
scripts/generate_dependency_graph.py
reports/skill_dependency_graph.json
reports/skill_dependency_graph.mmd
reports/orchestration_map.md
```

### Acceptance Criteria

- Graph includes all core, skill, and agent nodes.
- Graph identifies roots, leaves, cycles, and orphaned skills.
- Mermaid graph renders in GitHub markdown.

---

# V9-W3 — Enterprise Data & Ontology Foundation

## Phase 100 — Canonical Enterprise Entity Model

**Priority:** P0

### Deliverables

Create:

```text
core/canonical-entity-model/
core/business-event-model/
core/data-contract-registry/
schemas/entities/
schemas/events/
references/enterprise-ontology.md
```

### Required Entities

```text
Account
Customer
Lead
Contact
Opportunity
Invoice
Payment
Expense
Budget
Forecast
Vendor
PurchaseOrder
Contract
SKU
Product
InventoryItem
Warehouse
Shipment
Ticket
Campaign
Employee
Role
Project
Initiative
Risk
Control
Asset
DataSource
WorkflowRun
Agent
Decision
```

### Acceptance Criteria

- Each entity has a JSON schema.
- Each entity has ownership, source-of-record, lineage, and privacy classification fields.
- Cross-domain skills reference these schemas instead of inventing local formats.

---

## Phase 101 — Business Event Model

**Priority:** P0

### Deliverables

Create schemas for events:

```text
invoice.created
invoice.paid
payment.failed
opportunity.stage_changed
lead.qualified
customer.health_changed
inventory.low_stock
purchase_order.approved
vendor.risk_changed
ticket.escalated
campaign.launched
budget.variance_detected
forecast.updated
workflow.completed
agent.recommendation_created
business_policy.violation
```

### Acceptance Criteria

- Events include actor, timestamp, source system, confidence, lineage, and policy context.
- Event schemas are referenced by telemetry/governance/business skills.

---

## Phase 102 — Master Data Management Runtime

**Priority:** P1

### Deliverables

Create or update:

```text
core/master-data-management/
skills/entity-resolution/
skills/golden-record-management/
skills/data-quality-scoring/
```

### Acceptance Criteria

- Supports deduplication and survivorship rules.
- Defines golden record policies for customer, vendor, product, and employee.
- Emits data quality metrics.

---

# V9-W4 — Finance & Accounting Skill Pack

## Phase 103 — Accounting Operations Core

**Priority:** P0

### New Skills

```text
skills/accounting-operations/
skills/bookkeeping-automation/
skills/chart-of-accounts-management/
skills/journal-entry-review/
skills/month-end-close-support/
skills/reconciliation-automation/
```

### Capabilities

- Transaction classification
- Chart of accounts mapping
- Journal entry review
- Account reconciliation
- Month-end close checklist generation
- Exception detection

### Acceptance Criteria

- Skills use accounting best practices and internal control concepts.
- High-risk accounting actions require human approval.
- Outputs include audit trail and confidence score.

---

## Phase 104 — AP/AR Automation

**Priority:** P0

### New Skills

```text
skills/accounts-payable-automation/
skills/accounts-receivable-automation/
skills/invoice-processing/
skills/collections-prioritization/
skills/payment-matching/
```

### Acceptance Criteria

- Supports invoice extraction, validation, duplicate detection, payment matching, and collection prioritization.
- Requires approval before initiating payment or customer communication.
- Uses canonical Invoice, Payment, Vendor, Customer schemas.

---

## Phase 105 — FP&A and Cash Intelligence

**Priority:** P0

### New Skills

```text
skills/cash-flow-forecasting/
skills/fpa-analysis/
skills/budget-variance-analysis/
skills/financial-scenario-modeling/
skills/runway-analysis/
skills/revenue-leakage-detection/
```

### Acceptance Criteria

- Provides rolling forecasts.
- Supports scenario modeling.
- Detects budget variance and revenue leakage.
- Produces CFO-ready executive summary and assumptions log.

---

## Phase 106 — Payroll, Tax and Compliance Support

**Priority:** P1

### New Skills

```text
skills/payroll-audit/
skills/tax-planning-support/
skills/expense-policy-compliance/
skills/financial-control-monitoring/
```

### Acceptance Criteria

- Clearly marks outputs as support, not professional legal/tax advice.
- Flags exceptions and required expert review.
- Integrates with business policy engine.

---

# V9-W5 — Sales, Marketing & Customer Skill Pack

## Phase 107 — Sales & Revenue Operations

**Priority:** P0

### New Skills

```text
skills/sales-pipeline-forecasting/
skills/lead-scoring/
skills/opportunity-risk-analysis/
skills/proposal-automation/
skills/pricing-optimization/
skills/win-loss-analysis/
skills/account-expansion-intelligence/
```

### Acceptance Criteria

- Uses CRM schemas and Opportunity/Lead/Account canonical entities.
- Produces explainable scoring with confidence and evidence.
- Requires human approval before customer-facing outbound communication.

---

## Phase 108 — Marketing Intelligence

**Priority:** P0

### New Skills

```text
skills/marketing-attribution/
skills/campaign-optimization/
skills/seo-intelligence/
skills/content-strategy/
skills/brand-sentiment-analysis/
skills/persona-modeling/
skills/conversion-funnel-analysis/
```

### Acceptance Criteria

- Supports campaign KPIs, attribution assumptions, audience segmentation, and content recommendations.
- Avoids ungrounded claims about market data.
- Integrates with data collection and analytics workflows.

---

## Phase 109 — Customer Operations

**Priority:** P0

### New Skills

```text
skills/customer-health-scoring/
skills/churn-risk-detection/
skills/support-ticket-intelligence/
skills/sla-risk-detection/
skills/voice-of-customer-analysis/
skills/customer-journey-mapping/
skills/escalation-prediction/
```

### Acceptance Criteria

- Uses Ticket, Customer, Contract, and Account schemas.
- Produces ranked intervention recommendations.
- Requires approval before customer outreach.

---

# V9-W6 — Inventory, Product & Market Intelligence Skill Pack

## Phase 110 — Inventory & Supply Chain Intelligence

**Priority:** P0

### New Skills

```text
skills/inventory-forecasting/
skills/demand-planning/
skills/low-stock-detection/
skills/reorder-point-optimization/
skills/warehouse-optimization/
skills/supplier-risk-intelligence/
skills/purchase-order-optimization/
```

### Acceptance Criteria

- Uses SKU, Product, InventoryItem, Warehouse, Vendor, PurchaseOrder schemas.
- Produces reorder recommendations with assumptions.
- Requires approval before purchase order creation or modification.

---

## Phase 111 — Product Operations Intelligence

**Priority:** P0

### New Skills

```text
skills/product-lifecycle-intelligence/
skills/sku-margin-analysis/
skills/feature-prioritization/
skills/product-feedback-analysis/
skills/roadmap-impact-analysis/
skills/product-market-fit-analysis/
```

### Acceptance Criteria

- Links product decisions to margin, customer feedback, roadmap, and strategic goals.
- Produces tradeoff analysis.
- Integrates with product analytics and customer intelligence.

---

## Phase 112 — Local Market & Scarcity Intelligence

**Priority:** P0

### New Skills

```text
skills/local-market-data-collection/
skills/competitor-price-scraping/
skills/scarcity-analysis/
skills/market-pricing-intelligence/
skills/arbitrage-opportunity-detection/
skills/market-data-quality-scoring/
```

### Governance Requirements

- Respect robots.txt, site terms, rate limits, and applicable laws.
- Store source URL, timestamp, extraction method, and confidence.
- Never bypass access controls.
- Clearly separate observed data from inferred analysis.

### Acceptance Criteria

- Includes scraping policy document.
- Includes data quality scoring.
- Includes scarcity/pricing dashboard output schema.

---

# V9-W7 — People, Vendor, Legal & Operations Skill Pack

## Phase 113 — People & HR Operations

**Priority:** P1

### New Skills

```text
skills/workforce-planning/
skills/hiring-pipeline-intelligence/
skills/interview-scorecard-analysis/
skills/employee-performance-coaching/
skills/burnout-risk-detection/
skills/learning-path-optimization/
skills/org-design-analysis/
```

### Acceptance Criteria

- Uses human-sensitive governance and bias controls.
- Does not make final employment decisions autonomously.
- Requires human review for high-impact HR recommendations.

---

## Phase 114 — Procurement & Vendor Operations

**Priority:** P1

### New Skills

```text
skills/procurement-automation/
skills/vendor-scorecarding/
skills/vendor-risk-analysis/
skills/contract-renewal-intelligence/
skills/spend-analysis/
skills/purchase-approval-routing/
```

### Acceptance Criteria

- Uses Vendor, Contract, PurchaseOrder, Budget schemas.
- Applies approval thresholds.
- Produces cost/risk/reliability scoring.

---

## Phase 115 — Legal & Contract Operations

**Priority:** P1

### New Skills

```text
skills/contract-review-support/
skills/clause-risk-analysis/
skills/legal-obligation-tracking/
skills/compliance-evidence-collection/
skills/policy-document-analysis/
```

### Acceptance Criteria

- Outputs are legal support, not legal advice.
- Flags need for attorney review.
- Tracks obligations and renewal dates.

---

## Phase 116 — General Business Process Optimization

**Priority:** P1

### New Skills

```text
skills/process-mining/
skills/workflow-optimization/
skills/sop-generation/
skills/kpi-design/
skills/operational-bottleneck-analysis/
skills/root-cause-analysis/
```

### Acceptance Criteria

- Produces current-state and future-state process maps.
- Links recommendations to measurable KPIs.
- Integrates with workflow runtime.

---

# V9-W8 — Business Governance & Approval Runtime

## Phase 117 — Business Policy Engine

**Priority:** P0

### Deliverables

Create:

```text
core/business-policy-engine/
schemas/business-policy.schema.json
references/business-policy-standard.md
```

### Required Policy Categories

- Financial approval thresholds
- Payment authorization
- Procurement approval
- Customer communication approval
- Payroll/HR high-impact decision review
- Legal/tax expert review
- Data usage and scraping policy
- External system mutation policy

### Acceptance Criteria

- Policies are machine-readable.
- Skills declare which policies they invoke.
- Policy violations emit `business_policy.violation` events.

---

## Phase 118 — Human Approval Gateway for Business Actions

**Priority:** P0

### Deliverables

Create or update:

```text
core/business-approval-gateway/
skills/approval-policy-authoring/
skills/approval-queue-management/
```

### Acceptance Criteria

- External side effects can be blocked pending approval.
- Approval records include actor, reason, evidence, timestamp, and decision.
- Supports approve/reject/request-more-information.

---

## Phase 119 — Business Audit Trail & Evidence Ledger

**Priority:** P0

### Deliverables

Create:

```text
core/business-audit-ledger/
skills/evidence-pack-generation/
skills/audit-trail-analysis/
```

### Acceptance Criteria

- Records business decisions, recommendations, approvals, policy checks, and source evidence.
- Supports exportable evidence packs for finance, compliance, and executive review.

---

# V9-W9 — Evaluation, Telemetry & Runtime Economics

## Phase 120 — Skill Evaluation Harness Standard

**Priority:** P0

### Deliverables

Create:

```text
schemas/skill-eval.schema.json
references/skill-evaluation-standard.md
scripts/validate_skill_evals.py
```

### Required Eval Types

- Output schema validity
- Hallucination/grounding check
- Business KPI relevance
- Safety/governance compliance
- Token/cost budget compliance
- Regression examples
- Human review rubric where needed

### Acceptance Criteria

- Every P0/P1 skill has an evaluation specification.
- Validation fails if required evals are missing.

---

## Phase 121 — Telemetry Standardization

**Priority:** P0

### Deliverables

Create or update:

```text
schemas/telemetry-event.schema.json
references/telemetry-standard.md
scripts/validate_telemetry_events.py
```

### Required Metrics

```yaml
execution_time_ms:
token_usage:
estimated_cost:
success_rate:
retry_count:
confidence_score:
hallucination_risk:
human_intervention_required:
business_outcome:
policy_checks:
source_quality:
cache_hit:
```

### Acceptance Criteria

- Every skill declares telemetry events.
- Runtime and business events share correlation IDs.

---

## Phase 122 — Runtime Economics & Token Cost Attribution

**Priority:** P0

### Deliverables

Create or update:

```text
core/runtime-economics/
skills/token-cost-analysis/
skills/roi-estimation/
reports/runtime_economics_dashboard.schema.json
```

### Acceptance Criteria

- Cost can be attributed by skill, workflow, agent, tenant, and business domain.
- Reports include token savings from cache/context optimization.
- Skills can be ranked by value/cost ratio.

---

# V9-W10 — Skill Lifecycle, Marketplace & Self-Improvement

## Phase 123 — Skill Factory V9 Upgrade

**Priority:** P1

### Deliverables

Create or update:

```text
skills/skill-factory-v9/
skills/skill-gap-detection/
skills/skill-refactoring/
skills/skill-composition/
```

### Acceptance Criteria

- New skills are generated from the V9 contract.
- Skill gap detector compares desired capabilities to actual filesystem inventory.
- Skill refactoring detects duplication and stale references.

---

## Phase 124 — Marketplace Certification Gate

**Priority:** P1

### Deliverables

Create or update:

```text
skills/marketplace-certification/
scripts/certify_skill.py
references/marketplace-certification-v9.md
```

### Acceptance Criteria

Certification requires:

- Valid V9 manifest
- Passing evals
- Passing security policy
- Passing context budget check
- Passing telemetry contract validation
- No unresolved routing collision

---

## Phase 125 — Self-Improving Workflow Optimization

**Priority:** P1

### Deliverables

Create or update:

```text
skills/workflow-optimization-loop/
skills/outcome-feedback-analysis/
skills/prompt-variant-testing/
skills/routing-policy-optimization/
```

### Acceptance Criteria

- Workflow variants can be evaluated using business outcome metrics.
- Recommendations are generated for prompt/routing/workflow changes.
- Autonomous changes require policy-defined approval.

---

# 4. Codex Task Bundle Order

Codex should execute in this order:

1. Phase 93 — Backlog truth checker
2. Phase 94 — V9 skill contract
3. Phase 95 — Skill inventory generator
4. Phase 96 — Progressive disclosure standard
5. Phase 99 — Dependency graph
6. Phase 97 — Routing collision audit
7. Phase 100 — Canonical entity model
8. Phase 101 — Business event model
9. Phase 117 — Business policy engine
10. Phase 118 — Business approval gateway
11. Phase 120 — Skill evaluation standard
12. Phase 121 — Telemetry standard
13. Phase 122 — Runtime economics
14. Phase 103–106 — Finance/accounting pack
15. Phase 107–109 — Sales/marketing/customer pack
16. Phase 110–112 — Inventory/product/market pack
17. Phase 113–116 — People/vendor/legal/process pack
18. Phase 123–125 — Skill lifecycle/self-improvement

---

# 5. Required CI Gates

Add CI or local validation commands equivalent to:

```bash
python scripts/validate_backlog_truth.py
python scripts/validate_skill_contracts.py
python scripts/check_context_budget.py
python scripts/generate_skill_inventory.py
python scripts/generate_dependency_graph.py
python scripts/detect_skill_overlap.py
python scripts/validate_skill_evals.py
python scripts/validate_telemetry_events.py
```

All must pass before marking V9 complete.

---

# 6. Final V9 Acceptance Criteria

V9 is complete when:

- All existing skills are migrated to the V9 contract.
- Business-domain skill packs exist and pass validation.
- Finance, sales, marketing, customer, inventory, product, procurement, people, legal, and process skills are implemented.
- Token/context budget rules are enforced.
- Backlog claims are verified against actual files.
- Dependency and overlap reports are generated.
- Canonical enterprise entities and events exist.
- Business policy and approval controls exist.
- Evaluation, telemetry, and runtime economics standards are enforced.
- Skill inventory can drive routing without loading the full repository.
- Codex can use this backlog as a deterministic implementation plan.

### Phase 96 — Progressive Disclosure + Routing/Cache Hardening (2026-05-10)

- ✅ Added `references/progressive-disclosure-standard.md` and `schemas/context-loading.schema.json`.
- ✅ Added `scripts/check_context_budget.py` to enforce L1/L2/L3 and default-level conformance.
- ✅ Added dependency graph generation via `scripts/generate_dependency_graph.py` with outputs in `reports/`.
- ✅ Added routing overlap analysis via `scripts/detect_skill_overlap.py` and `reports/routing_collision_report.md`.
- ✅ Added scaffolds: `core/skill-router/`, `skills/routing-collision-analysis/`, `core/semantic-cache/`, `skills/context-reuse-optimization/`.
- ✅ Added `references/semantic-cache-policy.md` with safe/unsafe classes, invalidation, TTL, and lineage constraints.
- ✅ Normalized `use_when` and `do_not_use_when` manifest fields across core/skills SKILL frontmatter; added telemetry contract hooks for token savings and cache-hit rates.
