---
name: belief-state-management
description: Queries organizational belief state, quantifies uncertainty, and estimates entity state under partial information from the world-model.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['world-model']
---

## Role

Query interface and uncertainty quantification layer for the `world-model`. Provides structured
access to entity belief states, computes confidence intervals, propagates uncertainty through
dependent entities, and answers "what do we believe about X right now?" queries for agents
and skills that need to act under partial information.

## Activation Triggers

- A persistent agent or skill requires the current belief state for an entity before acting
- An agent needs to quantify uncertainty before deciding whether to act autonomously or escalate
- `world-model` emits a CONTRADICTION or STALE event requiring upstream consumer notification
- An operator queries organizational state for a decision or report
- A reasoning skill needs to condition its analysis on current organizational beliefs

## Execution Protocol

1. **State query**: Accept queries in the form `{entity_id, attribute?, as_of?}`:
   - Point query: return current belief distribution for a specific entity attribute
   - Entity snapshot: return all attributes for an entity with their confidence levels
   - Point-in-time: if `as_of` provided, return the historical belief state at that timestamp

2. **Uncertainty quantification**: For each returned belief:
   - `value`: the mode (most probable value) of the belief distribution
   - `confidence`: posterior probability assigned to the mode
   - `confidence_interval`: [lower, upper] bounds at 80% credible interval for numeric attributes
   - `last_observed`: timestamp of the most recent observation contributing to this belief
   - `state_quality`: `fresh` | `stale` | `uncertain` | `contradicted`

3. **Dependency propagation**: When a queried entity has upstream dependencies that are
   `stale` or `contradicted`, flag this in the response: the entity's beliefs may be
   unreliable due to upstream uncertainty.

4. **Decision threshold advisory**: On request, classify the belief state's suitability
   for autonomous action:
   - `confidence ≥ 0.80 AND state_quality = fresh` → `act_autonomously`
   - `confidence 0.60–0.80 OR state_quality = stale` → `act_with_caution`
   - `confidence < 0.60 OR state_quality = contradicted` → `escalate_to_human`

## Output Format

```yaml
belief_query_result:
  entity_id: "project/PROJ-123"
  queried_at: "2026-05-07T10:00:00Z"
  attributes:
    status:
      value: "at_risk"
      confidence: 0.87
      confidence_interval: null  # Categorical — no interval
      last_observed: "2026-05-07T09:45:00Z"
      state_quality: fresh
  decision_advisory: act_autonomously | act_with_caution | escalate_to_human
  upstream_uncertainty_warnings: []
```

## Quality Gates

- All queries must return within 200ms (world-model is read-optimized)
- Stale entities must be flagged — do not silently return stale data as if fresh
- Contradicted attributes must always return `escalate_to_human` decision advisory

## References

- `references/` — Query API schema, uncertainty thresholds, decision advisory rules
