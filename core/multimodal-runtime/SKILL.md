---
name: multimodal-runtime
description: Processes multi-modal enterprise inputs (PDF, image, audio, video) through a unified pipeline with modality routing and context assembly.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['cognitive-runtime', 'data-fabric', 'agent-kernel']
---

## Role

Processes multi-modal enterprise inputs (PDF, image, audio, video) through a unified pipeline with modality routing and context assembly.

## Activation Triggers

- Invoked by `sdlc-orchestration` when a task requires multimodal runtime capability
- Triggered by dependent skills requiring this control-plane service
- Activated by operator console or persistent agent runtime on standing mandate match

## Execution Protocol

1. **Validate inputs**: Confirm all required parameters and context are present.
2. **Execute core logic**: Apply the multimodal runtime capability to the request.
3. **Emit telemetry**: Record latency, cost, outcome, and any anomalies.
4. **Return structured output**: Deliver results in the schema defined in `references/`.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: multimodal-runtime
  outputs: {}
  telemetry:
    duration_ms: 0
    cost_usd: 0.0
```

## References

- `references/` — Domain-specific schemas, algorithms, and configuration standards
