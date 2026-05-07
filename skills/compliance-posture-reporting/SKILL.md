---
name: compliance-posture-reporting
description: Generates regulator-ready compliance reports, gap analyses, and remediation tracking dashboards.
metadata:
  version: "0.1.0"
  category: governance
  owner: platform
  maturity: draft
  dependencies: ['compliance-runtime', 'continuous-control-monitoring']
---

## Role

Generates regulator-ready compliance reports, gap analyses, and remediation tracking dashboards.

## Activation Triggers

- Invoked by `sdlc-orchestration` when the objective requires compliance posture reporting capability
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
  skill: compliance-posture-reporting
  outputs: {}
  quality_gates_passed: true
```

## References

- `references/` — Domain-specific methodology, schemas, and standards
