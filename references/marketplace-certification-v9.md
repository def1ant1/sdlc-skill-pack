# Marketplace Certification v9 Standard

## Objective

Define deterministic certification rules for publishing and operating skills in the marketplace.

## Required Prerequisites

- **Manifest validity**: `manifest.v9.json` exists and required keys are present.
- **Eval pass**: `eval_passed=true` and score meets threshold.
- **Security check**: no high-severity unresolved findings.
- **Context check**: required context contract is complete.
- **Telemetry check**: required telemetry events declared.
- **Routing collision check**: unresolved collisions count equals zero.

## Production Mutation Governance

Autonomous optimization outputs are advisory unless policy approval is granted.

Required controls before production mutation:

1. Policy identifier and version are supplied.
2. Approval decision equals `approved`.
3. Approval actor and timestamp are present.
4. Audit event `production_mutation_approved` is emitted.

If any control is missing, status must remain `approval_required` and no mutation occurs.
