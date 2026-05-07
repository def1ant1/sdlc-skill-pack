---
name: compliance-runtime
description: Continuously evaluates compliance controls, collects automated evidence, and scores organizational posture against SOC2/ISO 27001/HIPAA/GDPR/EU AI Act.
metadata:
  version: "0.1.0"
  category: governance
  owner: platform
  maturity: draft
  dependencies: ['governance', 'telemetry', 'data-fabric', 'audit-trail']
---

## Role

Continuously evaluates compliance controls, collects automated evidence, and scores organizational posture against SOC2/ISO 27001/HIPAA/GDPR/EU AI Act.

## Activation Triggers

- Invoked by `sdlc-orchestration` when a task requires compliance runtime capability
- Triggered by dependent skills requiring this control-plane service
- Activated by operator console or persistent agent runtime on standing mandate match

## Execution Protocol

1. **Validate inputs**: Confirm all required parameters and context are present.
2. **Execute core logic**: Apply the compliance runtime capability to the request.
3. **Emit telemetry**: Record latency, cost, outcome, and any anomalies.
4. **Return structured output**: Deliver results in the schema defined in `references/`.

## Output Format

```yaml
result:
  status: success | partial | failed
  skill: compliance-runtime
  outputs: {}
  telemetry:
    duration_ms: 0
    cost_usd: 0.0
```

## References

- `references/` — Domain-specific schemas, algorithms, and configuration standards
