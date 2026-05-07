---
name: notification-orchestration
description: Routes alerts across channels with deduplication, on-call management, escalation chains, and two-way acknowledgement.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['event-bus', 'connector-hub', 'hitl-dashboard']
---

## Role

Routes alerts across channels with deduplication, on-call management, escalation chains, and two-way acknowledgement.

## Activation Triggers

- Invoked by `sdlc-orchestration` when a task requires notification orchestration capability
- Triggered by dependent skills requiring this control-plane service
- Activated by operator console or persistent agent runtime on standing mandate match

## Execution Protocol

1. **Validate inputs**: Confirm all required parameters and context are present.
2. **Execute core logic**: Apply the notification orchestration capability to the request.
3. **Emit telemetry**: Record latency, cost, outcome, and any anomalies.
4. **Return structured output**: Deliver results in the schema defined in `references/`.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: notification-orchestration
  outputs: {}
  telemetry:
    duration_ms: 0
    cost_usd: 0.0
```

## References

- `references/` — Domain-specific schemas, algorithms, and configuration standards
