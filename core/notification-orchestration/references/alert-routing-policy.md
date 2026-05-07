# Alert Routing Policy & On-Call Schema

## Alert Severity Taxonomy

| Severity | Definition | First Response SLA | Auto-Escalate After |
|----------|-----------|--------------------|---------------------|
| P1 | Service down, data loss risk, external commitment at risk, security incident | 5 minutes | 5 minutes to secondary |
| P2 | Significant degradation, internal SLA breach, compliance gap critical | 30 minutes | 30 minutes to secondary |
| P3 | Non-critical issue, quality degradation, warning threshold breach | 4 hours | 4 hours to manager |
| P4 | Informational, low urgency, scheduled maintenance reminder | 24 hours | No auto-escalate |

---

## Channel Routing Matrix

```yaml
channel_routing:
  P1:
    channels: [pagerduty, slack_dm, email]
    send_simultaneously: true
    pagerduty_urgency: high

  P2:
    channels: [slack_dm, email]
    send_simultaneously: true

  P3:
    channels: [slack_channel, email]
    slack_channel: "#{routing_key}-alerts"

  P4:
    channels: [email]
```

---

## On-Call Schedule Schema

```yaml
oncall_schedule:
  schedule_id: "finance-oncall"
  description: "CFO Agent and Finance team on-call"
  timezone: "America/New_York"

  rotations:
    - rotation_name: "primary"
      rotation_type: weekly
      rotation_start: "2026-05-05T09:00:00-05:00"
      participants:
        - id: "alice@corp.com"
          name: "Alice Chen"
          slack_id: "U12345"
          pagerduty_id: "P12345"
          phone: "+1-555-0100"

    - rotation_name: "secondary"
      rotation_type: weekly
      rotation_start: "2026-05-05T09:00:00-05:00"
      participants:
        - id: "bob@corp.com"
          name: "Bob Smith"

  escalation_policy:
    - level: 1
      target: primary
      timeout_minutes: 5       # Escalate if not acked in 5m
    - level: 2
      target: secondary
      timeout_minutes: 15
    - level: 3
      target: "cfo@corp.com"   # Final escalation: executive
      timeout_minutes: 30
```

---

## Deduplication Algorithm

```python
def deduplicate_alert(incoming: Alert, active_alerts: list[Alert]) -> DedupResult:
    """
    Deduplicate incoming alert against active open alerts.
    Returns: MERGE (into existing) or NEW (create new alert record)
    """
    for active in active_alerts:
        if (active.dedup_key == incoming.dedup_key
                and active.status in ("sent", "acknowledged")
                and not active.is_resolved()):
            # Same incident — merge
            active.occurrence_count += 1
            active.last_seen_at = incoming.timestamp
            active.context_updates.append(incoming.context)
            return DedupResult(action="MERGE", target_alert_id=active.alert_id)

    return DedupResult(action="NEW", target_alert_id=None)
```

---

## Alert Record Schema

```yaml
alert:
  alert_id: "ALERT-2026-xxxxx"
  dedup_key: "inference-fleet-p95-breach"    # Used for deduplication
  routing_key: "infrastructure-oncall"        # Determines on-call schedule

  severity: P1
  title: "Inference Fleet P95 Latency SLO Breach"
  description: "vllm-prod fleet p95 latency is 920ms, exceeding 500ms SLO for > 5 minutes"
  context_url: "http://operator-console/fleet/vllm-prod"

  source: "inference-engine-fleet"
  source_ref: "engine_fleet_status_2026xxxxx"

  status: sent | acknowledged | escalated | resolved

  occurrence_count: 1
  first_seen_at: "2026-05-07T10:00:00Z"
  last_seen_at: "2026-05-07T10:00:00Z"
  sent_at: "2026-05-07T10:00:00Z"
  acknowledged_by: null
  acknowledged_at: null
  resolved_at: null

  escalation_count: 0
  escalation_history: []

  channels_notified: [pagerduty, slack_dm, email]
```

---

## Escalation Chain Execution

```
ON alert created (severity P1 or P2):
  1. Notify primary on-call responder
  2. Start SLA timer (P1: 5m, P2: 30m)
  3. IF no acknowledgement within SLA:
       escalation_count += 1
       Notify secondary on-call responder
       Extend SLA timer (×2)
  4. IF still no acknowledgement:
       escalation_count += 1
       Notify manager-level escalation target
       Extend SLA timer (×2)
  5. IF still no acknowledgement:
       Notify executive escalation target
       Mark alert as "CRITICAL_UNACKNOWLEDGED"

ON acknowledgement received:
  - Stop SLA timer
  - Record acknowledged_by and acknowledged_at
  - Update alert status to "acknowledged"
  - Send acknowledgement confirmation to all notified channels

ON resolution:
  - Send all-clear to all channels that received the original alert
  - Record resolved_at
  - Compute total_time_to_resolve_minutes for SLA tracking
```