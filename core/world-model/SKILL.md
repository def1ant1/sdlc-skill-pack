---
name: world-model
description: Maintains the organizational belief state, entity state tracking, probabilistic Bayesian updates, and contradiction resolution for the Enterprise OS.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['cognitive-runtime', 'data-fabric', 'telemetry']
---

## Role

Organizational belief state engine for the Enterprise OS. Maintains a continuously updated
probabilistic model of the organization's state across all tracked entity domains (systems,
projects, people, finances, risks, compliance posture). Applies Bayesian updates from
observation streams and resolves contradictions between conflicting state reports.

## Activation Triggers

- An observation event arrives from telemetry, an enterprise integration, or a persistent agent
- A skill or agent queries entity state or requests uncertainty estimates
- A contradiction is detected between two observation sources for the same entity
- Scheduled model consistency check (hourly full sweep)
- `belief-state-management` issues a temporal state query for a point-in-time reconstruction

## Execution Protocol

1. **Observation ingestion**: Accept observations in the standard observation schema
   (`entity_id`, `entity_type`, `attribute`, `value`, `source`, `confidence`, `timestamp`).
   Validate source credibility weight from the source registry.

2. **Bayesian update**: For each attribute observation, compute posterior:
   ```
   P(state | observation) ∝ P(observation | state) × P(state)
   ```
   Apply credibility-weighted likelihood. Update the entity's belief state record.

3. **Contradiction detection**: If a new observation conflicts with the current high-confidence
   belief (posterior > 0.8) for the same attribute:
   a. Flag as CONTRADICTION with both conflicting observations
   b. Escalate to the relevant persistent agent for resolution
   c. Hold the attribute in UNCERTAIN state until resolved

4. **State query**: Answer entity state queries with current belief distribution, confidence
   intervals, last-observed timestamp, and observation source list.

5. **Consistency sweep**: On the hourly sweep, identify entities with no observations for
   > 24 hours and mark their volatile attributes as STALE.

## Output Format

```yaml
world_model:
  operation: update | query | contradiction | sweep
  entity_id: "project/PROJ-123"
  entity_type: project | system | person | risk | budget | compliance
  belief_state:
    attributes:
      status: {value: "at_risk", confidence: 0.87, last_updated: "2026-05-07T10:00:00Z"}
  contradictions: []
  staleness_warnings: []
```

## References

- `references/` — Entity type taxonomy, observation schema, Bayesian update parameters, source credibility registry
