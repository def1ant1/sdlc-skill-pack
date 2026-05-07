---
name: prompt-optimization
description: Evaluates prompt variants systematically and applies automated improvement using outcome-feedback loops.
metadata:
  version: "0.1.0"
  category: ml-ops
  owner: platform
  maturity: draft
  dependencies: ['reinforcement-optimizer', 'benchmark-factory']
---

## Role

Evaluates prompt variants systematically and applies automated improvement using outcome-feedback loops.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires prompt optimization capability
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
  skill: prompt-optimization
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
