---
name: prompt-variant-testing
description: Prompt Variant Testing skill for SDLC skill-pack operations.
metadata:
  version: 0.1.0
  category: operations
  owner: Apotheon.ai
  maturity: beta
use_when:
- Request clearly matches this skill's domain capabilities.
do_not_use_when:
- Request is outside this skill's domain or lacks required context.
---

# Prompt Variant Testing

## Mission

Provide structured execution for prompt variant testing workflows.

## Workflow

1. Validate objective and prerequisites.
2. Gather required context and constraints.
3. Execute skill-specific analysis and recommendation steps.
4. Enforce governance and safety controls before mutation.
5. Emit outcome, telemetry, and next actions.


## Certification & Governance Gates

- Enforce marketplace prerequisites before certifying or promoting outcomes: valid `manifest.v9.json`, eval pass, security/context/telemetry pass, and zero unresolved routing collisions.
- Autonomous optimization outputs are advisory only until policy-defined approval is recorded (approval decision, actor, timestamp, policy id/version, and audit event).
