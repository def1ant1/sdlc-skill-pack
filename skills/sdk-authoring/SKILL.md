---
name: sdk-authoring
description: Provides SDK scaffolding and authoring workflows for building, testing, and packaging third-party Enterprise OS skills and agents.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['sdk-runtime', 'developer-portal']
---

## Role

Provides SDK scaffolding and authoring workflows for building, testing, and packaging third-party Enterprise OS skills and agents.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires sdk authoring capability
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
  skill: sdk-authoring
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
