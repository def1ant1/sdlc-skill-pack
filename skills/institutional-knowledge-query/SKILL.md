---
name: institutional-knowledge-query
description: Queries organizational precedents, similar past decisions, and failure pattern libraries from the Enterprise OS knowledge graph.
metadata:
  version: "0.1.0"
  category: knowledge
  owner: platform
  maturity: draft
  dependencies: ['world-model', 'enterprise-search']

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

## Role

Retrieval interface for the organization's accumulated institutional knowledge. Answers
questions about past decisions, applicable precedents, known failure patterns, and best
practices by querying the knowledge graph and semantic memory stores. Enables agents and
skills to benefit from organizational experience before taking action.

## Activation Triggers

- An agent or skill needs to check if a similar situation has been handled before
- A decision-maker requests relevant precedents before making a significant choice
- `research-agent` identifies a knowledge gap that should be checked against internal history
- A workflow encounters an anomaly and queries for prior handling of similar anomalies
- `lessons-learned-extraction` needs to compare a new lesson against existing knowledge

## Execution Protocol

1. **Query parsing**: Accept a natural-language or structured query:
   - `query_type`: `precedent` | `failure_pattern` | `best_practice` | `decision_history`
   - `context`: description of the current situation
   - `domain`: optional domain filter (engineering, finance, compliance, etc.)
   - `min_confidence`: minimum lesson confidence to include in results (default: 2)

2. **Semantic search**: Embed the query context. Perform k-NN search (k=10) over the
   semantic memory store filtered by `query_type` and `domain`. Return matches above
   a similarity threshold (default: 0.75).

3. **Precedent ranking**: Rank results by:
   - Semantic similarity to the query context (weight: 0.50)
   - Lesson confidence score (weight: 0.30)
   - Recency (weight: 0.20) — recent precedents more relevant

4. **Gap identification**: If no results above threshold are found, flag as a `knowledge_gap`.
   Create a research task for `research-agent` to investigate externally.

5. **Return**: Return the top-5 ranked precedents/patterns with their context, lesson,
   confidence, and the originating execution reference for drill-down.

## Output Format

```yaml
knowledge_query:
  query_id: "KQ-2026-xxxxx"
  query_type: failure_pattern
  results:
    - lesson: "..."
      context: "..."
      confidence: 4
      similarity: 0.87
      source_ref: "workflow-run-2026-xxxxx"
  knowledge_gap: false
  research_task_created: false
```

## Quality Gates

- Must return results within 500ms (semantic search must be pre-indexed)
- Knowledge gaps must always be flagged — do not return empty results silently

## References

- `references/` — Query API schema, similarity threshold tuning, gap escalation policy
