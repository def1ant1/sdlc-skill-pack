---
name: journal-entry-review
description: Phase 103 business skill using canonical entity/event outputs and policy-gated actions.
metadata:
  version: "9.0.0"
  category: sdlc
  owner: Apotheon
  maturity: beta
  manifest: manifest.v9.json
---

# Journal Entry Review

## Role
Execute journal entry review workflows while producing only canonical entity/event artifacts.

## Routing
- use_when: Request maps to phase 103 capabilities and requires structured decision support.
- do_not_use_when: Task is unrelated to business operations or lacks required tenant policy context.

## Governance
- Always validate outputs against canonical entity/event schemas before emit.
- Require human approval before any customer-facing message or external system mutation.

## Workflow Artifact
See `examples/workflow.yaml`.
