---
name: finance-accounting-phase-pack
description: Phase-pack skill for finance and accounting workflows with canonical schema outputs and strict approval gates.
metadata:
  version: 9.0.0
  category: business-operations
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
use_when:
- Request spans finance/accounting phases and needs governed workflow orchestration.
do_not_use_when:
- Request is outside finance/accounting scope or required policy context is missing.
---

# Finance & Accounting Phase Pack

## Role
Coordinate finance/accounting workflows across phase 103-105 capabilities using only canonical entity/event artifacts.

## Contracts & Context Loading
- All inputs and outputs must map to canonical schemas declared in `manifest.v9.json`.
- Load context in this order: tenant profile, policy context, canonical entities, then historical events.
- Respect token budgets and emit compact summaries when nearing output limits.

## Governance
- Require human approval before customer-facing communication.
- Require human approval before any external side-effect (ERP mutation, invoice send, payment action).
- If policy checks fail, emit a policy violation event and stop side-effect execution.

## Failure & Fallback
- On missing required context: request context bundle and pause.
- On schema validation failure: emit safe summary plus validation errors.
- On connector timeout: retry once, then create follow-up task.

## Example workflow
See `examples/workflow.yaml`.


## Governance References
- `docs/governance/professional-advice-boundaries.md`
- `docs/governance/financial-controls.md`

## MB-P2-001 Standardization
- Canonical entities for finance pack execution: `account`, `invoice`, `payment`, `approval`, `lineage`, `policy-context`, `task`, and `decision`.
- All child finance skills must structure outputs in four sections: **Observed data**, **Calculations**, **Assumptions**, **Recommendations**.
- Approval gate is mandatory for any payment action, accounting-book mutation, or tax-facing operation.
- Eval suites must assert both calculation correctness and governance/approval enforcement.

## Integration Fixtures
Use fixtures in `tests/fixtures/finance-pack/` to exercise cross-skill flows:
- `forecasting.integration.json`
- `close.integration.json`
- `reconciliation.integration.json`
- `controls.integration.json`

