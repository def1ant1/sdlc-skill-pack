---
name: zero-trust-policy-authoring
description: Authors zero-trust policy definitions, scope declarations, and exception management workflows.
metadata:
  version: "0.1.0"
  category: security
  owner: platform
  maturity: draft
  dependencies: ['zero-trust-runtime', 'governance']
---

## Role

Authors zero-trust policy definitions, scope declarations, and exception management workflows.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires zero trust policy authoring capability
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
  skill: zero-trust-policy-authoring
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
