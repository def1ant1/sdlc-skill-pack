# Cluster Topology Reference

## Overview

This document defines the topology schema for GPU compute clusters in the Autonomous OS
infrastructure. All placement optimization and defragmentation decisions reference this schema.

---

## Node Types

| Node Type | Role | Typical Hardware | Max Agents |
|---|---|---|---|
| primary-compute | Main inference and training workloads | DGX H100, A100 | 8 |
| secondary-compute | Overflow inference, batch processing | RTX 4090, L40 | 4 |
| coordinator | Task routing, health monitoring | CPU-only | N/A |
| edge | Local/air-gapped inference | Jetson, Mac M-series | 2 |

---

## Interconnect Specifications

### NVLink (Intra-node GPU-GPU)

| NVLink Version | Bandwidth per Link | Links per GPU | Total Bandwidth |
|---|---|---|---|
| NVLink 4.0 (H100) | 900 GB/s | 18 | 900 GB/s bidirectional |
| NVLink 3.0 (A100) | 600 GB/s | 12 | 600 GB/s bidirectional |
| NVLink 2.0 (V100) | 300 GB/s | 6 | 300 GB/s bidirectional |

**Placement rule:** Model shards with tensor-parallel communication > 50 GB/s MUST be placed
on GPUs connected via NVLink, not PCIe.

### PCIe (Intra-node GPU-CPU)

| PCIe Generation | Bandwidth (x16) | Typical Use |
|---|---|---|
| PCIe 5.0 | 64 GB/s | DGX Spark local bus |
| PCIe 4.0 | 32 GB/s | Standard server GPU |
| PCIe 3.0 | 16 GB/s | Legacy nodes |

### InfiniBand (Inter-node)

| IB Generation | Bandwidth | Latency | Use |
|---|---|---|---|
| HDR (200Gb) | 25 GB/s | 0.6 µs | DGX cluster backbone |
| HDR100 (100Gb) | 12.5 GB/s | 0.7 µs | Secondary cluster links |
| EDR (100Gb) | 12.5 GB/s | 1.0 µs | Storage/archive |

---

## Topology Graph Node Schema

```yaml
node:
  node_id: "NODE-DGX-001"
  node_type: primary-compute
  hostname: dgx-001.cluster.local
  location:
    datacenter: "DC-West"
    rack: "R03"
    unit: "U12"
  gpus:
    - gpu_id: "GPU-001-0"
      model: "H100 SXM5"
      vram_gb: 80
      nvlink_peers: ["GPU-001-1", "GPU-001-2", "GPU-001-3"]
      pcie_gen: 5
    - gpu_id: "GPU-001-1"
      model: "H100 SXM5"
      vram_gb: 80
      nvlink_peers: ["GPU-001-0", "GPU-001-2", "GPU-001-3"]
      pcie_gen: 5
  cpu_cores: 144
  ram_gb: 2048
  interconnect:
    type: InfiniBand-HDR
    bandwidth_gbps: 200
    peer_nodes: ["NODE-DGX-002", "NODE-DGX-003"]
  health:
    status: healthy  # healthy | degraded | failed
    last_heartbeat: "2026-05-07T14:23:00Z"
    thermal:
      gpu_temp_c: [72, 71, 73, 70]
      throttle_threshold_c: 85
      emergency_threshold_c: 90
```

---

## Thermal Thresholds

| Condition | GPU Temp | Action |
|---|---|---|
| Normal | < 75°C | No action |
| Warning | 75–84°C | Log and monitor; reduce batch size by 20% |
| Throttle | 85–89°C | Reduce workload to 70% capacity |
| Emergency | ≥ 90°C | Migrate workloads off node; alert operator |

---

## Bandwidth Bottleneck Detection

A bottleneck is flagged when observed throughput falls below the threshold fraction of
theoretical maximum for a sustained period:

| Link Type | Saturation Threshold | Observation Window | Action |
|---|---|---|---|
| NVLink | > 80% theoretical | 60 seconds | Consider tensor parallel redistribution |
| PCIe | > 70% theoretical | 30 seconds | Reduce model shard cross-bus traffic |
| InfiniBand | > 60% theoretical | 120 seconds | Redistribute pipeline across fewer nodes |

---

## Defragmentation Trigger Criteria

Defragmentation is triggered when any of the following conditions are met:

1. VRAM fragmentation ratio > 30% on any node (fragmented free / total free > 0.3)
2. Largest contiguous VRAM block < 50% of total free VRAM
3. Model requiring N×8 GB VRAM cannot be placed despite sufficient aggregate free VRAM
4. KV cache eviction rate > 15% of requests in any 5-minute window

---

## Placement Constraint Rules

| Rule | Constraint | Priority |
|---|---|---|
| NVLink affinity | Tensor-parallel shards → same NVLink domain | HARD |
| VRAM safety margin | Max 85% VRAM utilization per GPU | HARD |
| Thermal isolation | High-power models → distributed across nodes | SOFT |
| Cost efficiency | Prefer local nodes over cloud overflow | SOFT |
| Latency locality | KV cache producer and consumer → same node | SOFT |