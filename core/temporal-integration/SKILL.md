---
name: temporal-integration
description: Integrates Temporal.io cluster for durable workflow signals, queries, schedules, namespace isolation, and workflow visibility.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['workflow-runtime', 'event-bus', 'telemetry']
---

## Role

Integrates Temporal.io cluster for durable workflow signals, queries, schedules, namespace isolation, and workflow visibility.

## Activation Triggers

- Invoked by `sdlc-orchestration` when a task requires temporal integration capability
- Triggered by dependent skills requiring this control-plane service
- Activated by operator console or persistent agent runtime on standing mandate match

## Execution Protocol

1. **Validate inputs**: Confirm all required parameters and context are present.
2. **Execute core logic**: Apply the temporal integration capability to the request.
3. **Emit telemetry**: Record latency, cost, outcome, and any anomalies.
4. **Return structured output**: Deliver results in the schema defined in `references/`.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: temporal-integration
  outputs: {}
  telemetry:
    duration_ms: 0
    cost_usd: 0.0
```

## References

- `references/` — Domain-specific schemas, algorithms, and configuration standards
