---
name: lateral-movement-detection
description: Detects anomalous access patterns across agent execution graphs indicative of lateral movement.
metadata:
  version: "0.1.0"
  category: security
  owner: platform
  maturity: draft
  dependencies: ['zero-trust-runtime', 'telemetry']
---

## Role

Detects anomalous access patterns across agent execution graphs indicative of lateral movement.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires lateral movement detection capability
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
  skill: lateral-movement-detection
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
