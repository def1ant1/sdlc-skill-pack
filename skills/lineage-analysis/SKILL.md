---
name: lineage-analysis
description: Traverses the data lineage graph to trace upstream data provenance and downstream impact for any dataset or field, supporting impact analysis, audit, and root-cause investigation of data quality issues.
metadata:
  version: "1.0.0"
  category: data
  owner: data
  maturity: alpha
  dependencies: [data-fabric, semantic-layer, telemetry]

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

Data lineage traversal engine for the data fabric. Navigates the lineage graph in both
directions — upstream to identify provenance and data sources, downstream to identify
all consumers and derivative datasets — enabling complete impact analysis before changes
and root-cause attribution of data quality issues.

## Activation Triggers

- Schema-evolution requests downstream impact analysis before a breaking change
- Data quality incident requires upstream provenance investigation
- Compliance audit requires full data origin documentation for a regulated dataset
- Operator queries the lineage of a specific table, field, or pipeline output

## Execution Protocol

1. **Resolve lineage target**: Look up the dataset, table, or field in the semantic layer
   entity registry; retrieve its lineage graph node ID.

2. **Traverse upstream**: Walk the lineage graph from the target node to all source nodes;
   collect all transformation steps, intermediate datasets, and original data sources
   with their ingestion timestamps.

3. **Traverse downstream**: Walk the lineage graph from the target to all derived datasets,
   views, reports, and ML features; record all transformation logic and consumer identifiers.

4. **Compute lineage metrics**: Calculate lineage depth (hops from source), fan-out (downstream
   consumers), critical path (longest downstream chain), and data freshness propagation lag.

5. **Flag lineage risks**: Identify single-source dependencies (no redundancy), undocumented
   transformations (gap in lineage graph), and cross-boundary flows (data crossing residency zones).

6. **Render lineage report**: Produce a structured lineage document with upstream provenance
   map, downstream impact map, metrics, and risk flags.

## Output Format

Lineage report with: `target_id`, `upstream_sources` (list with transformation steps),
`downstream_consumers` (list with dependency depth), `lineage_depth`, `fan_out`,
`freshness_lag_max` (minutes), `risks` (list), and lineage graph export (DOT/Mermaid).

## References

- `references/lineage-graph-schema.md` — graph node/edge format, traversal algorithms, freshness propagation model