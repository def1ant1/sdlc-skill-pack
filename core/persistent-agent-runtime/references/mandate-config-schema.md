# Persistent Agent Mandate Configuration Schema

## Mandate Config YAML

```yaml
agent_mandate:
  agent_id: "cfo-agent"                 # Must match agents/ directory name
  display_name: "CFO Agent"
  version: "1.0.0"
  enabled: true

  # Monitoring cycle
  heartbeat_interval_minutes: 15         # How often the agent evaluates standing triggers
  domain: finance                        # Primary domain (used for world-model query scope)

  # Standing trigger conditions — evaluated on each heartbeat
  standing_triggers:
    - id: "SPEND-ANOMALY"
      condition: "budget.burn_rate_usd > budget.planned_rate_usd * 1.15"
      action: autonomous                 # autonomous | escalate | notify
      action_detail: "generate spend anomaly report and notify finance team"
      authority_scope: notify            # What the agent can do without approval

    - id: "BUDGET-BREACH"
      condition: "budget.forecast_to_complete > budget.total_budget_usd"
      action: escalate
      action_detail: "Create P1 escalation for CFO review with full budget analysis"
      authority_scope: read_analyze_escalate

    - id: "VENDOR-CONTRACT-EXPIRY"
      condition: "contract.expiry_date within 30 days AND contract.renewal_status != renewed"
      action: notify
      action_detail: "Alert procurement team with contract details"
      authority_scope: notify

  # Actions the agent can take autonomously (no HITL required)
  autonomous_action_scope:
    - generate_reports
    - send_notifications
    - query_world_model
    - query_erp_integration

  # Actions that always require HITL approval
  requires_hitl:
    - approve_spend
    - modify_budget_allocation
    - cancel_vendor_contract
    - initiate_audit

  # Inter-agent coordination
  coordination_peers:
    - "program-governance-agent"         # Can request portfolio spend data
    - "compliance-agent"                 # Can request financial compliance status

  # Agent-specific memory namespace
  memory_namespace: "agent/cfo-agent"
  memory_retention_days: 365

  # Escalation configuration
  escalation:
    default_severity: P2
    severity_overrides:
      BUDGET-BREACH: P1
    oncall_routing: "finance-oncall"
```

---

## Authority Scope Taxonomy

| Scope | Permitted Actions | Example |
|-------|------------------|---------|
| `read_only` | Query world model, read integrations | Research agent background monitoring |
| `notify` | Send notifications via notification-orchestration | Alert on detected condition |
| `read_analyze_escalate` | All read + create escalations in hitl-dashboard | Standard agent scope |
| `read_analyze_execute` | All above + autonomous write actions within domain | Advanced agents with approval |
| `full` | Unrestricted within domain boundary | Reserved; requires governance sign-off |

---

## Inter-Agent Message Schema

```yaml
agent_message:
  message_id: "MSG-2026-xxxxx"
  from_agent: "cfo-agent"
  to_agent: "program-governance-agent"
  message_type: data_request | data_response | coordination_request | alert
  subject: "Q2 portfolio spend data needed for budget anomaly analysis"
  payload: {}
  correlation_id: "SPEND-ANOMALY-heartbeat-1234"  # Links to originating trigger
  sent_at: "2026-05-07T10:15:00Z"
  ttl_minutes: 60
```

---

## Agent Health States

```
HEALTHY:    Heartbeats on schedule; triggers evaluated; no errors in last N cycles
DEGRADED:   Heartbeats delayed > 2× interval OR errors in last 3 cycles (non-fatal)
SUSPENDED:  Operator has manually suspended the agent; no heartbeats
FAILED:     Agent process crash or unrecoverable error; requires operator restart
```

---

## Mandate Evaluation Algorithm

```
ON each heartbeat for agent A:
  1. Fetch world-model snapshot for A.domain (entities A.domain cares about)
  2. FOR each trigger T in A.standing_triggers:
       IF evaluate_condition(T.condition, world_model_snapshot):
         IF T.action == "autonomous" AND A.autonomous_action_scope covers T.action_detail:
           execute_autonomous_action(A, T)
           log_action(agent=A, trigger=T, action_taken=T.action_detail)
         ELIF T.action == "escalate" OR scope_insufficient:
           create_escalation(agent=A, trigger=T, severity=T.severity or A.escalation.default)
         ELIF T.action == "notify":
           send_notification(A.escalation.oncall_routing, context=world_model_snapshot)
  3. Update A.last_heartbeat_at = now()
  4. Update A.consecutive_success_count += 1
```