---
name: lessons-learned-extraction
description: Synthesizes post-execution lessons and integrates them into the organizational knowledge graph.
metadata:
  version: "0.1.0"
  category: knowledge
  owner: platform
  maturity: draft
  dependencies: ['world-model', 'sdlc-memory-token-management']
---

## Role

Synthesizes post-execution lessons and integrates them into the organizational knowledge graph.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires lessons learned extraction capability
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
  skill: lessons-learned-extraction
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
