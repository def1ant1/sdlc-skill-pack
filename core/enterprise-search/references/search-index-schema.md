# Search Index Schema

## Index Definitions

### Skills Index

```yaml
index: skills
backend: qdrant
collection: platform_skills
vector_dim: 768
embedding_model: nomic-embed-text
chunk_strategy: full_document
update_trigger: on SKILL.md change (git hook)
access_level: all-internal

fields:
  - name: id          # source file path
  - name: title       # skill name
  - name: category    # core | sdlc | etc.
  - name: maturity    # alpha | beta | stable
  - name: content     # full SKILL.md text
  - name: sections    # list of ## section headings
  - name: dependencies
  - name: updated_at
```

### Decisions Index

```yaml
index: decisions
backend: neo4j + qdrant
collection: platform_decisions
vector_dim: 768
embedding_model: nomic-embed-text
chunk_strategy: per_decision_node
update_trigger: real-time (on Decision node creation)
access_level: all-registered-agents

fields:
  - name: id          # DEC-YYYYMMDD-NNN
  - name: question    # decision question text
  - name: context     # context summary
  - name: selected_option
  - name: rationale
  - name: decided_at
  - name: decided_by
  - name: related_projects
  - name: confidence
```

### Meetings Index

```yaml
index: meetings
backend: qdrant
collection: platform_meetings
vector_dim: 768
embedding_model: nomic-embed-text
chunk_strategy: per_section (decisions, action_items, discussion as separate chunks)
update_trigger: on summary publication (after human review)
access_level: all-registered-agents

fields:
  - name: id          # MTG-YYYYMMDD-NNN
  - name: title
  - name: date
  - name: meeting_type
  - name: participants
  - name: decisions   # text list
  - name: action_items # text list
  - name: summary
```

### Documents Index

```yaml
index: documents
backend: qdrant
collection: platform_documents
vector_dim: 768
embedding_model: nomic-embed-text
chunk_strategy: 512 tokens / 64 overlap
update_trigger: on git commit to shared/ or docs/
access_level: all-internal

fields:
  - name: id          # file path + chunk index
  - name: source      # file path
  - name: title       # document title (first H1)
  - name: category    # standards | policies | references | schemas
  - name: content     # chunk text
  - name: chunk_index
  - name: updated_at
```

### Code Index

```yaml
index: code
backend: qdrant
collection: platform_code
vector_dim: 768
embedding_model: nomic-embed-text (or code-specific model)
chunk_strategy: per_function_or_class
update_trigger: on CI completion
access_level: sdlc-agents + operators

fields:
  - name: id          # file:function_name
  - name: source      # file path
  - name: symbol      # function or class name
  - name: content     # code text + docstring
  - name: language
  - name: updated_at
```

### Customer Index (Restricted)

```yaml
index: customers
backend: qdrant (isolated collection)
collection: platform_customers
vector_dim: 768
embedding_model: nomic-embed-text
chunk_strategy: per_account_note
update_trigger: real-time (on CRM event or health score update)
access_level: customer-success + revenue-operations + level-2-operators-only

fields:
  - name: id          # account note ID
  - name: account_id
  - name: account_name
  - name: content     # note or health event text
  - name: category    # health | support | renewal | meeting
  - name: created_at
```

---

## Field Mappings for BM25 (Keyword Index)

BM25 indexes are maintained in-memory (for small corpora) or via Elasticsearch:

| Field | BM25 Weight | Notes |
|---|---|---|
| title | 3.0× | Title matches strongly boosted |
| category | 1.0× | Exact match for filtering |
| content | 1.0× | Full text |
| sections | 2.0× | Section headings as structured terms |

---

## Re-ranking Signals

Applied after initial retrieval to improve ranking:

| Signal | Boost | Condition |
|---|---|---|
| Recency | +20% score | Document updated in last 30 days |
| Authority | +30% score | Policy or decision document (not draft) |
| Context affinity | +25% score | Same project/skill as current workflow |
| Exact title match | +50% score | Query matches document title exactly |
| Access level match | Required | Documents outside requester's access removed |