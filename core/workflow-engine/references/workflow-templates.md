# Workflow Templates

## Built-in Template Registry

All templates are defined in Workflow DSL format (see `references/workflow-dsl.md`).

---

## Template: sdlc-full-cycle

**Purpose**: Execute the complete SDLC flow for a new feature from ticket to deployment.

**Trigger**: New feature ticket in project management system.

**Steps**:
1. `requirements-engineering` — Author PRD and user stories
2. Approval gate (Level-2): PRD review
3. `architecture` (agent) — Architecture review and ADR
4. `ai-engineering` (if AI feature) — LLM integration design
5. `backend-engineering` / `frontend-engineering` — Implementation
6. `qa-automation` — Test coverage verification
7. `code-review` — Review gate
8. `devsecops` — Security scan gate
9. Approval gate (Level-3): Production deployment authorization
10. `release-management` — Deploy to production
11. `observability` — Confirm SLO baseline

---

## Template: incident-response

**Purpose**: Full incident lifecycle from detection to post-mortem.

**Trigger**: P0 or P1 alert declared.

**Steps**:
1. `sre-incident-response` — Declare and classify severity
2. `hitl-dashboard` — Notify on-call and escalation contacts
3. `sre-incident-response` — Diagnose and mitigate
4. `sre-incident-response` — Resolve and communicate
5. `telemetry` — Log resolution metrics
6. `sre-incident-response` — Author post-mortem (48h deadline)

---

## Template: compliance-audit-prep

**Purpose**: Prepare for a scheduled compliance audit.

**Trigger**: Audit date T-90 days.

**Steps**:
1. `compliance-automation` — Pull current evidence inventory
2. `compliance-governance` — Run audit readiness score
3. Approval gate: Review readiness score with compliance owner
4. `compliance-automation` — Fill evidence gaps
5. `compliance-governance` — Verify all policy attestations current
6. `compliance-automation` — Produce audit package

---

## Template: model-promotion

**Purpose**: Evaluate, approve, and promote a LoRA adapter to production.

**Trigger**: `lora.training.completed` event.

**Steps**: See full DSL example in `references/workflow-dsl.md`.

---

## Template: weekly-business-review

**Purpose**: Produce the weekly business review report.

**Trigger**: Friday 17:00 UTC (scheduled).

**Steps**:
1. `product-analytics` — Pull product metrics
2. `revenue-operations` — Pull revenue metrics
3. `customer-success` — Pull customer health data
4. `gtm-orchestration` — Pull GTM metrics
5. `observability` — Pull engineering metrics
6. `executive-reporting` — Synthesize and draft WBR
7. Approval gate (Level-2): Review before distribution
8. `telemetry` — Log report produced

---

## Template: onboard-new-skill

**Purpose**: Validate and activate a new skill added to the registry.

**Trigger**: PR merged adding a new SKILL.md.

**Steps**:
1. `skill-gap-engine` — Validate frontmatter and quality score
2. `governance` — Scope permissions and data access
3. `autonomous-os` — Register in agent registry
4. Approval gate (Level-3): New skill activation authorization
5. `skill-gap-engine` — Mark gap closed (if filling a known gap)
6. `telemetry` — Log skill activation event

---

## Template: vendor-onboard

**Purpose**: Qualify and onboard a new vendor.

**Trigger**: Vendor spend request for unregistered vendor.

**Steps**:
1. `vendor-procurement` — Vendor qualification checklist
2. `legal-ops` — Review/execute DPA (if data processing)
3. `legal-ops` — Review/execute contract
4. Approval gate (Level-2 or Level-3 depending on spend)
5. `accounting-automation` — Create vendor record; issue PO
6. `local-security` — Provision access (if required)
7. `vendor-procurement` — Add to approved vendor registry

---

## Template: new-hire

**Purpose**: Coordinate new employee onboarding.

**Trigger**: Offer letter countersigned.

**Steps**:
1. `workforce-management` — Generate onboarding plan
2. `local-security` — Provision all accounts (parallel with step 3)
3. `accounting-automation` — Add to payroll
4. `meeting-intelligence` — Schedule first-week 1:1s
5. `workflow-engine` — Schedule 30/60/90 day check-in tasks