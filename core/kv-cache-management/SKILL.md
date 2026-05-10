---
name: kv-cache-management
description: Manages KV cache zones for the local LLM runtime to maximize prefix cache hits, minimize redundant computation, and optimize VRAM utilization. Defines cache zones for system prompts, skill definitions, shared context, and per-request prefixes.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [local-runtime, connector-hub]

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

# KV Cache Management

## Role

You are the KV Cache Management skill. You structure prompt prefixes to maximize KV cache
reuse across inference requests, define cache zones that align with local model backend
capabilities (vLLM RadixAttention, SGLang, llama.cpp), and monitor cache hit rates to
optimize VRAM efficiency.

You do not run inference — you structure prompts and manage cache zones so inference runs
faster and cheaper.

---

## When This Skill Activates

Load this skill when:

- A new session begins and system prompts / skill definitions must be pre-cached
- A repeated prompt prefix is detected and a cache hit opportunity exists
- VRAM is under pressure and cache eviction must be prioritized
- Cache hit rate falls below the warn threshold (< 60%)
- A new skill or shared context block is added that should be pre-warmed

---

## Cache Zone Architecture

| Zone | Content | TTL | Priority | Estimated Tokens |
|---|---|---|---|---|
| `system-core` | Core system prompt, safety rules, output format instructions | Session | Highest | 500–1000 |
| `skill-definitions` | Active SKILL.md content for loaded skills | Phase | High | 1000–5000 |
| `shared-context` | Memory packet (non-conversation sections), constraints, decisions | Phase | High | 2000–8000 |
| `retrieval-context` | GraphRAG / VectorRAG results for current query | Request | Medium | 1000–4000 |
| `conversation` | Recent turns (rolling window) | Turn | Low | 500–3000 |

Full zone definitions: `references/cache-zones.md`

---

## Execution Protocol

**Step 1 — Structure the Prompt Prefix**
Order prompt sections to maximize prefix stability. Stable sections (system, skills,
shared context) must come before variable sections (retrieval results, conversation).

The canonical prompt order:
```
[system-core zone]
[skill-definitions zone]
[shared-context zone]
[retrieval-context zone]
[conversation zone]
[current query]
```

**Step 2 — Register Cache Zones**
On session start, register the `system-core` and `skill-definitions` zones with the
local runtime backend. For vLLM: pre-fill prefix cache. For SGLang: use RadixAttention.
For Ollama: no explicit pre-fill; cache is implicit.

**Step 3 — Detect Cache Hit Opportunities**
Before each inference request, compute the common prefix length with the previous request.
If common prefix > 512 tokens, a cache hit is expected. Log the hit.

**Step 4 — Monitor Hit Rate**
Track the rolling cache hit rate (last 50 requests). Emit WARN if hit rate < 60%.
Emit ALERT if hit rate < 40% (indicates poor prefix ordering or too much zone churn).

**Step 5 — Manage Eviction**
When VRAM pressure requires cache eviction, evict in this order:
1. `conversation` (oldest turns)
2. `retrieval-context` (re-fetchable)
3. `skill-definitions` for inactive skills
4. `shared-context` (only if memory packet can be reloaded)
5. Never evict `system-core`

**Step 6 — Pre-warm on Skill Load**
When the orchestration layer loads a new skill, pre-fill its SKILL.md into the
`skill-definitions` zone before the first inference request that uses it.

---

## Cache Hit Rate Targets

| Scenario | Target Hit Rate | Notes |
|---|---|---|
| Same skill, consecutive requests | > 85% | System + skill prefix stable |
| Same workflow, phase transition | > 70% | Shared context changes; skill may change |
| Different workflows, same session | > 50% | System core still cached |
| Cold start (new session) | 0% for first request | Pre-warm immediately |

---

## Output Format

Cache status is reported as part of telemetry events, not surfaced directly to users.
On operator request:

```
KV Cache Status
───────────────
Session Hit Rate: XX% (last 50 requests)
Active Zones:     system-core (Xk tokens), skill-definitions (Xk), shared-context (Xk)
VRAM Used (cache):X GB
Eviction Events:  N (last hour)
Status:           OPTIMAL | WARN (< 60%) | ALERT (< 40%)
```

---

## References

- `references/cache-zones.md` — Zone definitions, token budgets, TTL policies, eviction order
- `references/prefix-caching-guide.md` — How to structure prompts for maximum cache reuse per backend