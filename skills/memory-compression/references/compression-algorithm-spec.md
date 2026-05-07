# Memory Compression — Compression Algorithm Specification

## Compression Strategy Selection

| Strategy | When to Apply | Compression Ratio | Fidelity |
|----------|--------------|-------------------|---------|
| Lossless deduplication | Exact duplicate observations | Up to 10× | 100% |
| Semantic clustering | Near-duplicate observations (cosine sim > 0.92) | 3–8× | ~99% |
| Abstractive summarization | Conversation history > 2K tokens | 5–15× | ~95% |
| Hierarchical rolling | Long-term episodic memory > 30 days | 20–50× | ~85% |
| Lossy pruning | Low-salience observations past retention window | ∞ (delete) | 0% (intentional) |

---

## Compression Pipeline

```
INPUT: Memory buffer exceeds token budget
        │
        ▼
1. Deduplication pass
   ├── Hash-based exact dedup (O(n))
   └── Embedding similarity dedup (cosine sim > 0.92)
        │
        ▼
2. Salience scoring
   ├── Recency score: exp(-λ × age_days), λ = 0.1
   ├── Reference count score: log(1 + ref_count) / log(max_refs)
   ├── Entity importance: is_entity_in_active_project? × 0.3
   └── Combined: 0.4 × recency + 0.3 × ref_count + 0.3 × entity
        │
        ▼
3. Cluster by semantic similarity
   ├── Embed all observations (batch)
   ├── HDBSCAN clustering (min_cluster_size=3)
   └── Per cluster: keep highest-salience + summarize rest
        │
        ▼
4. Abstractive summarization (LLM call)
   ├── Input: cluster members (up to 2K tokens)
   ├── Output: 200-token summary preserving key facts + decisions
   └── Preserve: all entity references, all decisions, all open tasks
        │
        ▼
5. Rolling window truncation
   └── Drop observations past retention window if salience < 0.2
        │
        ▼
OUTPUT: Compressed memory buffer within token budget
```

---

## Salience Scoring Formula

```python
import math

def compute_salience(
    age_days: float,
    reference_count: int,
    max_refs: int,
    is_active_entity: bool,
    is_decision: bool,
    is_open_task: bool,
) -> float:
    """
    Compute salience score in [0, 1]. Higher = more important to retain.
    """
    # Recency: exponential decay, half-life ~7 days
    recency = math.exp(-0.1 * age_days)

    # Reference frequency
    ref_score = math.log(1 + reference_count) / math.log(1 + max(max_refs, 1))

    # Entity importance bonus
    entity_bonus = 0.2 if is_active_entity else 0.0

    # Structural importance: never prune decisions or open tasks
    if is_decision or is_open_task:
        return 1.0

    # Weighted combination
    return min(1.0, 0.4 * recency + 0.3 * ref_score + 0.3 * entity_bonus)
```

---

## Memory Observation Schema (Pre- and Post-Compression)

```yaml
# Pre-compression observation
observation:
  obs_id: "OBS-2026-00412"
  content: "Sprint 22 review: all 8 user stories completed. Velocity: 42 points. No carryover."
  entities: [sprint-22, apotheon-v8]
  obs_type: event
  observed_at: "2026-04-18T17:00:00Z"
  salience: 0.61
  compressed: false

# Post-compression (abstractive summary)
compressed_observation:
  obs_id: "OBS-COMP-2026-00001"
  content: "Sprints 20–22 (Apr 2026): All stories completed. Avg velocity 40 pts/sprint. No carryover items."
  source_obs_ids: [OBS-2026-00380, OBS-2026-00398, OBS-2026-00412]
  entities: [sprint-20, sprint-21, sprint-22, apotheon-v8]
  obs_type: summary
  period_start: "2026-04-04T00:00:00Z"
  period_end: "2026-04-18T17:00:00Z"
  compression_ratio: 3.1
  fidelity_score: 0.97
  compressed: true
```

---

## Token Budget Policy

| Memory Tier | Max Tokens | Compression Trigger | Hard Limit Action |
|------------|------------|--------------------|--------------------|
| Working memory (active context) | 4,096 | At 80% (3,277) | Compress to 60% |
| Short-term memory (session) | 16,384 | At 80% | Compress to 60% |
| Long-term memory (persistent) | 128,000 | At 90% | Compress + archive oldest |
| Archive (cold storage) | Unlimited | N/A | No token limit; content-addressed storage |

---

## Compression Quality Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| `compression_ratio` | `tokens_before / tokens_after` | > 3× |
| `fidelity_score` | Fraction of key facts retained (human-rated sample) | > 0.93 |
| `entity_retention_rate` | % of active entities preserved | > 0.99 |
| `decision_retention_rate` | % of decisions preserved | 1.00 (never lose decisions) |
| `compression_latency_ms` | Time to compress 10K token buffer | < 5,000 ms |

Compression runs are logged with all metrics to enable regression detection.