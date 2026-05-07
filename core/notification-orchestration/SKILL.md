---
name: notification-orchestration
description: Routes alerts across channels with deduplication, on-call management, escalation chains, and two-way acknowledgement for the Enterprise OS event surface.
metadata:
  version: "0.1.0"
  category: platform
  owner: platform
  maturity: draft
  dependencies: ['event-bus', 'connector-hub', 'hitl-dashboard']
---

## Role

Intelligent notification router for the Enterprise OS. Accepts alert events from agents,
skills, and monitoring systems, deduplicates correlated alerts, routes to the correct
on-call responder via the configured channel (email, Slack, PagerDuty, Teams), manages
escalation chains when acknowledgements are not received, and tracks two-way confirmation.

## Activation Triggers

- A persistent agent creates an escalation requiring human attention
- A telemetry threshold fires an alert rule
- A workflow enters a failure state requiring operator action
- An on-call shift change is due (update routing configuration)
- An alert is not acknowledged within the configured SLA (escalation trigger)
- Operator configures a new alert routing rule or on-call schedule

## Execution Protocol

1. **Alert ingestion**: Accept alert events with:
   - `alert_id`, `source`, `severity` (P1/P2/P3/P4), `title`, `description`, `context_url`
   - `routing_key`: determines which on-call team or individual receives the alert
   - `dedup_key`: used for deduplication of correlated alerts

2. **Deduplication**: Before routing, check if an open alert with the same `dedup_key` exists.
   If yes: merge the new alert into the existing one (increment `occurrence_count`).
   If no: create a new alert record and proceed to routing.

3. **Route**: Look up the on-call schedule for the `routing_key`. Determine the primary
   responder. Select channel based on severity:
   - P1: PagerDuty + Slack DM + email (all simultaneously)
   - P2: Slack DM + email
   - P3: Slack channel message + email
   - P4: Email only

4. **Send**: Dispatch notification via `connector-hub` to the selected channels.
   Record send timestamp and delivery receipt.

5. **Acknowledgement tracking**: Start SLA timer on send. Expected acknowledgement windows:
   - P1: 5 minutes; P2: 30 minutes; P3: 4 hours; P4: 24 hours
   On non-acknowledgement: escalate to secondary responder. On secondary non-ack: escalate
   to manager. Log each escalation step.

6. **Resolution**: When the originating issue is resolved, send an all-clear notification
   to all channels that received the original alert. Close the alert record.

## Output Format

```yaml
notification:
  alert_id: "ALERT-2026-xxxxx"
  dedup_key: "inference-fleet-p95-breach"
  severity: P1
  status: sent | acknowledged | escalated | resolved
  sent_at: "2026-05-07T10:00:00Z"
  acknowledged_by: null
  acknowledged_at: null
  escalation_count: 0
  channels_notified: [pagerduty, slack, email]
```

## References

- `references/` — Alert severity taxonomy, on-call schedule schema, channel routing policy, escalation chain config
