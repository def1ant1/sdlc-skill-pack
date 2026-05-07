# Institutional Knowledge Query — Knowledge Index Schema

## Knowledge Source Registry

| Source Type | Examples | Ingestion Method | Refresh Cadence |
|-------------|---------|-----------------|----------------|
| `lesson` | Lessons learned records | lessons-learned-extraction | On extraction |
| `decision` | Architecture Decision Records (ADRs) | document-intelligence | On publish |
| `runbook` | Operational runbooks | manual upload + CI | On git push |
| `standard` | Coding standards, security policies | manual upload | On version bump |
| `postmortem` | Incident post-mortems | document-intelligence | On completion |
| `benchmark` | Performance benchmark results | inference-engine-benchmarking | After each run |
| `meeting_summary` | Board/team meeting notes | audio-video-processing | After transcript |
| `skill_contract` | SKILL.md behavioral contracts | validate_frontmatter CI | On git push |

---

## Knowledge Entry Schema

```yaml
knowledge_entry:
  entry_id: "KW-2026-xxxxx"
  source_type: lesson | decision | runbook | standard | postmortem | benchmark | meeting_summary | skill_contract
  source_id: "LES-2026-xxxxx"         # ID in originating system
  source_uri: "gs://apotheon-docs/..."  # Optional: raw document location

  title: "Connection pool must be tuned for expected concurrency"
  summary: |
    PostgreSQL connection pools must be sized to the expected peak concurrent
    workers, not left at application defaults. Formula: pool_size = peak_concurrent_workers × 1.2.

  full_content: |
    [Full text of the lesson, decision, or document...]

  tags: [database, postgresql, connection-pool, deployment, performance]
  project_ids: []          # Empty = applies globally
  skill_names: []          # Empty = applies to all skills
  phase: []                # SDLC phases this applies to; empty = all

  data_classification: INTERNAL   # PUBLIC | INTERNAL | CONFIDENTIAL | RESTRICTED
  author: "sre-agent"
  created_at: "2026-05-07T10:00:00Z"
  last_updated_at: "2026-05-07T10:00:00Z"
  version: 1

  embedding:
    model: "text-embedding-3-large"
    dimensions: 3072
    vector: [...]            # Stored in vector DB; not serialized to YAML

  indexed_at: "2026-05-07T10:05:00Z"
  searchable: true
  archived: false
```

---

## Query API

### Semantic Search

```yaml
knowledge_query:
  query_id: "KW-QRY-2026-xxxxx"
  query_text: "how to size database connection pools for high concurrency"
  query_type: semantic   # semantic | keyword | hybrid

  filters:
    source_types: []        # Empty = all sources
    tags: []
    project_ids: []
    skill_names: []
    data_classification: [PUBLIC, INTERNAL, CONFIDENTIAL]
    date_range: null

  retrieval:
    top_k: 10
    min_relevance_score: 0.70
    rerank: true            # Apply cross-encoder reranking

  output_format: entries | summaries | augmented_prompt
```

### Augmented Prompt Output

When `output_format: augmented_prompt`, the query result is formatted for direct injection into an LLM context window:

```
[Institutional Knowledge Context]

1. (Score: 0.94) Connection Pool Sizing — Lesson LES-2026-00041
   Pool size must be tuned for expected concurrency. Formula: pool_size = peak_workers × 1.2.
   Tags: database, postgresql, connection-pool
   Source: Post-incident review, 2026-05-07

2. (Score: 0.88) PostgreSQL Deployment Checklist — Runbook RUN-2026-00008
   Pre-deployment: verify pg_max_connections ≥ pool_size × replica_count.
   Source: SRE Runbook Library, v2.1

[End Institutional Knowledge Context]
```

---

## Vector Index Configuration

```yaml
vector_index:
  backend: pgvector   # pgvector | qdrant | pinecone | weaviate
  collection_name: "apotheon-knowledge"
  dimensions: 3072
  distance_metric: cosine

  embedding_model:
    id: "text-embedding-3-large"
    batch_size: 100
    rate_limit_rpm: 3000

  index_params:
    index_type: HNSW
    m: 16               # HNSW graph connections per node
    ef_construction: 200

  metadata_filters:
    indexed_fields:
      - source_type
      - tags
      - project_ids
      - data_classification
      - searchable

  refresh:
    strategy: incremental   # Only re-embed changed documents
    schedule: "*/15 * * * *"  # Every 15 minutes
```

---

## Knowledge Lifecycle

```
1. Source document created / updated
        │
        ▼
2. Ingestion trigger (CI push / schedule / event)
        │
        ▼
3. Extract text and metadata
   └── document-intelligence for PDFs, DOCX
   └── Direct YAML parse for structured sources
        │
        ▼
4. Generate embedding (text-embedding-3-large)
        │
        ▼
5. Upsert to vector index
        │
        ▼
6. Update knowledge entry metadata in DB
        │
        ▼
7. Available for query (eventual consistency ≤ 15 min)
```

---

## Staleness & Versioning Policy

| Source Type | Stale After | Action |
|-------------|------------|--------|
| `lesson` | 365 days with no view | Flag for archival review |
| `runbook` | 90 days with no update | Alert runbook owner |
| `standard` | 180 days with no version bump | Alert standards owner |
| `decision` | Never (immutable history) | Archive only on explicit request |
| `benchmark` | Superseded by newer run for same model | Auto-archive previous |

When a newer version of a document is ingested, the old entry is archived (`archived: true`) and the new entry takes its place. Queries return only non-archived entries by default.