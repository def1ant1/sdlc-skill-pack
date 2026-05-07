---
name: business-continuity-planning
description: Authors BCPs, runs DR simulations, monitors RTO/RPO targets, and maintains communication plans.
metadata:
  version: "0.1.0"
  category: resilience
  owner: platform
  maturity: draft
  dependencies: ['disaster-recovery-automation', 'governance']
---

## Role

Authors BCPs, runs DR simulations, monitors RTO/RPO targets, and maintains communication plans.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires business continuity planning capability
- Called by orchestration plan referencing this skill as a required step

## Execution Protocol

1. **Receive task context**: Parse the skill invocation payload and validate required fields.
2. **Execute skill workflow**: Apply the domain-specific logic documented in `references/`.
3. **Validate outputs**: Check outputs against quality gates before returning.
4. **Return result**: Emit structured output and telemetry.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: business-continuity-planning
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
