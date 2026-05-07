---
name: itsm-integration
description: Automates ServiceNow/Jira SM incident management, change management, and service catalog operations.
metadata:
  version: "0.1.0"
  category: connectivity
  owner: platform
  maturity: draft
  dependencies: ['enterprise-integration-hub']
---

## Role

Automates ServiceNow/Jira SM incident management, change management, and service catalog operations.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires itsm integration capability
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
  skill: itsm-integration
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
