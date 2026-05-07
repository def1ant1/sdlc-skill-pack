# Retrieval Fusion

## Hybrid Search Architecture

Enterprise search combines two retrieval methods and fuses their results:

```
Query
  │
  ├── Vector Search (semantic) ──────► top-K candidates (scored by cosine similarity)
  │       via retrieval-engine / Qdrant
  │
  └── BM25 Search (keyword) ─────────► top-K candidates (scored by BM25)
              via in-memory index
                      │
                      └── Reciprocal Rank Fusion (RRF)
                                  │
                                  └── Re-ranking (recency, authority, context)
                                              │
                                              └── Access Control Filter
                                                          │
                                                          └── Final top-N results
```

---

## Reciprocal Rank Fusion (RRF)

RRF combines ranked lists without requiring score normalization:

```
RRF_score(doc) = Σ 1 / (k + rank_in_list_i)

Where:
  k = 60  (constant; reduces impact of top-ranked but irrelevant results)
  rank_in_list_i = rank of doc in the i-th retrieval list (1-indexed)
  Σ = sum over all retrieval lists (vector + BM25)
```

**Example**:
```
Document A: rank 3 in vector, rank 1 in BM25
  RRF = 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226

Document B: rank 1 in vector, rank 10 in BM25
  RRF = 1/(60+1) + 1/(60+10) = 0.01639 + 0.01429 = 0.03068

Document A ranks higher despite lower vector rank, due to strong BM25 match.
```

---

## Re-ranking Weights

After RRF, apply multiplicative boosts:

```python
def rerank_score(rrf_score, doc):
    score = rrf_score
    # Recency boost
    days_old = (today - doc.updated_at).days
    if days_old < 30:
        score *= 1.20
    # Authority boost
    if doc.category in ('policies', 'decisions'):
        score *= 1.30
    # Title match boost
    if query_terms_in_title(doc.title, query):
        score *= 1.50
    return score
```

---

## Access Control Filter

Applied as a post-retrieval hard filter (before returning results to caller):

```python
def access_filter(documents, requester):
    allowed = []
    for doc in documents:
        if doc.access_level == 'all-internal':
            allowed.append(doc)
        elif doc.access_level == 'sdlc-agents' and requester.is_sdlc_agent:
            allowed.append(doc)
        elif doc.access_level == 'customers-restricted' and requester.has_customer_access:
            allowed.append(doc)
        elif doc.access_level == 'hr-restricted' and requester.has_hr_access:
            allowed.append(doc)
    return allowed
```

Access levels are set at indexing time from the source document's `access_level` field.

---

## Query Expansion

Before retrieval, expand the query to improve recall:

1. **Acronym expansion**: "SLO" → "SLO service level objective"
2. **Synonym addition**: "error budget" → "error budget burn rate"
3. **Entity recognition**: If query contains a skill name, also search for its description
4. **Compound decomposition**: "meeting action items" → search for "action items" + "meeting" separately

Query expansion is applied to the BM25 query only; vector query uses the original.

---

## Retrieval Parameters

| Parameter | Value | Notes |
|---|---|---|
| vector_top_k | 20 | Retrieve top-20 from vector search |
| bm25_top_k | 20 | Retrieve top-20 from BM25 |
| rrf_k | 60 | RRF fusion constant |
| final_top_n | 5 | Return to caller (default) |
| min_score | 0.01 | Discard RRF results below this |
| dedup_by | source | Return only one chunk per source file |