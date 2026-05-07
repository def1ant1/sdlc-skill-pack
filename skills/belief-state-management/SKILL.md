---
name: belief-state-management
description: Queries organizational belief state, quantifies uncertainty, and estimates entity state under partial information.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['world-model']
---

## Role

Queries organizational belief state, quantifies uncertainty, and estimates entity state under partial information.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires belief state management capability
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
  skill: belief-state-management
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
