---
name: model-placement-optimization
description: Computes and executes optimal model shard placement across GPU cluster nodes to maximize cache efficiency, minimize cross-node communication, and meet latency SLOs.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [cluster-management, network-topology-analysis, local-runtime, runtime-economics]
---

## Role

Model placement optimization specialist. Given the current cluster topology, active model
inventory, and workload demand, computes the placement configuration that maximizes KV cache
hit rates, minimizes inter-GPU communication overhead, and meets per-model latency SLOs within
available VRAM capacity.

## Activation Triggers

- New model registered requiring placement
- Cluster VRAM fragmentation exceeds 25%
- P95 inference latency exceeds SLO by >20%
- Node failure requiring workload rebalancing
- Scheduled placement optimization cycle (every 4 hours)

## Execution Protocol

1. **Inventory current placement**: Retrieve current model → GPU mapping from local-runtime;
   record VRAM usage, shard configuration, and serving metrics per placement.

2. **Collect demand signals**: Sample request rate, batch size, and queue depth per model
   to estimate relative demand weight for each model.

3. **Compute placement score**: For each candidate placement: score = (cache_hit_rate × 0.4)
   + (nvlink_efficiency × 0.3) + (vram_utilization_balance × 0.2) + (latency_estimate × 0.1).

4. **Generate migration plan**: Select highest-scoring placement that requires fewest migrations
   from current state; estimate migration downtime and cost.

5. **Validate feasibility**: Verify VRAM constraints for proposed placement; check that no model
   exceeds node VRAM capacity; ensure at least one replica of each model remains available during migration.

6. **Execute migrations**: Migrate model shards sequentially; validate P95 latency after each
   migration; roll back if latency degrades.

## Output Format

Placement plan with: current vs. proposed model-to-GPU mapping, expected improvement in cache
hit rate and latency, migration sequence with estimated downtime per step, and rollback criteria.

## References

- `references/placement-scoring-algorithm.md` — scoring formula details, VRAM capacity constraints, migration cost model