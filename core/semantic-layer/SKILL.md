---
name: semantic-layer
description: Maintains the enterprise knowledge graph with 30+ entity types, resolves entity identity across systems, performs ontological reasoning, and provides temporal graph analysis for the Autonomous OS.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: data
  maturity: alpha
  dependencies: [data-fabric, knowledge-graph, telemetry]

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

Enterprise ontology and semantic reasoning engine for the Autonomous OS. Maintains the
authoritative knowledge graph containing all enterprise entities and their relationships,
resolves entity identity across heterogeneous systems, performs semantic and temporal
reasoning, and provides a unified semantic query interface for all skills and agents.

## Activation Triggers

- Entity creation or update event from any connected data system
- Skill requests a semantic query or entity resolution
- Lineage-analysis or causal-tracing requests graph traversal
- Scheduled ontology consistency validation cycle

## Execution Protocol

1. **Ingest entity events**: Consume entity creation, update, and deletion events from
   the event-bus; validate against the enterprise ontology schema; reject invalid entities.

2. **Resolve entity identity**: For new entities, apply entity resolution rules — exact
   match on canonical identifiers, probabilistic match on attribute vectors — to find
   existing records and merge or link accordingly.

3. **Apply semantic reasoning**: Execute active inference rules (SR-001 through SR-005)
   on newly ingested entities; derive implicit relationships; detect constraint violations.

4. **Maintain temporal validity**: Track bi-temporal validity (valid_time and transaction_time)
   for all entity records; apply temporal reasoning rules (TR-001 through TR-003) for
   point-in-time queries.

5. **Serve semantic queries**: Process Cypher and SPARQL queries from skills and agents;
   enforce access control on sensitive entity types; return results with provenance metadata.

6. **Validate consistency**: Periodically validate the knowledge graph against ontology
   constraints; emit `ontology.violation` events for detected inconsistencies.

## Output Format

Query results with: entity records (including all attributes and temporal validity),
relationship edges (with type, confidence, and provenance), and consistency check summaries
with violation counts and details.

## References

- `references/enterprise-ontology.md` — 30+ entity types, 15 relationships, temporal properties, constraints
- `references/semantic-reasoning-rules.md` — 5 inference rules, 3 temporal rules, Cypher query patterns