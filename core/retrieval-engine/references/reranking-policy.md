# Reranking Policy

## Overview

After initial retrieval (vector + BM25), results are re-ranked to improve relevance.
This document defines the reranking signals, weights, and rules.

---

## Reranking Pipeline

```
Initial results (merged via RRF)
        │
        ▼
1. Access control filter (hard — remove unauthorized)
        │
        ▼
2. Diversity filter (remove near-duplicate chunks from same source)
        │
        ▼
3. Signal scoring (apply multiplicative boosts)
        │
        ▼
4. Final sort by adjusted score
        │
        ▼
Return top-N to caller
```

---

## Reranking Signals

| Signal | Boost Factor | Condition | Rationale |
|---|---|---|---|
| Exact title match | ×1.5 | Query terms appear in document title | Title is the strongest relevance signal |
| Section heading match | ×1.3 | Query terms appear in a ## heading | Section headings indicate topic focus |
| Authority document | ×1.3 | Category is `policies` or `decisions` | Authoritative sources preferred over opinions |
| Recency boost | ×1.2 | Document updated in last 30 days | Fresh information preferred for time-sensitive queries |
| Context affinity | ×1.25 | Document in same project/skill as current workflow | Project context improves relevance |
| Exact phrase match | ×1.4 | Query phrase appears verbatim in chunk | Exact matches are highly relevant |
| Stale penalty | ×0.7 | Document not updated in > 12 months | Old docs may be outdated |
| Draft penalty | ×0.8 | Document has `draft` or `wip` in metadata | Prefer finalized documents |

---

## Cross-Encoder Reranking (Optional)

For high-stakes queries (e.g., governance decisions, compliance checks), apply a
cross-encoder reranking model:

1. Retrieve top-20 via vector + BM25 + RRF
2. Run cross-encoder model on (query, chunk) pairs to produce relevance scores
3. Re-sort by cross-encoder score
4. Return top-5

Cross-encoder adds ~200ms latency; use only when precision is critical.

**Recommended model**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (local inference via Ollama).

---

## Diversity Filter

Before reranking, remove near-duplicate results:

1. Compute pairwise cosine similarity for all retrieved chunks
2. If two chunks from the same source have similarity > 0.95: keep only the higher-scored one
3. If results from more than 3 sources return the same core answer: return only the most authoritative

**Goal**: Avoid returning 5 results that all say the same thing.

---

## Query Type Detection

Apply different reranking strategies based on detected query type:

| Query Type | Strategy | Example |
|---|---|---|
| Fact lookup | Exact match boost; authority boost | "What is the SLO for the account service?" |
| Exploration | Diversity boost; penalize near-duplicates less | "What are the governance principles?" |
| Recent events | Recency boost ×1.5; stale penalty ×0.5 | "What happened in this week's incident?" |
| Decision retrieval | Authority boost; cross-encoder | "What did we decide about the database migration?" |
| Code search | Language filter; exact symbol match | "Show me the AccountRepository interface" |

---

## Quality Metrics

Monitor reranking quality via:

| Metric | Target | Measurement |
|---|---|---|
| NDCG@5 | > 0.80 | Evaluated on held-out query set quarterly |
| Click-through rate (top result) | > 60% | Tracked via user interaction events |
| "No useful result" rate | < 15% | Tracked via explicit feedback |