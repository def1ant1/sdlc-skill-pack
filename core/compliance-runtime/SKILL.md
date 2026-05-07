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

Always-on compliance control evaluation engine. Continuously evaluates every in-scope
compliance control against live platform data, collects and stores automated evidence,
computes real-time compliance posture scores by framework, and surfaces gaps to the
`compliance-agent` for remediation. The platform is compliant-by-default — not just
at audit time.

## Activation Triggers

- A control's evaluation schedule fires (per-control cadence from the control catalog)
- A platform change event may affect control status (deployment, config change, policy update)
- `compliance-agent` requests an on-demand control re-evaluation
- Audit preparation is triggered (full evidence refresh for all controls in scope)
- A new regulatory framework is added to the compliance scope
- Evidence for a control exceeds its freshness threshold (re-collection required)

## Execution Protocol

1. **Control catalog**: Maintain the registry of all in-scope controls across frameworks:
   - Control ID, framework, description, evaluation method, evidence sources, schedule
   - Current status: `passing` | `failing` | `not_tested` | `not_applicable`
   - Last evaluated timestamp, evidence references, responsible owner

2. **Automated evaluation**: For each control, execute the control-specific evaluation:
   - Query `telemetry`, `audit-trail`, or `enterprise-integration-hub` for control evidence
   - Apply the evaluation logic (e.g., "MFA enabled for all admin accounts?")
   - Record result: `passing` | `failing` with evidence artifact reference

3. **Evidence collection**: Store evidence artifacts in the evidence vault:
   - Artifact type: screenshot, log export, configuration snapshot, test result
   - Artifact hash (SHA-256) for tamper detection
   - Collection timestamp and evaluator identity

4. **Posture scoring**: Compute framework-level posture score after each evaluation cycle:
   ```
   posture_score = (passing_controls / total_applicable_controls) × 100
   weighted_score = Σ (control_weight × passing) / Σ control_weight
   ```
   Publish score to `world-model` under `compliance` entity type.

5. **Gap notification**: For any control that transitions from `passing` → `failing`,
   emit `compliance.control.failed` event on `event-bus`. Include control ID, framework,
   failure reason, and responsible owner.

## Output Format

```yaml
compliance_evaluation:
  evaluation_run_id: "COMP-EVAL-2026-xxxxx"
  framework: soc2 | iso27001 | hipaa | gdpr | eu_ai_act
  controls_evaluated: 0
  controls_passing: 0
  controls_failing: 0
  posture_score: 0.0
  new_failures: []
  evidence_collected: 0
  next_evaluation_at: "2026-05-07T11:00:00Z"
```

## References

- `references/` — Control catalog schema, evaluation method library, evidence vault spec, posture scoring formula
