---
name: itsm-integration
description: Automates ServiceNow/Jira SM incident management, change management, and service catalog operations via the enterprise-integration-hub.
metadata:
  version: "0.1.0"
  category: connectivity
  owner: platform
  maturity: draft
  dependencies: ['enterprise-integration-hub']
---

## Role

ITSM integration skill. Provides incident creation, change management, service catalog,
and task management operations for ServiceNow and Jira Service Management via
`enterprise-integration-hub`. Enables platform agents and skills to create incidents,
track change approvals, and manage tasks without direct ITSM tool access.

## Activation Triggers

- An agent needs to create an incident for a detected platform issue
- A workflow step requires a change request to be submitted and approved
- `program-governance-agent` creates milestone tasks for human program managers
- `inbox-automation` needs to create follow-up tasks for routed messages
- An ITSM webhook event arrives (incident updated, change approved, task completed)

## Execution Protocol

1. **Incident management**:
   - Create: submit incident with title, description, severity (P1–P4), affected_ci, assignee
   - Update: add work notes, change status, escalate severity
   - Resolve: mark resolved with resolution notes and root_cause
   - Query: search incidents by state, assignee, affected_ci, or time range

2. **Change management**:
   - Submit change request with: title, description, affected_systems, rollback_plan, start_window
   - Route for approval: notify CAB approvers via `notification-orchestration`
   - Track approval status: poll or receive webhook on approval/rejection
   - Close: record actual change time and outcome

3. **Service catalog**:
   - Submit service catalog requests (e.g., access provisioning, infrastructure requests)
   - Track fulfillment status
   - Cancel pending requests

4. **Task management**:
   - Create tasks with owner, description, due date, and priority
   - Link tasks to parent incidents or change requests
   - Update completion status

5. **Webhook processing**: On ITSM event webhooks from `enterprise-integration-hub`:
   normalize to platform canonical event and publish to `event-bus`.

## Output Format

```yaml
itsm_result:
  operation: create_incident | update_incident | create_change | create_task
  system: servicenow | jira_sm
  record_id: "INC-0001234"
  status: success | auth_failed | validation_failed
  record_url: "https://instance.service-now.com/incident/INC-0001234"
  audit_ref: "ITSM-OPS-2026-xxxxx"
```

## Quality Gates

- P1 incidents must be created within 60 seconds of detection
- Change requests must include rollback_plan — reject submissions without one

## References

- `references/` — ITSM field mapping, severity classification matrix, change type taxonomy
