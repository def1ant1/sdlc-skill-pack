---
name: marketplace-publishing
description: Manages skill certification, publishing, versioning, and lifecycle operations within the Enterprise OS marketplace.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['developer-portal', 'sdk-runtime', 'governance']
---

## Role

Manages skill certification, publishing, versioning, and lifecycle operations within the Enterprise OS marketplace.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires marketplace publishing capability
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
  skill: marketplace-publishing
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
