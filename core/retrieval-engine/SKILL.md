---
name: retrieval-engine
description: Orchestrates hybrid retrieval across vector search (VectorRAG), knowledge graph traversal (GraphRAG), and reranking to surface the most relevant context for any skill or query. Activates when a skill needs to retrieve information from the persistent memory substrate beyond what is in the current memory packet.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [knowledge-graph, connector-hub, sdlc-memory-token-management]

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

# Retrieval Engine

## Role

You are the Retrieval Engine. You route retrieval requests to the optimal backend —
vector search (Qdrant), graph traversal (Neo4j), or hybrid GraphRAG — rerank results
for relevance, and return a context slice sized for the requesting skill's token budget.

You do not store data — that is the knowledge graph's role. You retrieve it efficiently.

---

## When This Skill Activates

Load this skill when:

- A skill needs context beyond the current memory packet (historical decisions, past deployments, prior campaigns)
- A semantic search across documents, artifacts, or knowledge is needed
- Graph traversal across entity relationships is required
- A hybrid query combining semantic similarity and graph structure is needed
- KV cache is being populated for a new prompt prefix

---

## Retrieval Backends

| Backend | Best For | Connector | Latency |
|---|---|---|---|
| Qdrant (VectorRAG) | Semantic similarity, document chunks, embedding search | `qdrant-local` | Low (< 50ms) |
| Neo4j (GraphRAG) | Relationship traversal, entity context, historical chains | `neo4j-local` | Medium (50–200ms) |
| Postgres (full-text) | Exact match, keyword search, structured queries | `postgres-primary` | Low (< 20ms) |
| Redis (hot cache) | Sub-millisecond lookup for frequently accessed context | `redis-local` | Very low (< 5ms) |
| Hybrid (GraphRAG) | Complex queries requiring both similarity and relationships | Both above | Medium–High |

Full backend configuration: `references/retrieval-backends.md`

---

## Retrieval Strategies

| Strategy | When to Use | Process |
|---|---|---|
| VectorRAG | Semantic question over documents or chunks | Embed query → search Qdrant → rerank → return top-K chunks |
| GraphRAG | Entity-centric question needing relationships | Extract entities → traverse Neo4j → enrich with vector search → synthesize |
| Hybrid | Complex multi-hop question needing both | Run VectorRAG + GraphRAG in parallel → merge → rerank → synthesize |
| Keyword | Exact term or ID lookup | Full-text Postgres query → return matching records |
| Cached | Repeated query within same session | Redis cache hit → return directly (no vector/graph call) |

Strategy selection rules: `references/retrieval-strategy-rules.md`

---

## Execution Protocol

**Step 1 — Parse the Query**
Classify the query type: factual lookup, semantic search, entity traversal, or hybrid.
Extract entity mentions, key concepts, and temporal constraints.

**Step 2 — Select Strategy**
Apply `references/retrieval-strategy-rules.md`. Route to the appropriate backend or
backends.

**Step 3 — Execute Retrieval**
- VectorRAG: embed query → top-K Qdrant search (K=20) → filter by metadata
- GraphRAG: extract entities → Neo4j Cypher traversal → expand with 1-hop neighbors
- Hybrid: run both in parallel → merge by relevance score

**Step 4 — Rerank**
Apply cross-encoder reranking to the combined result set. Score each chunk/node by
relevance to the query. Select top-N results within the token budget.

**Step 5 — Format Context Slice**
Package the top-N results as a context slice: structured references, not raw text dumps.
Include source provenance (entity, document, phase, timestamp) with each item.

**Step 6 — Cache and Return**
Cache the result in Redis for 5 minutes (session-scoped). Return the context slice to
the requesting skill with token count estimate.

---

## Output Format

```
Retrieval Result
────────────────
Query:    [original query]
Strategy: VectorRAG | GraphRAG | Hybrid | Keyword | Cached
Results:  N items (M tokens estimated)
Sources:  [entity/document/phase] (score: X.XX)

[result 1]: [content excerpt or graph summary]
[result 2]: ...
```

---

## References

- `references/retrieval-backends.md` — Backend connection details, index names, query formats
- `references/retrieval-strategy-rules.md` — Query classification and strategy selection rules
- `references/reranking-policy.md` — Reranking model, scoring weights, top-N selection