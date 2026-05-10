---
name: lateral-movement-detection
description: Detects anomalous access patterns across agent execution graphs indicative of lateral movement between unauthorized resources.
metadata:
  version: "0.1.0"
  category: security
  owner: platform
  maturity: draft
  dependencies: ['zero-trust-runtime', 'telemetry']

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Behavioral security analytics for agent-to-agent access patterns. Monitors the access
graph of all agent and skill interactions, builds a baseline of normal access patterns,
and detects deviations that may indicate lateral movement, credential compromise, or
an agent operating outside its intended scope.

## Activation Triggers

- `zero-trust-runtime` logs a DENY event (potential unauthorized access attempt)
- An agent accesses a target it has never accessed before (first-access anomaly)
- An agent's access rate to any target exceeds 3× its baseline rate in a 5-minute window
- Same caller is DENIED at 3+ different targets within 5 minutes (scanning pattern)
- `security-architect-agent` requests an access pattern audit for a specific agent

## Execution Protocol

1. **Baseline modeling**: Maintain a rolling 7-day access baseline per agent:
   - `normal_targets`: set of targets the agent regularly accesses
   - `normal_access_rate`: requests/minute to each target (mean + 2σ)
   - `normal_access_hours`: time-of-day access pattern (business hours vs. off-hours)

2. **Anomaly detection**: On each authorization decision from `zero-trust-runtime`:
   - `new_target`: agent accessing a target not in `normal_targets` → AMBER alert
   - `rate_spike`: access rate > baseline_mean + 3σ → AMBER alert
   - `off_hours_access`: P1/P2 agent accessing sensitive targets outside normal hours → AMBER
   - `deny_storm`: 3+ DENY events for the same caller within 5 minutes → RED alert (scanning)
   - `privilege_escalation_attempt`: request for capabilities not in declared scope → RED alert

3. **Alert correlation**: Group related anomalies into an incident:
   - A series of AMBER alerts for the same agent within 30 minutes → escalate to RED
   - Provide the full correlated access timeline as context

4. **Response**: On RED alert:
   - Immediately notify `security-architect-agent` with full context
   - Recommend: suspend agent pending investigation (requires human confirmation for suspension)
   - Preserve the access log for forensic investigation

5. **False positive learning**: When an investigation confirms a false positive, update the
   baseline model to include the newly confirmed legitimate access pattern.

## Output Format

```yaml
lateral_movement_alert:
  alert_id: "LM-ALERT-2026-xxxxx"
  severity: AMBER | RED
  agent_id: "cfo-agent"
  anomaly_type: new_target | rate_spike | deny_storm | privilege_escalation_attempt
  evidence:
    - timestamp: "2026-05-07T10:00:00Z"
      target: "hr-integration"
      action: "read_employee_data"
      decision: DENY
  recommended_action: "Suspend agent pending investigation"
  escalated_to: security-architect-agent
```

## Quality Gates

- False positive rate target: < 5% of RED alerts (validated quarterly)
- All RED alerts must be escalated within 60 seconds of detection

## References

- `references/` — Anomaly detection thresholds, baseline modeling algorithm, incident correlation rules
