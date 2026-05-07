---
name: institutional-knowledge-query
description: Queries organizational precedents, similar past decisions, and failure pattern libraries.
metadata:
  version: "0.1.0"
  category: knowledge
  owner: platform
  maturity: draft
  dependencies: ['world-model', 'enterprise-search']
---

## Role

Queries organizational precedents, similar past decisions, and failure pattern libraries.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires institutional knowledge query capability
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
  skill: institutional-knowledge-query
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
