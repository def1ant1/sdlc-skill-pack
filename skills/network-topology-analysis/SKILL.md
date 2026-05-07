---
name: network-topology-analysis
description: Analyzes GPU cluster and datacenter network topology to identify bandwidth bottlenecks, optimize interconnect utilization, and inform model sharding and placement decisions.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [cluster-management, local-runtime, telemetry]
---

## Role

Network topology intelligence specialist for sovereign AI infrastructure. Builds and maintains
a live topology map of NVLink, PCIe, and Ethernet interconnects across the DGX Spark cluster,
identifies bandwidth saturation points, and produces topology-aware placement recommendations
that minimize cross-node data movement.

## Activation Triggers

- Cluster topology change detected (node added/removed/reconfigured)
- Inference latency degradation traced to network bottleneck
- Model placement optimization cycle requesting topology data
- Distributed inference job requiring topology-aware sharding plan

## Execution Protocol

1. **Discover topology**: Query NCCL topology detection and OS device APIs to enumerate
   all GPUs, NVLink connections, PCIe bridges, and network interfaces.

2. **Build topology graph**: Construct weighted graph where nodes are GPUs/CPUs and edges
   are interconnects with bandwidth (GB/s) and latency (μs) as edge weights.

3. **Measure current utilization**: Sample NVLink and PCIe utilization counters; overlay
   current bandwidth usage on topology graph.

4. **Identify bottlenecks**: Find edges with utilization > 70% sustained; rank by impact
   on current inference workloads.

5. **Generate placement recommendations**: Compute optimal GPU affinity groups for model
   sharding based on NVLink bandwidth; minimize cross-NVLink-domain traffic.

6. **Produce topology report**: Topology diagram, bottleneck list, affinity groups,
   bandwidth utilization heatmap, and placement recommendations for cluster-management.

## Output Format

Topology report containing: GPU affinity groups, bottleneck rankings, bandwidth utilization
per link, recommended tensor-parallel groupings, and suggested workload migrations.

## References

- `references/topology-graph-schema.md` — topology graph node/edge format, bandwidth measurement methodology