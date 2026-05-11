---
name: accounting-operations
description: Phase 103 business skill using canonical entity/event outputs and policy-gated
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

# Accounting Operations

## Role
Execute accounting operations workflows while producing only canonical entity/event artifacts.

## Routing
- use_when: Request maps to phase 103 capabilities and requires structured decision support.
- do_not_use_when: Task is unrelated to business operations or lacks required tenant policy context.

## Governance
- Always validate outputs against canonical entity/event schemas before emit.
- Require human approval before any customer-facing message or external system mutation.

## Workflow Artifact
See `examples/workflow.yaml`.

## Domain Cognition + Self-Check Integration
- Apply the domain module for **finance/accounting** from `docs/cognition/modules/mvp-domain-cognition-modules.md` before finalizing recommendations.
- Run the self-check rubric in `docs/cognition/references/self-check-rubric.md`.
- If rubric score is below threshold or any blocking dimension is `0`, pause, state gaps, and request/trigger human review.
- Persist memory hooks defined by the module in the output memory packet.

