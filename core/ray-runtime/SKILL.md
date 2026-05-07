---
name: ray-runtime
description: Manages Ray cluster and KubeRay operator for distributed workload scheduling, training, serving, and data processing.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['cluster-management', 'distributed-agent-runtime', 'event-bus']
---

## Role

Manages Ray cluster and KubeRay operator for distributed workload scheduling, training, serving, and data processing.

## Activation Triggers

- Invoked by `sdlc-orchestration` when a task requires ray runtime capability
- Triggered by dependent skills requiring this control-plane service
- Activated by operator console or persistent agent runtime on standing mandate match

## Execution Protocol

1. **Validate inputs**: Confirm all required parameters and context are present.
2. **Execute core logic**: Apply the ray runtime capability to the request.
3. **Emit telemetry**: Record latency, cost, outcome, and any anomalies.
4. **Return structured output**: Deliver results in the schema defined in `references/`.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: ray-runtime
  outputs: {}
  telemetry:
    duration_ms: 0
    cost_usd: 0.0
```

## References

- `references/` — Domain-specific schemas, algorithms, and configuration standards
