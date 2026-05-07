# Cache Optimization Strategies Reference

## Cache Types in AI Inference

| Cache Type | What Is Cached | Scope | Hit Rate Target |
|---|---|---|---|
| KV Cache (attention) | Key-value pairs from attention computation | Per-session | N/A (session-scoped) |
| Prompt cache | Shared prefix token activations | Multi-tenant | ≥ 40% |
| Response cache (semantic) | Model outputs for semantically similar inputs | Global | ≥ 20% |
| Embedding cache | Input text embeddings | Global | ≥ 60% |
| Feature cache | Intermediate layer activations | Request-scoped | Session-level |

---

## Strategy 1: Prompt Prefix Caching

Cache shared prompt prefixes (e.g., system prompts, RAG context) across requests.

```
PREFIX CACHING ALGORITHM:
  1. For each incoming request, extract prefix tokens (system prompt + static context)
  2. Compute prefix hash = SHA-256(prefix_token_ids)
  3. Lookup prefix_hash in KV cache store
  4. IF HIT:
       Load cached KV activations for prefix tokens
       Only run model forward pass on NEW tokens (user message + output)
       Cost reduction: (prefix_tokens / total_tokens) × inference_cost
  5. IF MISS:
       Run full forward pass
       Store KV activations for prefix tokens in cache

CACHE EVICTION POLICY:
  - LRU (Least Recently Used) is default
  - Prefix size weighting: evict smaller prefixes before larger ones
    (larger prefixes are more expensive to recompute)
  - Pin system prompts: never evict system prompt KV cache (static, high reuse)
```

**Savings model:**
```
savings_pct = prefix_hit_rate × (prefix_tokens / (prefix_tokens + avg_completion_tokens))
# Example: 60% hit rate, 1000 prefix tokens, 200 completion tokens
# savings = 0.60 × (1000 / 1200) = 50% average cost reduction
```

---

## Strategy 2: Semantic Response Cache

Cache responses to semantically similar queries (not just exact matches):

```
SEMANTIC CACHE PROTOCOL:
  1. Embed incoming query: q_embed = embed(query)
  2. Search cache index: neighbors = knn_search(q_embed, cache_index, k=5)
  3. For each neighbor n:
     similarity = cosine_similarity(q_embed, n.query_embed)
     IF similarity > semantic_similarity_threshold:
       IF n.response_still_valid():  # Check TTL and staleness
         RETURN n.cached_response (with staleness warning if > 1h old)
  4. IF no cache hit:
     response = model.generate(query)
     cache.add(query, q_embed, response, ttl=cache_ttl_policy(query))

CACHE INVALIDATION:
  Time-based: TTL set by query sensitivity
    Factual knowledge: 24h TTL
    Recent events: 1h TTL
    Code generation: 7-day TTL (stable)
    Current data: No caching (real-time queries)

  Content-based: Invalidate if underlying knowledge base updated
    Use cache_tag = hash(relevant_knowledge_sources)
    Invalidate on knowledge base version increment
```

---

## Strategy 3: Tiered Cache Architecture

```
CACHE TIER HIERARCHY:
  L1: In-memory (hot cache)
    - Size: 4GB per inference server
    - Latency: < 1ms read
    - Hit target: ≥ 40% of all requests
    - Contents: System prompt KV caches, highest-frequency query responses

  L2: Redis cluster (warm cache)
    - Size: 100GB distributed
    - Latency: < 5ms read
    - Hit target: ≥ 25% of L1 misses
    - Contents: Prompt prefix caches, moderately frequent queries

  L3: S3/object store (cold cache)
    - Size: Unlimited
    - Latency: < 50ms read
    - Hit target: N/A (archival + pre-warming use only)
    - Contents: Pre-computed embeddings, historical popular query responses

LOOKUP WATERFALL:
  check_L1 → HIT? return
  check_L2 → HIT? promote to L1, return
  check_L3 → HIT? promote to L2, return
  MISS → generate, store in L1 (overflow to L2 on eviction)
```

---

## Cache Placement Scoring

When deciding which items to cache and where:

```python
def cache_placement_score(item):
    """
    Score items for cache placement priority.
    Higher score = higher priority for caching and L1 placement.
    """
    access_frequency_score = min(100, item.requests_per_hour × 5)
    # 20+ requests/hour = max score

    compute_cost_score = min(100, item.generation_cost_ms / 10)
    # 1000ms generation = max score (expensive to generate)

    reuse_probability_score = min(100, item.semantic_neighbor_count × 10)
    # 10+ semantic neighbors = max score (likely to be reused)

    staleness_risk_score = max(0, 100 - item.knowledge_volatility_score × 20)
    # High volatility = lower caching priority

    placement_score = (
        access_frequency_score × 0.40 +
        compute_cost_score × 0.30 +
        reuse_probability_score × 0.20 +
        staleness_risk_score × 0.10
    )

    cache_tier = (
        "L1" if placement_score >= 80 else
        "L2" if placement_score >= 50 else
        "L3" if placement_score >= 20 else
        "NO_CACHE"
    )

    return CachePlacement(score=placement_score, tier=cache_tier)
```

---

## Cache Performance Metrics

```yaml
cache_metrics:
  period: "2026-05-07T00:00:00Z to 2026-05-07T23:59:59Z"

  overall:
    total_requests: 142000
    cache_hits: 61340
    overall_hit_rate: 0.432
    avg_response_time_cache_hit_ms: 4.2
    avg_response_time_cache_miss_ms: 847
    latency_reduction_pct: 99.5  # For cache hits
    compute_cost_savings_pct: 43.2

  by_tier:
    L1:
      hit_rate: 0.38
      avg_latency_ms: 0.8
      evictions_per_hour: 420
      memory_utilization_pct: 87

    L2:
      hit_rate: 0.23  # Of L1 misses
      avg_latency_ms: 3.1
      evictions_per_hour: 180

  semantic_cache:
    similarity_threshold: 0.92
    hits: 8400
    false_positive_rate: 0.003  # Wrong answer served
    avg_similarity_of_hits: 0.96

  recommendations:
    - "Increase L1 cache size from 4GB to 6GB (hit rate would improve ~5%)"
    - "Lower semantic similarity threshold from 0.92 to 0.90 for code tasks (+8% hit rate, review false positive rate)"
```