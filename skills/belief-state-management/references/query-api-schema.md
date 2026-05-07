# Belief State Management — Query API Schema

## Query API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/belief/{entity_id}` | Get current belief state for an entity |
| `GET` | `/v1/belief/{entity_id}/history` | Get belief state change history |
| `POST` | `/v1/belief/query` | Structured query across multiple entities |
| `POST` | `/v1/belief/observe` | Submit a new observation to update belief state |
| `GET` | `/v1/belief/contradictions` | List unresolved contradictions |
| `POST` | `/v1/belief/resolve` | Submit contradiction resolution |

---

## Entity Belief State Response

```json
{
  "entity_id": "project:apotheon-v8",
  "entity_type": "project",
  "retrieved_at": "2026-05-07T10:00:00Z",

  "attributes": {
    "status": {
      "value": "in-progress",
      "confidence": 0.97,
      "source": "observation:OBS-2026-00412",
      "last_updated": "2026-05-07T09:30:00Z",
      "staleness_flag": false
    },
    "completion_pct": {
      "value": 72,
      "confidence": 0.85,
      "source": "observation:OBS-2026-00398",
      "last_updated": "2026-05-06T18:00:00Z",
      "staleness_flag": false
    },
    "risk_level": {
      "value": "medium",
      "confidence": 0.71,
      "source": "observation:OBS-2026-00380",
      "last_updated": "2026-05-05T12:00:00Z",
      "staleness_flag": true    # Exceeds staleness threshold
    }
  },

  "open_contradictions": [],
  "next_refresh_due": "2026-05-07T11:00:00Z"
}
```

---

## Structured Query Schema

```yaml
belief_query:
  query_id: "BQ-2026-xxxxx"
  submitted_by: "program-governance-agent"

  filters:
    entity_types: [project, risk, dependency, person]
    entity_ids: []              # Empty = all entities of specified types
    attribute_names: []         # Empty = all attributes
    min_confidence: 0.70        # Only return attributes with confidence >= threshold
    exclude_stale: false        # If true, omit stale attributes

  aggregations:
    - type: count
      group_by: entity_type
    - type: mean
      attribute: completion_pct
      group_by: entity_type

  sort:
    field: last_updated
    order: desc

  limit: 100
  offset: 0
```

---

## Observation Submission Schema

```yaml
observation:
  observation_id: "OBS-2026-xxxxx"     # Assigned by world-model on receipt
  submitted_by: "qa-agent"
  observed_at: "2026-05-07T10:00:00Z"
  source_type: agent_report | sensor | api_poll | human_input | document_extract

  entity_id: "project:apotheon-v8"
  entity_type: project

  updates:
    - attribute: completion_pct
      new_value: 74
      evidence: "Sprint 22 velocity report shows 2% gain"

    - attribute: risk_level
      new_value: low
      evidence: "P1 blockers resolved; no open incidents"

  source_credibility: 0.90   # Caller-declared; world-model may override
```

---

## Contradiction Record Schema

```yaml
contradiction:
  contradiction_id: "CONTR-2026-xxxxx"
  detected_at: "2026-05-07T10:00:00Z"
  entity_id: "project:apotheon-v8"
  attribute: risk_level
  status: open | resolved | suppressed

  conflicting_observations:
    - observation_id: "OBS-2026-00380"
      value: "medium"
      confidence: 0.71
      source: "risk-assessment-agent"
      observed_at: "2026-05-05T12:00:00Z"

    - observation_id: "OBS-2026-00412"
      value: "low"
      confidence: 0.90
      source: "qa-agent"
      observed_at: "2026-05-07T09:30:00Z"

  resolution:
    strategy: higher_confidence_wins | recency_wins | human_adjudicated
    resolved_value: "low"
    resolved_at: null
    resolved_by: null
```

---

## Staleness Policy

| Entity Type | Attribute | Max Age Before Stale |
|-------------|-----------|---------------------|
| `project` | `status` | 2 hours |
| `project` | `completion_pct` | 24 hours |
| `risk` | `risk_level` | 6 hours |
| `person` | `availability` | 1 hour |
| `dependency` | `version` | 48 hours |
| `infrastructure` | `health_status` | 5 minutes |

When an attribute is stale, `staleness_flag: true` is returned and the world-model schedules a refresh observation request to the originating source agent.

---

## Confidence Decay Function

Confidence decays linearly from the observed value toward `0.5` (maximum uncertainty) as time passes beyond the staleness threshold:

```
confidence_at_time_t = observed_confidence × max(0.5, 1 - decay_rate × hours_past_threshold)
```

Default `decay_rate` = 0.05 per hour (confidence halves after ~10 hours past threshold).