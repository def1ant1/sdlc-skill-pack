# Retrieval Backends

## Backend Inventory

| Backend | Role | Primary Use Case | Deployment |
|---|---|---|---|
| Qdrant | Vector store | Semantic search across all corpora | Local (Docker) |
| Neo4j | Graph database | Knowledge graph queries and traversal | Local (Docker) |
| Redis | Cache | Hot query caching; recent embeddings | Local (Docker) |
| BM25 (in-memory) | Keyword index | Exact and keyword matching | In-process |

---

## Qdrant Configuration

```yaml
# qdrant configuration
qdrant:
  host: localhost
  port: 6333
  grpc_port: 6334
  collections:
    - name: platform_skills
      vector_size: 768
      distance: Cosine
      on_disk_payload: true
    - name: platform_documents
      vector_size: 768
      distance: Cosine
      on_disk_payload: true
    - name: platform_decisions
      vector_size: 768
      distance: Cosine
      on_disk_payload: false    # small; keep in RAM
    - name: platform_customers
      vector_size: 768
      distance: Cosine
      on_disk_payload: true
      # Access restricted — separate collection for isolation
```

**Embedding model**: `nomic-embed-text` via Ollama (local inference).
Fallback: OpenAI `text-embedding-3-small` (when local unavailable).

---

## Neo4j Configuration

```yaml
neo4j:
  uri: bolt://localhost:7687
  username: neo4j
  password: ${NEO4J_PASSWORD}
  database: platform
  max_connection_pool_size: 50
  connection_timeout_seconds: 30
```

**Schema**: Defined in `references/graph-schema.md` (knowledge-graph skill).
**Indexes**: Created on startup; see `references/ontology.md`.

---

## Redis Configuration

```yaml
redis:
  host: localhost
  port: 6379
  db: 0
  max_connections: 20
  ttl_seconds:
    embedding_cache: 3600       # 1 hour for computed embeddings
    query_cache: 300            # 5 minutes for query results
    hot_context: 86400          # 24 hours for workflow context packets
```

Cache keying:
- Embedding: `emb:<model>:<sha256(text)[:16]>`
- Query result: `search:<index>:<sha256(query)[:16]>:<top_k>`

---

## Routing Logic

```
Incoming query
      │
      ├── Is it a graph traversal? (decision history, skill deps, risk chains)
      │     YES → Neo4j graph query
      │     NO  → Continue
      │
      ├── Is result in Redis cache? (recent embedding or query result)
      │     YES → Return cached result (skip vector search)
      │     NO  → Continue
      │
      ├── Retrieve: Qdrant (vector) + BM25 (keyword) in parallel
      │
      └── Merge via RRF → Re-rank → Cache result in Redis → Return
```

---

## Embedding Pipeline

```python
def embed(text: str, model: str = "nomic-embed-text") -> list[float]:
    cache_key = f"emb:{model}:{sha256(text)[:16]}"
    # Check Redis cache
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    # Generate embedding via Ollama
    response = ollama.embeddings(model=model, prompt=text)
    embedding = response["embedding"]
    # Cache for 1 hour
    redis.setex(cache_key, 3600, json.dumps(embedding))
    return embedding
```

---

## Failure Modes and Fallbacks

| Failure | Fallback |
|---|---|
| Qdrant unavailable | BM25-only search (keyword); log degraded mode |
| Neo4j unavailable | Skip graph queries; return empty graph results |
| Redis unavailable | Skip caching; continue without cache |
| Ollama embedding unavailable | Fallback to OpenAI text-embedding-3-small |
| OpenAI embedding unavailable | BM25-only search; log critical alert |

All failures are logged to telemetry with the backend, error type, and fallback action taken.