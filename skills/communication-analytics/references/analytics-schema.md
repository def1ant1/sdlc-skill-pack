# Communication Analytics — Analytics Schema & Metric Definitions

## Communication Data Sources

| Source | Data Type | Ingestion Method | Cadence |
|--------|-----------|-----------------|---------|
| Gmail / Exchange | Email threads | enterprise-integration-hub | Real-time (webhook) |
| Slack / Teams | Channel messages, DMs | enterprise-integration-hub | Real-time (webhook) |
| Zoom / Meet | Meeting transcripts | audio-video-processing | Post-meeting |
| Jira / Linear | Issue comments, descriptions | enterprise-integration-hub | On change |
| GitHub | PR comments, reviews | enterprise-integration-hub | On change |
| Calendar | Meeting metadata | Google Calendar connector | Sync every 15 min |

---

## Communication Analytics Record Schema

```yaml
communication_record:
  record_id: "COMM-2026-xxxxx"
  source: gmail | slack | teams | zoom | jira | github | calendar
  channel_type: email | chat | meeting | issue_comment | code_review

  participants:
    - person_id: "person:alice-chen"
      name: "Alice Chen"
      role: sender | recipient | mention | attendee
      department: engineering

  content:
    subject: "Re: Wave 9 deployment readiness"
    body_tokens: 342
    sentiment: positive | neutral | negative | mixed
    sentiment_score: 0.72     # [−1, 1], positive direction
    urgency: P1 | P2 | P3 | P4
    intent: request | information | escalation | approval_needed | fyi

  entities_mentioned:
    projects: [apotheon-v8]
    people: [alice-chen, bob-smith]
    dates: ["2026-05-14"]
    risks: []

  response_metrics:
    sent_at: "2026-05-07T09:00:00Z"
    first_response_at: "2026-05-07T10:23:00Z"
    response_time_minutes: 83
    sla_target_hours: 4
    sla_met: true

  thread_id: "THREAD-2026-xxxxx"
  in_reply_to: "COMM-2026-yyyyy"
```

---

## Team Communication Health Metrics

| Metric | Definition | Target | Alert Threshold |
|--------|-----------|--------|----------------|
| `p50_response_time_minutes` | Median first-response time | < 60 min (P3) | > 180 min |
| `sla_compliance_rate_pct` | % messages responded to within SLA | > 90% | < 75% |
| `escalation_rate_pct` | % messages that become escalations | < 5% | > 10% |
| `meeting_load_hours_per_week` | Hours in meetings per person | < 12 h/week | > 20 h/week |
| `async_to_sync_ratio` | Async (email/chat) vs. sync (meeting) messages | > 4:1 | < 2:1 |
| `cross_team_message_volume` | Messages across team boundaries | Informational | N/A |
| `sentiment_score_7d_avg` | Rolling 7-day average sentiment | > 0.3 | < 0 (3 consecutive days) |

---

## Communication Health Report Schema

```yaml
communication_health_report:
  report_id: "COMM-RPT-2026-xxxxx"
  generated_at: "2026-05-07T00:00:00Z"
  period: "2026-04-28" to "2026-05-04"
  scope: organization | team | project

  summary:
    total_messages: 1840
    total_meetings: 34
    total_meeting_hours: 68
    active_threads: 142
    unresolved_threads_past_sla: 7

  response_time:
    p50_minutes: 47
    p95_minutes: 210
    sla_compliance_pct: 88.2

  sentiment:
    overall_score: 0.41
    trend: improving   # improving | stable | declining
    negative_thread_count: 12

  top_communication_bottlenecks:
    - type: slow_response
      description: "7 threads unresolved past SLA — all in compliance domain"
      recommendation: "Route compliance queries to compliance-agent for draft responses"

    - type: meeting_overload
      description: "Engineering team averaging 22 hours/week in meetings"
      recommendation: "Convert 3 recurring syncs to async standup format"

  collaboration_graph:
    # Who is communicating with whom (anonymized for privacy)
    most_connected_nodes: [engineering-lead, program-governance-agent]
    isolated_nodes: []    # People with very low communication volume
    bridge_nodes: [alice-chen]   # People who connect otherwise-disconnected groups
```

---

## Sentiment Analysis Configuration

```yaml
sentiment_analysis:
  model: "claude-haiku-4-5-20251001"   # Fast + cost-effective for high volume
  batch_size: 50
  schema:
    sentiment: positive | neutral | negative | mixed
    score: float   # [−1, 1]
    signals:       # Contributing phrases or words
      - phrase: "blocked on"
        contribution: -0.3
      - phrase: "great progress"
        contribution: +0.4

  privacy:
    pii_scrub_before_analysis: true   # Remove names, emails before sending to LLM
    store_raw_content: false          # Only store derived metrics, not message body
    data_classification: CONFIDENTIAL
```

---

## Meeting Efficiency Metrics

```yaml
meeting_metrics:
  meeting_id: "MTG-2026-xxxxx"
  title: "Wave 9 Deployment Review"
  date: "2026-05-07"
  duration_minutes: 60
  attendees: 8
  person_minutes: 480   # duration × attendees

  efficiency_indicators:
    had_agenda: true
    started_on_time: true
    action_items_count: 5
    action_items_with_owner: 5
    action_items_with_due_date: 4
    decisions_made: 2
    could_have_been_async: false   # AI assessment

  transcript_summary: |
    Reviewed Wave 9 deployment plan. Approved go/no-go for 2026-05-14.
    5 action items assigned; 2 architectural decisions recorded.

  efficiency_score: 0.82   # [0, 1]; composite of above indicators
```