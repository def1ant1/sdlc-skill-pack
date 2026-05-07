# ITSM Integration — Connector Specification

## Supported ITSM Systems

| ITSM | Integration Method | Auth | Key Objects |
|------|-------------------|------|-------------|
| ServiceNow | Table API + Event Management API | OAuth 2.0 | Incident, Change, Problem, CMDB CI |
| Jira Service Management | REST API v3 | OAuth 2.0 / API token | Issue, Request, SLA, Approvals |
| PagerDuty | REST API v2 | API key | Incident, Alert, On-Call Schedule |
| OpsGenie | REST API | API key | Alert, Incident, On-Call Schedule |

---

## Canonical ITSM Data Schemas

### Incident

```yaml
itsm_incident:
  incident_id: "INC-2026-xxxxx"
  source_itsm: servicenow
  source_number: "INC0042001"

  title: "API Gateway returning 502 errors — wave 9 deployment"
  description: "Following wave-9 deployment at 14:00 UTC, API gateway error rate exceeded 5%. Rollback initiated."

  severity: P1 | P2 | P3 | P4
  priority: 1 | 2 | 3 | 4
  status: new | in_progress | on_hold | resolved | closed

  affected_services:
    - service_id: "CI-api-gateway"
      name: "API Gateway"
      environment: production

  assignment:
    team: "SRE"
    assignee: "sre-agent"
    escalation_level: 0    # 0 = first-line; increments with each escalation

  timeline:
    detected_at: "2026-05-07T14:03:00Z"
    acknowledged_at: "2026-05-07T14:05:00Z"
    mitigated_at: "2026-05-07T14:18:00Z"
    resolved_at: "2026-05-07T14:45:00Z"

  sla:
    response_target_minutes: 15    # For P1
    resolve_target_minutes: 60
    response_met: true
    resolve_met: true

  related_change_id: "CHG-2026-xxxxx"
  root_cause: "Misconfigured connection pool limit in wave-9 deployment"
  postmortem_id: "PM-2026-xxxxx"

  synced_at: "2026-05-07T15:00:00Z"
```

### Change Request

```yaml
change_request:
  change_id: "CHG-2026-xxxxx"
  source_itsm: servicenow
  source_number: "CHG0012345"

  title: "Wave 9 inference engine deployment — 2026-05-07"
  type: standard | normal | emergency
  risk: low | medium | high | critical

  schedule:
    planned_start: "2026-05-07T14:00:00Z"
    planned_end: "2026-05-07T16:00:00Z"
    maintenance_window: "MAINT-WINDOW-002"

  approval:
    required: true
    approvers: [cto, sre-lead]
    approved_by: ["cto", "sre-lead"]
    approved_at: "2026-05-06T10:00:00Z"

  implementation:
    plan: "Deploy wave-9 engine fleet using blue/green strategy"
    rollback_plan: "Revert to wave-8 engine fleet within 5 minutes"
    test_plan: "Smoke test: 100 synthetic inference requests"

  status: draft | pending_approval | approved | in_progress | completed | failed | cancelled

  actual_start: "2026-05-07T14:00:00Z"
  actual_end: "2026-05-07T14:50:00Z"   # Extended due to incident
  outcome: success | partial_success | failed | rolled_back
  related_incident_ids: ["INC-2026-xxxxx"]
```

---

## Incident Lifecycle Integration

```
INCIDENT DETECTED (alert or user report)
        │
        ▼
1. Create incident in ITSM (auto via monitoring-agent)
        │
        ▼
2. Notify on-call via notification-orchestration
        │
        ▼
3. sre-agent engaged:
   ├── Queries world-model for recent changes (CHG records)
   ├── Runs diagnostic runbooks from DR runbook library
   └── Posts updates to incident timeline every 15 min
        │
        ▼
4. Mitigation applied → status: on_hold (if partial)
   or mitigated_at set
        │
        ▼
5. Root cause confirmed → resolved_at set
        │
        ▼
6. Lessons-learned-extraction triggered
7. Post-mortem created
8. Related change request updated with outcome
```

---

## CMDB Configuration Item Schema

```yaml
cmdb_ci:
  ci_id: "CI-api-gateway"
  name: "API Gateway"
  type: service | server | database | network_device | software | container
  environment: production | staging | development

  attributes:
    owner_team: "SRE"
    tier: 1    # Business criticality: 1 (highest) to 4
    rto_minutes: 15
    rpo_minutes: 5
    deployment_method: blue_green
    infrastructure_as_code_uri: "github:apotheon/infra/api-gateway"

  dependencies:
    upstream: []             # Services this CI depends on
    downstream: ["CI-inference-fleet", "CI-zero-trust-runtime"]

  last_deployed_at: "2026-05-07T14:00:00Z"
  last_change_id: "CHG-2026-xxxxx"
  health_status: healthy | degraded | unhealthy
```

---

## SLA Monitoring

```yaml
itsm_sla_monitoring:
  sla_policies:
    P1:
      response_minutes: 15
      resolve_minutes: 60
      breach_escalation: "notify on-call lead immediately"

    P2:
      response_minutes: 60
      resolve_minutes: 240
      breach_escalation: "notify team lead"

    P3:
      response_minutes: 240
      resolve_minutes: 1440   # 24 hours
      breach_escalation: "create follow-up task"

    P4:
      response_minutes: 480
      resolve_minutes: 4320   # 72 hours
      breach_escalation: null

  reporting:
    sla_compliance_target_pct: 95
    report_cadence: weekly
    report_recipients: [sre-lead, program-governance-agent]
```