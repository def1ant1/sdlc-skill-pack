---
name: memory-compression
description: Consolidates episodic memory to semantic memory with importance scoring and forgetting curve management.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['sdlc-memory-token-management']
---

## Role

Consolidates episodic memory to semantic memory with importance scoring and forgetting curve management.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires memory compression capability
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
  skill: memory-compression
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
