# Temporal Memory Replay — Replay Protocol Specification

## Replay Use Cases

| Use Case | Trigger | Replay Window | Purpose |
|----------|---------|--------------|---------|
| Post-incident review | Incident closed | Incident duration + 1h buffer | RCA context reconstruction |
| Decision archaeology | User query about past decision | Surrounding 48h | Explain why a decision was made |
| Agent restart recovery | Agent cold-start after crash | Last 7 days | Restore working context |
| Training data generation | Scheduled weekly | Rolling 30-day window | Generate RLHF preference pairs |
| Anomaly investigation | Alert triggered | Alert window ± 2h | Find causal chain |

---

## Replay Request Schema

```yaml
replay_request:
  replay_id: "REPLAY-2026-xxxxx"
  requested_by: "program-governance-agent"
  requested_at: "2026-05-07T10:00:00Z"

  scope:
    time_range:
      start: "2026-05-06T14:00:00Z"
      end: "2026-05-06T18:00:00Z"
    entity_filter:
      entity_types: [project, incident, decision]
      entity_ids: ["incident:INC-2026-0042"]
    agent_filter: []              # Empty = include all agents
    min_salience: 0.3             # Exclude low-salience observations

  reconstruction_options:
    include_compressed: true      # Expand compressed observations
    include_decisions: true
    include_agent_actions: true
    chronological: true           # Replay in time order
    max_observations: 500
    max_tokens: 16384

  output_format: timeline | narrative | structured_json
```

---

## Replay Output Formats

### Timeline Format

```yaml
replay_output:
  replay_id: "REPLAY-2026-xxxxx"
  reconstructed_at: "2026-05-07T10:01:00Z"
  observation_count: 47
  token_count: 8240

  timeline:
    - timestamp: "2026-05-06T14:03:21Z"
      obs_id: "OBS-2026-04210"
      agent: "monitoring-agent"
      type: event
      content: "Alert triggered: API error rate exceeded 5% threshold"
      entities: [api-gateway, incident-INC-2026-0042]

    - timestamp: "2026-05-06T14:05:00Z"
      obs_id: "OBS-2026-04211"
      agent: "sre-agent"
      type: decision
      content: "Decision: roll back api-gateway to v2.3.1 immediately"
      entities: [api-gateway, incident-INC-2026-0042]
      decision_outcome: "Rollback completed at 14:08; error rate normalized"

    - timestamp: "2026-05-06T14:08:15Z"
      obs_id: "OBS-2026-04215"
      agent: "monitoring-agent"
      type: event
      content: "API error rate returned to < 0.5%"
```

### Narrative Format

Narrative format invokes an LLM to generate a prose reconstruction:

```
[Incident Timeline Reconstruction — 2026-05-06 14:00–18:00]

At 14:03, the monitoring agent detected that the API gateway error rate
exceeded the 5% alert threshold. The SRE agent was notified and, after
reviewing the deployment history, made the decision at 14:05 to roll back
the API gateway to version 2.3.1...
```

---

## Temporal Indexing Schema

All observations in long-term memory are indexed by:

```yaml
temporal_index_entry:
  obs_id: "OBS-2026-04210"
  timestamp: "2026-05-06T14:03:21Z"
  unix_timestamp: 1746540201
  entity_ids: [api-gateway, "incident:INC-2026-0042"]
  agent_id: "monitoring-agent"
  obs_type: event | decision | action | summary
  salience: 0.88
  is_compressed: false
  archive_tier: hot | warm | cold
```

**Index storage tiers:**
- **Hot** (< 7 days): In-memory, < 10ms retrieval
- **Warm** (7–90 days): SSD-backed, < 100ms retrieval
- **Cold** (> 90 days): Object storage, < 2s retrieval

---

## Replay Quality Assurance

```yaml
replay_validation:
  completeness_check:
    # Verify no time gaps > 30 min within the replay window
    # (gaps indicate missing observations, not true silence)
    max_allowed_gap_minutes: 30
    gap_action: annotate_gap    # Mark gaps explicitly in output

  consistency_check:
    # Verify decisions reference observations that precede them
    decision_has_prior_evidence: true

  entity_coherence:
    # All entity_ids in timeline must resolve in world-model
    resolve_entities: true
    unknown_entity_action: include_with_flag

  token_budget:
    max_output_tokens: 16384
    overflow_action: truncate_oldest  # Keep most recent if over budget
```

---

## RLHF Data Generation via Replay

```yaml
rlhf_replay_job:
  job_id: "RLHF-GEN-2026-xxxxx"
  replay_window_days: 30
  target_pairs: 1000

  selection_criteria:
    # Select episodes where agent took an action and outcome is known
    has_decision: true
    has_outcome: true
    min_salience: 0.5

  pair_format:
    prompt: "Reconstructed context up to the decision point (≤ 2K tokens)"
    chosen: "The action actually taken (if outcome was positive)"
    rejected: "Alternative action considered but not taken (if outcome was negative)"

  quality_filter:
    min_outcome_confidence: 0.80   # Only use episodes with clear outcomes
    exclude_contradicted_decisions: true

  output_uri: "gs://apotheon-rlhf-data/temporal-replay-{date}.jsonl"
```