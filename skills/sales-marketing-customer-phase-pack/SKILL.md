---
name: sales-marketing-customer-phase-pack
description: Phase-pack skill for sales, marketing, and customer operations with canonical schema outputs and HITL safeguards.
metadata:
  version: 9.0.0
  category: go-to-market
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
use_when:
- Request spans sales/marketing/customer phases and needs policy-governed execution.
do_not_use_when:
- Request is unrelated to sales, marketing, or customer lifecycle operations.
---

# Sales, Marketing & Customer Phase Pack

## Role
Orchestrate phase 107-109 workflows while outputting only canonical entities/events.

## Contracts & Context Loading
- Validate all artifacts against canonical schema refs in `manifest.v9.json`.
- Context loading order: account + lead/customer entities, policy context, campaign/sales history.
- Apply token budgets; fall back to concise action plans when budget risk is high.

## Governance
- Human approval required for outbound customer communications.
- Human approval required for CRM/helpdesk mutations and external campaign actions.
- Emit approval events before execution and approval_decided events after review.

## Failure & Fallback
- Missing context -> request bounded context packet.
- Policy denied -> emit business_policy_violation and halt mutations.
- Low confidence decision -> escalate to human with alternatives.

## Example workflow
See `examples/workflow.yaml`.


## Governance References
- `docs/governance/external-action-policy.md`
