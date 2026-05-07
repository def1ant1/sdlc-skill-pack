# Cache Zones

Used by `core/kv-cache-management/SKILL.md` to define KV cache zone specifications,
token budgets, TTL policies, and eviction priority for each zone.

---

## Zone Definitions

### Zone 1: system-core

| Property | Value |
|---|---|
| Content | Core system prompt, safety policy, output format rules, platform identity |
| TTL | Entire session (never evict) |
| Max tokens | 1000 |
| Eviction priority | Never evict |
| Pre-warm | Yes — at session start |
| Stability | Completely static within a session |
| Backend support | vLLM ✓, SGLang ✓, Ollama ✓ (implicit), llama.cpp ✓ |

**Optimization rule**: Keep under 800 tokens. Every token added here is cached for every
request in the session — over-engineering the system prompt is expensive.

---

### Zone 2: skill-definitions

| Property | Value |
|---|---|
| Content | SKILL.md content for all currently active skills |
| TTL | Current phase (evict when phase transitions + skill unloads) |
| Max tokens | 5000 (across all active skills) |
| Eviction priority | Low — evict inactive skill definitions first |
| Pre-warm | Yes — when orchestrator loads a skill |
| Stability | Changes on skill load/unload |

**Optimization rule**: Load only the active skill's SKILL.md, not the full skill pack.
A single SKILL.md should be < 300 lines (500–800 tokens). If multiple skills are active
simultaneously, concatenate in dependency order.

---

### Zone 3: shared-context

| Property | Value |
|---|---|
| Content | Memory packet (project, decisions, constraints, phase_status, risks, open_questions, next_action) |
| TTL | Current phase; updated on phase transition |
| Max tokens | 8000 |
| Eviction priority | Medium — can be reloaded from memory packet |
| Pre-warm | Yes — after memory packet is initialized or updated |
| Stability | Updated at phase transitions; stable within a phase |

**Optimization rule**: Load the scoped handoff packet (not the full memory packet) to
minimize tokens. The full packet is at most needed during compression or full audit.

---

### Zone 4: retrieval-context

| Property | Value |
|---|---|
| Content | GraphRAG / VectorRAG results for the current query |
| TTL | Single request (evict after response generated) |
| Max tokens | 4000 |
| Eviction priority | High — always evict first (re-fetchable) |
| Pre-warm | No |
| Stability | Changes with every query |

**Optimization rule**: This zone is inherently un-cacheable. Keep it as small as possible
(top-5 reranked chunks, not top-20). Every token here is not reused.

---

### Zone 5: conversation

| Property | Value |
|---|---|
| Content | Recent conversation turns (rolling window) |
| TTL | Session |
| Max tokens | 3000 |
| Eviction priority | Highest — drop oldest turns first |
| Pre-warm | No |
| Stability | Appended with every turn |

**Optimization rule**: Keep a rolling window of the last 5–8 turns. Older turns should
be summarized (via `summarize_context.py`) and moved to shared-context, not retained verbatim.

---

## Eviction Order

When VRAM pressure requires cache eviction, evict in this order:

```
1. retrieval-context (entire zone — re-fetchable)
2. conversation (oldest turns first)
3. skill-definitions (inactive skills only)
4. shared-context (only if memory packet can be reloaded from storage)
5. system-core: NEVER EVICT
```

---

## Backend-Specific Notes

### vLLM
- Uses automatic prefix caching with a LRU eviction policy
- Set `--enable-prefix-caching` and `--gpu-memory-utilization 0.90`
- Prefix cache is shared across concurrent requests with the same prefix
- Prompt ordering is critical: stable zones must precede variable zones

### SGLang
- Uses RadixAttention for tree-structured prefix caching
- Cache is shared across requests sharing the same prefix tree branch
- Branching point (where conversation diverges) determines cache reuse

### Ollama
- Implicit KV cache per-session; no explicit control
- To maximize reuse: keep system prompt identical across requests in the same session

### llama.cpp
- `--cache-reuse N`: enables prefix reuse for last N tokens
- Set `--cache-reuse 512` to cache the system + skill definition prefix

---

## VRAM Budget for Cache

| Hardware Tier | Total VRAM | Model VRAM | Cache VRAM Budget |
|---|---|---|---|
| DGX Spark (128 GB) | 128 GB | 40–90 GB | 10–40 GB |
| Workstation (48 GB) | 48 GB | 20–40 GB | 4–12 GB |
| Laptop GPU (16 GB) | 16 GB | 8–12 GB | 2–4 GB |

Target: allocate 20–30% of available VRAM to the KV cache. Below 10% causes thrashing.
Above 40% starves the model weights.