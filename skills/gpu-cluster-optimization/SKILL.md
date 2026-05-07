---
name: gpu-cluster-optimization
description: Analyzes GPU cluster topology, detects VRAM fragmentation and thermal hotspots, and executes topology-aware model placement and VRAM defragmentation to maximize inference throughput.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [cluster-management, network-topology-analysis, telemetry]
---

## Role

GPU cluster efficiency optimizer for the AI infrastructure runtime. Continuously analyzes
cluster topology, VRAM utilization, thermal distribution, and interconnect saturation to
identify optimization opportunities and execute placement improvements that maximize
effective throughput per watt.

## Activation Triggers

- Cluster-management detects VRAM utilization above 85% across a node pool
- Inference-batching-optimization reports throughput degradation from VRAM fragmentation
- Scheduled optimization cycle (default: every 4 hours) triggers routine analysis
- Operator requests on-demand cluster optimization

## Execution Protocol

1. **Collect cluster telemetry**: Gather current VRAM utilization, model shard locations,
   NVLink/PCIe bandwidth utilization, GPU temperature, and power draw per device.

2. **Detect inefficiencies**: Identify fragmentation (VRAM split across non-adjacent GPUs),
   thermal hotspots (GPU temp > 85°C), bandwidth bottlenecks (PCIe saturation), and
   load imbalance (coefficient of variation > 0.3 across GPUs).

3. **Compute optimal placement**: Run topology-aware placement algorithm — maximize NVLink
   bandwidth for multi-GPU shards; minimize PCIe hops for high-communication model pairs;
   balance thermal load across nodes.

4. **Plan migration sequence**: Order shard migrations to minimize service interruption;
   use checkpoint-management to preserve active inference state; schedule migrations
   during low-traffic windows when possible.

5. **Execute defragmentation**: Migrate model shards to optimal locations; verify VRAM
   integrity after each migration; update placement registry.

6. **Measure improvement**: Compute before/after throughput, VRAM utilization efficiency,
   and thermal distribution metrics; emit optimization report.

## Output Format

Optimization report with: `cluster_id`, `inefficiencies_detected` (list), `migrations_executed`
(count and details), `vram_efficiency_improvement` (%), `throughput_improvement` (tokens/s),
and updated `placement_map`.

## References

- `references/cluster-topology.md` — NVLink/PCIe topology mapping, thermal thresholds, placement algorithm