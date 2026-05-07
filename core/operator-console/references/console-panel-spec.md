# Operator Console Panel Specifications

## Panel Inventory

| Panel | Data Source | Refresh Rate | Drill-Down |
|-------|------------|--------------|-----------|
| Agent Fleet | persistent-agent-runtime | 30s | Per-agent detail view |
| Workflow DAGs | workflow-runtime + temporal-integration | 15s | Full DAG visualization |
| Inference Fleet | inference-engine-fleet | 30s | Per-engine metrics |
| Cost Attribution | economic-coordination | 5m | Per-agent/workflow breakdown |
| Escalation Queue | hitl-dashboard | real-time (push) | Full escalation packet |
| Compliance Posture | compliance-runtime | 1h | Per-framework control status |
| Security Posture | zero-trust-runtime | 5m | Per-policy violation detail |

---

## Escalation Severity Classification

| Severity | Definition | Response SLA | Auto-Notify |
|----------|-----------|--------------|-------------|
| P1 | Platform outage or data loss risk; external commitment at risk | 5 minutes | PagerDuty + Slack DM + email |
| P2 | Significant degradation; internal SLA breach | 30 minutes | Slack DM + email |
| P3 | Non-critical issue requiring attention | 4 hours | Slack channel + email |
| P4 | Informational; low urgency | 24 hours | Email only |

---

## Directive Schema

```yaml
operator_directive:
  directive_id: "DIR-2026-xxxxx"
  issued_by: "operator@corp.com"
  issued_at: "2026-05-07T10:00:00Z"

  target_type: agent | workflow | engine | policy
  target_id: "cfo-agent"

  action: suspend | resume | restart | override | configure | terminate

  parameters: {}  # Action-specific parameters

  authorization:
    scope_required: agent_management   # Must be in operator's authorized scope
    requires_confirmation: true        # Show confirmation dialog before executing
    confirmation_timeout_s: 30        # Auto-cancel if not confirmed within 30s

  audit_ref: "DIR-AUD-2026-xxxxx"
```

---

## Agent Fleet Panel Data Model

```yaml
agent_fleet_panel:
  snapshot_at: "2026-05-07T10:00:00Z"
  agents:
    - agent_id: "cfo-agent"
      display_name: "CFO Agent"
      status: healthy | degraded | suspended | failed
      last_heartbeat: "2026-05-07T09:59:30Z"
      heartbeat_age_s: 30
      pending_escalations: 0
      domain: finance
      autonomous_actions_last_hour: 3

  fleet_summary:
    total: 0
    healthy: 0
    degraded: 0
    suspended: 0
    failed: 0
    pending_escalations_total: 0
```

---

## Workflow DAG Panel Data Model

```yaml
workflow_dag_panel:
  snapshot_at: "2026-05-07T10:00:00Z"
  active_workflows:
    - workflow_id: "WF-2026-xxxxx"
      name: "Q2 Compliance Audit Preparation"
      status: running | blocked | failed
      progress_pct: 65
      current_step: "Evidence collection — SOC2 CC6.1"
      blocked_reason: null
      started_at: "2026-05-07T08:00:00Z"
      expected_completion: "2026-05-07T14:00:00Z"

  summary:
    active: 0
    blocked: 0
    failed_last_hour: 0
    completed_last_hour: 0
```

---

## Cost Attribution Panel Data Model

```yaml
cost_panel:
  period: "last_1_hour"
  total_cost_usd: 0.0
  by_agent:
    - agent_id: "cfo-agent"
      cost_usd: 0.0
      pct_of_total: 0.0
  by_workflow:
    - workflow_id: "WF-2026-xxxxx"
      cost_usd: 0.0
      pct_of_total: 0.0
  by_engine:
    - engine_id: "vllm-prod-0"
      cost_usd: 0.0
      pct_of_total: 0.0
  hourly_burn_rate_usd: 0.0
  budget_attainment_pct: 0.0  # burn vs. hourly budget
```