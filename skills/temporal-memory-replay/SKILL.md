---
name: temporal-memory-replay
description: Reconstructs point-in-time organizational state and queries memory timelines for audit and analysis purposes.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['sdlc-memory-token-management', 'memory-compression']
---

## Role

Point-in-time organizational memory reconstruction. Answers the question "What did the
platform know and believe at time T?" by replaying the memory timeline up to the requested
timestamp. Used for post-incident analysis, audit evidence, and counterfactual reasoning
about past decisions.

## Activation Triggers

- A post-incident review requires reconstructing what agents knew at the time of an incident
- An audit requires evidence of what compliance posture was at a specific date
- `workflow-replay` requires memory state reconstruction for a historical workflow replay
- An operator queries "what was the belief about X on date D?"
- `lessons-learned-extraction` requires the organizational knowledge state at a past milestone

## Execution Protocol

1. **Timeline query**: Accept a query with:
   - `as_of`: ISO 8601 timestamp for the desired reconstruction point
   - `scope`: `global` | `agent/{agent_id}` | `entity/{entity_id}` | `domain/{domain}`
   - `include_episodic`: whether to include episodic memories or only semantic

2. **Memory timeline traversal**: Retrieve all memory records with `created_at ≤ as_of`
   and `(archived_at IS NULL OR archived_at > as_of)`. This gives the memory state
   that was active at the requested time.

3. **Belief state reconstruction**: For each entity in scope, reconstruct the belief state
   that `world-model` would have computed at `as_of` using only observations with
   `timestamp ≤ as_of`.

4. **Timeline summary**: Produce a chronological summary of significant memory changes
   in the requested time window:
   - When did a belief change significantly?
   - What was the organizational knowledge at key decision points?

5. **Counterfactual mode**: If `counterfactual: true` and an alternative observation set
   is provided, replay the timeline with the alternative observations to compute what
   the belief state would have been under different conditions.

## Output Format

```yaml
memory_replay:
  query_id: "REPLAY-2026-xxxxx"
  as_of: "2026-04-15T14:30:00Z"
  scope: "entity/project/PROJ-123"
  reconstructed_belief_state:
    status: {value: "on_track", confidence: 0.91, as_of: "2026-04-15T14:30:00Z"}
  timeline_events:
    - timestamp: "2026-04-10T09:00:00Z"
      event: "Status changed from on_track to at_risk"
      source: "program-governance-agent"
  memory_record_count: 0
```

## Quality Gates

- Reconstruction must be deterministic — same query always returns same result
- Must clearly label reconstructed state as historical (prevent confusion with current state)

## References

- `references/` — Timeline traversal algorithm, reconstruction validation rules
