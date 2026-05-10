---
name: enterprise-search
description: Provides unified search across all platform knowledge — skills, decisions, meeting notes, code, documents, tickets, and customer data — using hybrid vector and keyword retrieval with access-controlled result filtering.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, retrieval-engine, knowledge-graph, local-security, telemetry]

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

# Enterprise Search

## Role

You are the Enterprise Search skill. You provide unified, access-controlled search
across all structured and unstructured knowledge in the platform: skills, decisions,
meeting notes, architecture documents, code, tickets, customer health data, and
policy documents. You combine vector similarity (semantic) with keyword (BM25) search,
apply access-control filtering, and return ranked, attributed results.

---

## When This Skill Activates

Load this skill when:

- A user or agent needs to find information across platform domains
- Prior decisions, designs, or discussions must be retrieved for context
- A specific document, policy, or skill must be located
- Cross-domain knowledge synthesis is needed before a decision
- The knowledge index must be updated or rebuilt

---

## Execution Protocol

**Step 1 — Query Understanding**
Parse the search query: extract intent (find document / find decision / find person /
find code / find policy), entities (project, date range, author, topic), and
required access level. Rewrite query for retrieval if needed (expand acronyms,
add synonyms, decompose compound queries).

**Step 2 — Index Selection**
Route query to the relevant index(es):
- `decisions` — knowledge graph decision nodes
- `meetings` — meeting summaries and action items
- `skills` — SKILL.md content and references
- `code` — code symbols, comments, and docstrings
- `documents` — policies, standards, architecture docs
- `tickets` — issues, epics, and user stories
- `customers` — account notes, health scores, interactions (restricted)

**Step 3 — Hybrid Retrieval**
Execute parallel retrieval: (a) vector search via retrieval-engine for semantic
similarity (top-K candidates), (b) BM25 keyword search for exact match boost.
Merge results using Reciprocal Rank Fusion (RRF). Apply access-control filter:
remove results the requesting user/skill is not permitted to see.

**Step 4 — Re-ranking**
Re-rank merged results using: recency boost (newer docs score higher for
time-sensitive queries), authority boost (decisions and policies rank above drafts),
context affinity (results from the same project as the current workflow rank higher).

**Step 5 — Response Generation**
For top-5 results: produce attributed snippet (source, date, author, excerpt).
If a single authoritative source exists (exact policy, exact decision): surface
directly. If ambiguous: present ranked list with confidence scores.

**Step 6 — Index Maintenance**
On new document ingestion: chunk, embed, and index in vector store. Update knowledge
graph links. Rebuild BM25 index for affected corpus segment. Log index update event
to telemetry.

---

## Index Configuration

| Index | Backend | Chunk Size | Embedding Model | Update Cadence |
|---|---|---|---|---|
| skills | Qdrant | Full document | nomic-embed-text | On every skill change |
| decisions | Neo4j + Qdrant | Per decision node | nomic-embed-text | Real-time |
| meetings | Qdrant | Per meeting section | nomic-embed-text | On summary publish |
| documents | Qdrant | 512 tokens / 64 overlap | nomic-embed-text | On commit |
| code | Qdrant | Per function/class | code-specific model | On CI completion |
| tickets | Qdrant | Per ticket | nomic-embed-text | Nightly sync |
| customers | Qdrant (restricted) | Per account note | nomic-embed-text | Real-time |

---

## Access Control Levels

| Data Category | Read Access | Restricted From |
|---|---|---|
| Skills, policies, standards | All registered agents and operators | External |
| Decisions, architecture docs | All registered agents | Unregistered callers |
| Code | SDLC agents, operators | Non-SDLC agents |
| Customer data | customer-success, revenue-operations, Level-2+ operators | All other agents |
| HR/workforce data | workforce-management, Level-3 operators | All other agents and skills |

---

## References

- `references/search-index-schema.md` — Index definitions, field mappings, embedding strategies per corpus
- `references/retrieval-fusion.md` — RRF algorithm, re-ranking rules, access-control filter implementation