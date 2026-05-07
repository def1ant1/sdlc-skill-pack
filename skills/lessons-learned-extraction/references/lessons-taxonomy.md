# Lessons Learned Extraction — Lessons Taxonomy

## Lesson Type Taxonomy

| Type ID | Type Name | Description | Source Events |
|---------|-----------|-------------|--------------|
| `LES-INCIDENT` | Incident lesson | What caused the incident; what prevented faster resolution | Post-incident reviews, RCA reports |
| `LES-DECISION` | Decision lesson | What made a decision good or bad in retrospect | Decision records + outcomes |
| `LES-PROCESS` | Process lesson | Bottlenecks, ambiguities, or missing steps in workflows | Sprint retros, audit logs |
| `LES-TECHNICAL` | Technical lesson | Architecture or implementation patterns that helped or hurt | Code review outcomes, perf benchmarks |
| `LES-COMM` | Communication lesson | Coordination failures or successes across teams/agents | Escalation logs, inbox analytics |
| `LES-FORECAST` | Forecasting lesson | Where estimates were significantly wrong | Budget actuals vs. forecasts |

---

## Lesson Record Schema

```yaml
lesson:
  lesson_id: "LES-2026-xxxxx"
  lesson_type: LES-INCIDENT | LES-DECISION | LES-PROCESS | LES-TECHNICAL | LES-COMM | LES-FORECAST
  extracted_at: "2026-05-07T10:00:00Z"
  extracted_by: "sdlc-orchestration"
  source_event_ids: ["INC-2026-0042", "RCA-2026-0042"]
  project_id: "apotheon-v8"
  phase: retrospective | in-flight

  title: "DB connection pool exhaustion during peak load"

  what_happened: |
    During the wave-9 deployment load test, the PostgreSQL connection pool
    hit the 100-connection limit, causing a 12-minute degradation window.

  root_cause: |
    The connection pool limit was set at the application default (100) rather
    than tuned for the expected concurrency (400 concurrent workers).

  contributing_factors:
    - "No load test ran before wave-9 deployment"
    - "Connection pool config not included in deployment checklist"

  what_worked: |
    The on-call runbook correctly identified the symptom within 3 minutes
    via the `pg_stat_activity` dashboard.

  what_did_not_work: |
    The automated rollback did not trigger because error rate stayed below 5%
    threshold despite degraded latency.

  recommendation: |
    Add connection pool sizing to the pre-deployment checklist.
    Add a latency-based rollback trigger (P95 > 3× baseline) in addition
    to error-rate-based triggers.

  action_items:
    - owner: "sre-agent"
      task: "Update DR runbook with connection pool sizing formula"
      due: "2026-05-14"
      status: open

    - owner: "infrastructure-optimization-agent"
      task: "Add P95 latency rollback trigger to engine-fleet-spec"
      due: "2026-05-21"
      status: open

  tags: [database, connection-pool, load-testing, deployment]
  severity: high          # low | medium | high | critical
  applicability: [all-future-wave-deployments]
  archived: false
```

---

## Extraction Triggers

| Trigger | When | Scope |
|---------|------|-------|
| Post-incident | Incident resolved | Incident window + contributing context |
| Sprint retrospective | End of each sprint | Sprint duration |
| Quarterly program review | Every 90 days | Full quarter |
| Failed deployment | Rollback triggered | Deployment window + 24h |
| Significant forecast miss | Actuals deviate > 20% from forecast | Budget period |
| On-demand | Human or agent request | Specified scope |

---

## Pattern Detection Rules

Lessons are clustered to detect recurring patterns:

```yaml
pattern_detection:
  min_lesson_count_to_form_pattern: 3
  similarity_threshold: 0.80   # Embedding cosine similarity

  pattern_schema:
    pattern_id: "PAT-2026-xxxxx"
    title: "Recurring: connection pool exhaustion on deployment"
    lesson_ids: [LES-2026-00041, LES-2026-00082, LES-2026-00103]
    frequency: 3
    first_occurrence: "2026-02-15"
    last_occurrence: "2026-05-07"
    recommended_systemic_fix: |
      Automate connection pool sizing as part of the deployment scaffolding.
      Never rely on application defaults.
    escalated_to: "program-governance-agent"
    escalation_reason: "Third recurrence; systemic fix required"
```

---

## Lessons Corpus Query API

```yaml
lesson_query:
  filters:
    lesson_type: []           # Empty = all types
    tags: [database]
    severity: [high, critical]
    project_id: null          # null = all projects
    date_range:
      from: "2026-01-01"
      to: "2026-05-07"
    archived: false

  sort:
    field: extracted_at
    order: desc

  include_patterns: true      # Include matching patterns alongside lessons

  limit: 50
```

---

## Institutional Knowledge Integration

Lessons are ingested into the `institutional-knowledge-query` index after extraction:

```yaml
knowledge_index_entry:
  entry_id: "KW-2026-xxxxx"
  source_type: lesson
  source_id: "LES-2026-xxxxx"
  title: "DB connection pool exhaustion during peak load"
  summary: "Connection pool limit must be tuned for expected concurrency; never use application defaults."
  tags: [database, connection-pool, deployment]
  embedding_model: "text-embedding-3-large"
  indexed_at: "2026-05-07T10:05:00Z"
  searchable: true
```