---
name: communication-analytics
description: Analyzes communication volume, response times, and thread health across enterprise communication channels to surface operational insights.
metadata:
  version: "0.1.0"
  category: analytics
  owner: platform
  maturity: draft
  dependencies: ['inbox-automation', 'telemetry']
---

## Role

Operational analytics for enterprise communication health. Aggregates metadata from
email, Slack, and Teams interactions (via `inbox-automation`) to surface patterns:
response time trends, high-volume communication bottlenecks, unanswered threads,
and team communication health scores.

## Activation Triggers

- Weekly communication health report is due
- `inbox-automation` detects a surge in incoming message volume (> 2× baseline)
- An SLA breach is detected (message unanswered beyond configured response SLA)
- An operator requests a communication analysis for a team or project
- A persistent agent needs communication load data for capacity planning

## Execution Protocol

1. **Data ingestion**: Pull communication metadata from `inbox-automation` logs:
   - Message counts by channel, sender domain, and time period
   - Response times per thread (time from first message to first response)
   - Thread resolution status (resolved, escalated, pending, abandoned)
   - Message classification distribution (request, information, escalation, etc.)

2. **Metric computation**:
   - `avg_response_time_hours`: mean first-response time by team and channel
   - `p95_response_time_hours`: 95th percentile (identifies tail latency)
   - `unanswered_rate`: fraction of threads with no response within SLA window
   - `volume_trend`: week-over-week and month-over-month message volume change
   - `escalation_rate`: fraction of threads that required escalation

3. **Health scoring**: Compute a team communication health score (0–100):
   - Response time score: based on SLA attainment
   - Volume trend score: penalize runaway growth (may indicate process breakdown)
   - Resolution rate score: penalize high unanswered rate

4. **Anomaly detection**: Flag unusual patterns:
   - Volume spike (> 2× 7-day rolling average)
   - Response time degradation (> 50% increase week-over-week)
   - High unanswered rate for a specific channel or sender domain

5. **Report generation**: Produce a structured communication health report for the operator.

## Output Format

```yaml
communication_analytics:
  period: "2026-05-01 to 2026-05-07"
  channels_analyzed: [email, slack, teams]
  total_messages: 0
  avg_response_time_hours: 0.0
  p95_response_time_hours: 0.0
  unanswered_rate: 0.0
  health_score: 0.0
  anomalies: []
  top_volume_channels: []
```

## Quality Gates

- Analytics must exclude message content — metadata only (privacy compliance)
- PII in sender/recipient fields must be aggregated to team level before reporting

## References

- `references/` — Communication SLA policy, health score formula, anomaly detection thresholds
