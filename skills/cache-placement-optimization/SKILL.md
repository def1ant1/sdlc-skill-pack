---
name: cache-placement-optimization
description: Optimizes KV cache placement and prefix cache configuration across GPU VRAM to maximize cache hit rates, reduce redundant computation, and improve inference throughput.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [cluster-management, kv-cache-management, local-runtime, telemetry]

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

KV cache placement specialist for the inference serving layer. Analyzes cache hit rates,
prefix reuse patterns, and VRAM allocation to optimize how KV caches are sized and distributed
across GPUs — maximizing cache efficiency and reducing redundant computation.

## Activation Triggers

- KV cache hit rate falls below 60%
- VRAM pressure causing cache evictions at high rate
- New prefix-heavy workload detected requiring cache warmup
- Quarterly cache configuration review

## Execution Protocol

1. **Measure current cache performance**: Collect KV cache hit rate, eviction rate, VRAM
   allocated to cache, and prefix reuse statistics per model from telemetry.

2. **Analyze prefix patterns**: Identify the most frequently reused prompt prefixes; compute
   expected hit rate improvement from dedicated prefix cache allocation.

3. **Compute optimal cache sizing**: Balance VRAM allocation between KV cache and model
   weights; solve allocation to maximize expected hit rate subject to VRAM constraints.

4. **Configure prefix caching**: Update vLLM/SGLang prefix cache configuration with optimal
   cache size and eviction policy (LRU with recency bias for system prompts).

5. **Warm high-value prefixes**: Pre-populate cache with the top-N most reused system
   prompt prefixes to eliminate cold-start latency on next restart.

6. **Validate improvement**: Measure cache hit rate and P95 latency for 15 minutes post-change;
   roll back configuration if hit rate decreases or latency degrades.

## Output Format

Cache optimization report with: before/after hit rates, VRAM allocation change, prefix warmup
list, configuration diff applied, and observed latency improvement.

## References

- `references/cache-optimization-strategies.md` — cache sizing formulas, prefix cache warmup methodology, eviction policy tuning