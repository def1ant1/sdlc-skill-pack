---
name: master-data-management
description: Maintains canonical enterprise entity records through deduplication, survivorship rules, and golden record management for customers, vendors, employees, and products.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [data-fabric, knowledge-graph, semantic-layer, enterprise-search]

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

Canonical truth authority for enterprise entities. Resolves duplicate entity records across
sources, applies survivorship rules to determine authoritative attribute values, maintains
golden records as single sources of truth, and propagates updates to all downstream systems
via the event-bus.

## Activation Triggers

- New entity record ingested from any connected source
- Potential duplicate detected by fuzzy matching
- Golden record update triggered by source record change
- Customer 360 view requested
- Entity merge or split event initiated by operator

## Execution Protocol

1. **Ingest entity record**: Normalize incoming record to canonical schema; assign provisional
   entity-id; extract matching attributes (name, email, address, identifiers).

2. **Match against existing records**: Run fuzzy matching on identifying attributes; compute
   match confidence score for each candidate match; cluster records above threshold.

3. **Resolve duplicates**: For each duplicate cluster, apply survivorship rules per attribute
   (most recent, most complete, source priority hierarchy).

4. **Create or update golden record**: Merge surviving attributes into the canonical master
   record; write to knowledge-graph as a canonical entity node.

5. **Propagate updates**: Publish golden record update to event-bus; downstream systems
   subscribed to the entity type receive normalized change events.

6. **Maintain lineage**: Record which source records contributed to each golden record
   attribute; support provenance queries for audit.

## Output Format

Golden record with: canonical entity-id, merged attributes with source provenance, match
confidence, contributing source records list, and propagation event confirmation.

## References

- `references/survivorship-rules.md` — per-attribute survivorship logic, source priority hierarchy, entity type configurations

## Integrated Skills

- `skills/entity-resolution` for duplicate clustering and identity linkage.
- `skills/golden-record-management` for canonical record lifecycle control.
- `skills/data-quality-scoring` for confidence/quality signals used in survivorship.
