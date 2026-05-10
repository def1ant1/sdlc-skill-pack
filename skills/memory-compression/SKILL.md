---
name: memory-compression
description: Consolidates episodic memory to semantic memory with importance scoring and forgetting curve management for the Enterprise OS long-term memory.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['sdlc-memory-token-management']

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Long-term memory lifecycle manager. Prevents unbounded growth of the platform's memory
store by applying importance-weighted consolidation: episodic memories (specific past events)
that meet the importance threshold are distilled into semantic memories (generalizable knowledge),
while low-importance episodic memories are archived or discarded per the forgetting curve schedule.

## Activation Triggers

- Memory store utilization exceeds the configured compression threshold (e.g., 80% of quota)
- A scheduled compression cycle is due (daily, weekly for different memory tiers)
- `temporal-memory-replay` requires a consolidated representation for a long time span
- An agent's memory namespace reaches its per-agent quota
- `sdlc-memory-token-management` requests consolidation before a context-limit-critical operation

## Execution Protocol

1. **Memory inventory**: Query `sdlc-memory-token-management` for all episodic memories
   older than the minimum retention window (default: 7 days).

2. **Importance scoring**: Score each episodic memory on:
   - `access_frequency`: how often this memory has been retrieved (weight: 0.35)
   - `outcome_impact`: did decisions informed by this memory lead to good outcomes (weight: 0.30)
   - `novelty`: how unique is this memory vs. existing semantic memories (weight: 0.20)
   - `recency_decay`: exponential decay since last access (weight: 0.15)

   Composite: `importance = Σ(weight × score)` on [0, 1]

3. **Consolidation decision**:
   - `importance ≥ 0.70`: Consolidate — extract semantic insight and store as semantic memory.
     Archive the episodic source for audit trail.
   - `importance 0.40–0.69`: Retain as episodic for next compression cycle review.
   - `importance < 0.40`: Discard (after checking it's not referenced by any active workflow).

4. **Semantic distillation**: For memories marked for consolidation, generate a semantic
   summary: "What generalizable lesson or fact does this episodic memory establish?"
   Merge with related existing semantic memories if they overlap (use cosine similarity > 0.85).

5. **Quota update**: Report compressed memory counts and freed storage to `sdlc-memory-token-management`.

## Output Format

```yaml
compression_result:
  memories_evaluated: 0
  consolidated: 0
  retained: 0
  discarded: 0
  semantic_memories_created: 0
  semantic_memories_merged: 0
  storage_freed_kb: 0
  compression_ratio: 0.0
```

## Quality Gates

- Discard only episodic memories with no active workflow references
- Semantic distillations must be reviewed by the `meta-reasoning` skill if importance was ≥ 0.85

## References

- `references/` — Importance scoring rubric, forgetting curve parameters, semantic distillation prompt
