# Commerce Network Graph

`core/commerce-network-graph` defines graph primitives for supplier, reseller, and intermediary relationship intelligence.

## Scope
- Represent supplier/reseller organizations as graph nodes.
- Track historical reliability and pricing behavior as time-series signals attached to edges.
- Compute fraud/risk correlation features across shared contacts, addresses, payment routes, and incident patterns.
- Persist graph summaries and derived insights into organizational memory primitives.

## Organizational memory integration
Each graph update emits memory primitives:
- `memory.fact`: canonical supplier/relation facts (node/edge identity, confidence, source lineage).
- `memory.timeseries`: reliability and price trajectories by supplier and product class.
- `memory.signal`: derived fraud/risk correlation indicators with feature attributions.
- `memory.snapshot`: periodic graph-state snapshots for audit and replay.

## Core data model
- **Node**: organization profile (supplier, reseller, broker, marketplace actor).
- **Edge**: commercial relationship (contracted, inferred, transactional, shared-control).
- **Signal**: reliability, pricing, fraud/risk feature vectors, each with timestamps and provenance.
- **Correlation**: scored relationship between fraud/risk events and entities/paths in the graph.

See `references/network-graph-memory-primitives.md` for signal semantics and retention guidance.
