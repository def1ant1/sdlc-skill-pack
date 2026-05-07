---
name: disaster-recovery-automation
description: Executes DR runbooks, automates cross-region failover, runs chaos testing, and validates recovery.
metadata:
  version: "0.1.0"
  category: resilience
  owner: platform
  maturity: draft
  dependencies: ['runtime-recovery', 'cluster-management']
---

## Role

Executes DR runbooks, automates cross-region failover, runs chaos testing, and validates recovery.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires disaster recovery automation capability
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
  skill: disaster-recovery-automation
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
