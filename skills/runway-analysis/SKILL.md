---
name: runway-analysis
description: Phase 105 business skill using canonical entity/event outputs and policy-gated
  actions.
metadata:
  version: 9.0.0
  category: sdlc
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
use_when:
- Request clearly matches this skill's domain capabilities.
do_not_use_when:
- Request is outside this skill's domain or lacks required context.
---

# Runway Analysis

## Role
Execute runway analysis workflows while producing only canonical entity/event artifacts.

## Routing
- use_when: Request maps to phase 105 capabilities and requires structured decision support.
- do_not_use_when: Task is unrelated to business operations or lacks required tenant policy context.

## Governance
- Always validate outputs against canonical entity/event schemas before emit.
- Require human approval before any customer-facing message or external system mutation.

## Workflow Artifact
See `examples/workflow.yaml`.

## Canonical finance entities
- Primary entities: `account`, `invoice`, `payment`, `lineage`, `approval`, `policy-context`, `task`, and `decision`.
- Optional entities by workflow: `vendor`, `customer`, `subscription`, `order`, and `contract`.
- Every financial output must preserve source lineage and emit canonical IDs for entity joins.

## Standardized financial output sections
- **Observed data**: source records, freshness timestamps, lineage, and data quality exceptions.
- **Calculations**: explicit formulas, computed values, tolerances, and reconciliation diffs.
- **Assumptions**: scenario assumptions, accounting policy choices, and uncertainty notes.
- **Recommendations**: prioritized actions, owner, due date, and expected financial impact.

## Approval gates for high-risk actions
- Any **payment**, **accounting-book update** (journal posting, close sign-off, ledger mutation), or **tax-facing** action must pause for human approval before execution.
- Emit `approval_requested` before blocked actions and `approval_decided` before any follow-on action.
- If approval is denied or missing, report must continue in analysis-only mode with no side effects.

## Governance-aware evaluation requirements
- Evals must include calculation-correctness datasets with expected numeric outputs and tolerance assertions.
- Evals must include governance-negative datasets that confirm approval gating and policy blocking behavior.
- Passing criteria requires both numeric correctness and governance compliance gates to pass.
