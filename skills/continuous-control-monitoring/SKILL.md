---
name: continuous-control-monitoring
description: Evaluates SOC2/ISO 27001/HIPAA/GDPR/EU AI Act controls continuously and collects automated evidence.
metadata:
  version: "0.1.0"
  category: governance
  owner: platform
  maturity: draft
  dependencies: ['compliance-runtime', 'governance']
---

## Role

Evaluates SOC2/ISO 27001/HIPAA/GDPR/EU AI Act controls continuously and collects automated evidence.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires continuous control monitoring capability
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
  skill: continuous-control-monitoring
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
