---
name: inference-engine-benchmarking
description: Cross-engine latency and throughput benchmarking with automatic selection recommendations.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['inference-engine-fleet', 'model-benchmarking']
---

## Role

Cross-engine latency and throughput benchmarking with automatic selection recommendations.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires inference engine benchmarking capability
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
  skill: inference-engine-benchmarking
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
