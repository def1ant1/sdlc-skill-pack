---
name: operator-console
description: Unified enterprise OS dashboard surfacing agent fleet status, active workflow DAGs, model status, cost attribution, and the governance escalation queue.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['telemetry', 'hitl-dashboard', 'cognitive-runtime', 'persistent-agent-runtime']

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

Unified observability and control surface for the Enterprise OS. Aggregates agent fleet
health, active workflow DAG status, inference model availability, real-time cost attribution,
and the governance escalation queue into a single operator view. Accepts directives from
operators and routes them to the appropriate runtime component.

## Activation Triggers

- Operator opens the console (triggers a full state snapshot assembly)
- A persistent agent creates an escalation requiring human decision
- A workflow enters a terminal failure state requiring operator acknowledgement
- An inference engine health event changes fleet status
- A cost threshold alert fires from the economic-coordination skill
- Operator issues a directive, override, or agent suspension command

## Execution Protocol

1. **State aggregation**: On console open, query in parallel:
   - `persistent-agent-runtime`: agent fleet status (healthy/degraded/suspended count, escalations)
   - `workflow-runtime`: active workflow DAGs with status, progress, blockers
   - `inference-engine-fleet`: engine availability, queue depths, p95 latency by engine
   - `economic-coordination`: hourly cost burn rate, cost attribution by agent/workflow
   - `hitl-dashboard`: pending escalation queue with age, priority, assigned agent
   - `governance`: current compliance posture score, open policy violations

2. **Escalation routing**: When a new escalation arrives:
   a. Classify severity (P1/P2/P3) based on escalation type and source agent
   b. Surface in the escalation queue with full context packet
   c. Notify on-call operator via `notification-orchestration`
   d. Start escalation SLA timer

3. **Directive dispatch**: When operator submits a directive:
   a. Validate directive syntax and operator authorization scope
   b. Route to target component (agent, workflow, engine)
   c. Confirm receipt; display outcome in console

4. **Drill-down**: Support drill-down from any console panel into the originating skill's
   detailed output (e.g., click a workflow to see full DAG; click an agent to see belief state).

## Output Format

```yaml
console_snapshot:
  generated_at: "2026-05-07T10:00:00Z"
  agent_fleet:
    total: 0
    healthy: 0
    degraded: 0
    suspended: 0
    pending_escalations: 0
  workflows:
    active: 0
    blocked: 0
    failed_last_hour: 0
  inference_fleet:
    engines_healthy: 0
    p95_latency_ms: 0
    queue_depth: 0
  cost:
    hourly_burn_usd: 0.0
    top_consumers: []
  escalation_queue: []
  compliance_posture_score: 0.0
```

## References

- `references/` — Console panel specifications, escalation severity taxonomy, directive schema
