---
name: distributed-training-orchestration
description: Orchestrates Ray Train fine-tuning workflows with DDP and FSDP distributed training strategies.
metadata:
  version: "0.1.0"
  category: ml-ops
  owner: platform
  maturity: draft
  dependencies: ['ray-runtime', 'model-distillation']
---

## Role

Orchestrates Ray Train fine-tuning workflows with DDP and FSDP distributed training strategies.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires distributed training orchestration capability
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
  skill: distributed-training-orchestration
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
