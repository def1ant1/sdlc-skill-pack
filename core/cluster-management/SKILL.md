---
name: cluster-management
description: Autonomous infrastructure intelligence layer that monitors GPU cluster health, optimizes model placement, manages inference batching, and coordinates autonomous capacity scaling.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [local-runtime, runtime-economics, telemetry, lora-lifecycle]
---

## Role

Intelligent orchestrator for sovereign AI compute infrastructure. Monitors GPU cluster topology
and utilization, optimizes model placement for cache efficiency and latency, manages inference
batching windows, and triggers autonomous scaling decisions within operator-approved bounds.

## Activation Triggers

- GPU utilization above 90% or below 60% sustained for >5 minutes
- Model placement optimization cycle triggered (every 15 minutes)
- Inference latency P95 exceeds SLO threshold
- Node failure or capacity change detected
- Scheduled capacity planning review

## Execution Protocol

1. **Collect cluster metrics**: Sample GPU SM utilization, VRAM usage, NVLink bandwidth,
   PCIe saturation, and inference queue depth per node every 15 seconds.

2. **Analyze topology**: Map current model placements against NVLink interconnect topology;
   identify cross-node communication overhead and cache fragmentation.

3. **Detect inefficiencies**: Flag nodes below 60% GPU utilization, VRAM fragmentation >25%,
   or P95 latency degradation >20% versus baseline.

4. **Plan rebalancing**: Generate placement proposals using model-placement-optimization;
   score each proposal by expected latency improvement vs. migration cost.

5. **Execute optimization**: Execute approved rebalancing: migrate model shards, adjust batch
   sizes, rebalance inference queues; apply changes incrementally.

6. **Validate outcome**: Measure P95 latency and GPU utilization for 5 minutes post-change;
   roll back to previous configuration if any metric degrades.

## Output Format

Cluster health report with: per-node utilization, optimization actions taken, before/after
latency metrics, VRAM allocation map, and next scheduled optimization window.

## References

- `references/cluster-topology.md` — DGX Spark topology, NVLink bandwidth map, VRAM capacity per node
- `references/placement-optimization-rules.md` — placement scoring algorithm, migration cost model, rollback thresholds