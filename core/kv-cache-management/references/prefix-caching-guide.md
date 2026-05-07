# Prefix Caching Guide

## Overview

KV cache prefix caching reuses previously computed key-value tensors for shared
prompt prefixes, reducing both latency and compute cost for prompts with common
leading content (system prompts, skill instructions, context documents).

---

## Cache Hit Conditions

A cache hit occurs when the model processes a new request where:
1. The leading tokens of the new prompt exactly match a cached prefix
2. The cached prefix is still in memory (not evicted)
3. The model and quantization settings match the cached computation

**Critical**: Any character difference (space, punctuation, capitalization) in the
prefix breaks the cache hit. Prefix order matters.

---

## Canonical Prompt Order

To maximize cache hits, always structure prompts in this order (from most stable to
least stable content):

```
1. System prompt (role + invariant instructions)     ← MOST STABLE
2. Skill-specific context (current skill instructions)
3. Retrieved context (RAG documents)
4. Conversation history (turns prior to current)
5. Tool definitions (if tool use)
6. Current user message                              ← LEAST STABLE
```

Never insert dynamic or user-specific content before stable content.

---

## Cache Zones

| Zone | Content | Stability | Cache Hit Rate Target |
|---|---|---|---|
| Zone 0 | Base system prompt | Permanent (never changes) | ~100% |
| Zone 1 | Skill instructions | High (changes on skill update) | > 90% |
| Zone 2 | Retrieved context | Medium (changes per query) | 60–80% |
| Zone 3 | Conversation history | Low (changes each turn) | 30–60% |
| Zone 4 | Current user message | Zero (always new) | 0% |

---

## Implementation Patterns

### Anthropic API (claude models)

Use the `cache_control: {"type": "ephemeral"}` marker on large, stable blocks:

```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": LONG_SKILL_CONTEXT,  # stable content
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": user_query  # dynamic content — no cache marker
            }
        ]
    }
]
```

### vLLM (local inference)

Enable prefix caching in vLLM server configuration:

```python
# In vLLM startup
LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    enable_prefix_caching=True,
    gpu_memory_utilization=0.90,
    max_model_len=32768,
)
```

---

## Cache Eviction Policy

When GPU VRAM for KV cache is exhausted, evict using LRU (Least Recently Used):

1. Evict Zone 4 blocks first (most dynamic, lowest reuse value)
2. Then Zone 3 (conversation history — moderate reuse)
3. Only evict Zone 0–2 if absolutely necessary

Never pre-emptively evict Zone 0 (base system prompt) — it has the highest hit rate.

---

## Measuring Cache Effectiveness

Monitor these metrics in telemetry:

| Metric | Formula | Target |
|---|---|---|
| Cache hit rate | cache_hits / total_requests | > 70% |
| Tokens saved by cache | cached_prefix_tokens × hit_rate | Track trend |
| TTFT reduction | (cold_TTFT - cached_TTFT) / cold_TTFT | > 40% |
| Cost reduction | cached_input_cost_savings | Track monthly |

Log all cache hit/miss events to telemetry with: request_id, model, prefix_length,
cache_hit (bool), and zone.

---

## Common Mistakes

| Mistake | Effect | Fix |
|---|---|---|
| Putting dynamic content before system prompt | Zero cache hits on Zone 0 | Move dynamic content to end |
| Trailing whitespace variation in system prompt | Cache miss on Zone 0 | Trim and normalize prompts |
| Different model loaded than cached | Cache miss | Pin model version |
| Too many unique retrieved documents | Low Zone 2 hit rate | Use document deduplication |