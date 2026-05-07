# Retrieval Strategy Rules

Used by `core/retrieval-engine/SKILL.md` to classify incoming queries and select
the optimal retrieval strategy and backend.

---

## Query Classification

| Query Type | Signals | Strategy |
|---|---|---|
| Semantic document search | "find", "search for", "what does X say about", open-ended question | VectorRAG |
| Entity lookup | Entity name + property question, "what is the status of", "when was X deployed" | GraphRAG or Keyword |
| Relationship traversal | "what decisions led to", "which customers use", "trace the chain from" | GraphRAG |
| Cross-entity synthesis | Multi-hop: "which campaigns drove revenue for products that used feature X" | Hybrid |
| Exact ID lookup | DEC-NNN, WP-NNN, ART-NNN, known identifier | Keyword → Postgres |
| Recent history | "last N workflows", "most recent deployment", "latest gate result" | Keyword + timestamp filter |
| Semantic + structure | "find similar architecture decisions that also involved security constraints" | Hybrid |

---

## Strategy Selection Algorithm

```
1. Extract entity mentions → if 2+ named entities with relationship question → GraphRAG
2. Check for known ID patterns (DEC-, WP-, ART-, RISK-) → Keyword
3. Check for temporal constraints ("last", "most recent", "before date") → Keyword
4. Check for semantic signals ("similar to", "related to", "find documents") → VectorRAG
5. Check for multi-hop or synthesis requirement → Hybrid
6. Default → VectorRAG
```

---

## VectorRAG Configuration

| Parameter | Value | Notes |
|---|---|---|
| Embedding model | `Qwen-Embedding-3` (local) | 1536-dim embeddings |
| Index | Qdrant `apotheon-main` | HNSW index, cosine similarity |
| Top-K | 20 (pre-rerank) | Reduced to 5–10 after reranking |
| Min score | 0.65 | Below threshold: discard |
| Metadata filters | phase, entity_type, date_range | Applied pre-search |
| Chunk overlap | 50 tokens | Set at indexing time |

---

## GraphRAG Configuration

| Parameter | Value | Notes |
|---|---|---|
| Graph DB | Neo4j (local) | Connector: `neo4j-local` |
| Default traversal depth | 2 hops | Increase to 3 for multi-hop queries |
| Max nodes returned | 50 | Reranked to top 10 |
| Relationship types | All (per graph-schema.md) | Filter by query context |
| Vector enrichment | Yes — each graph result augmented with Qdrant chunk | Requires both backends |

---

## Hybrid Mode

Hybrid retrieval runs VectorRAG and GraphRAG in parallel, then merges:

1. VectorRAG returns: chunks with vector scores
2. GraphRAG returns: entity + relationship subgraph
3. Merge: for each entity in graph result, find matching chunks from vector result
4. Deduplicate: prefer graph-anchored results when both contain same fact
5. Rerank: apply cross-encoder over merged set
6. Return top-N

Hybrid mode adds ~100–300ms latency vs single-backend retrieval.

---

## Caching Rules

| Cache Level | TTL | Scope | Invalidated By |
|---|---|---|---|
| Redis hot cache | 5 minutes | Session | New write to same entity |
| Redis warm cache | 30 minutes | Cross-session | Graph write to related entity |
| No cache | — | One-time queries | n/a |

Cache the embedding of the query (not the result) to detect near-duplicate queries within
the same session and serve from cache.