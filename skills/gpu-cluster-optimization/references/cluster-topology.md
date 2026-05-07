# GPU Cluster Topology Reference

## Cluster Node Types

| Node Type | GPU Count | GPU Model | GPU RAM | Interconnect | NVLink Bandwidth | Use For |
|---|---|---|---|---|---|---|
| Large training node | 8 | H100 SXM5 | 80GB × 8 | NVLink 4.0 | 900 GB/s bidirectional | Large model training |
| Standard training node | 8 | A100 SXM4 | 80GB × 8 | NVLink 3.0 | 600 GB/s bidirectional | Standard training |
| Inference node | 4 | H100 PCIe | 80GB × 4 | PCIe 5.0 | 128 GB/s | Batch inference |
| Edge inference node | 2 | L40S | 48GB × 2 | PCIe 4.0 | 64 GB/s | Low-latency inference |
| Development node | 1 | A10G | 24GB × 1 | PCIe 4.0 | N/A | Development, debugging |

---

## Inter-Node Network Topology

```
Cluster network fabric (3-tier fat-tree):
  - Access layer: 25 GbE per node (CPU-to-ToR switch)
  - Aggregation: 100 GbE InfiniBand (ToR-to-spine)
  - Core: 400 GbE InfiniBand (spine-to-spine)

GPU-to-GPU communication:
  - Intra-node (same physical host): NVLink (see table above)
  - Inter-node (different hosts): RDMA over InfiniBand
    latency: < 2 microseconds
    bandwidth: 200 Gb/s per link (HDR InfiniBand)
  - Cross-rack: 100 Gb/s aggregated

Rail optimization:
  - Each NVLink domain = 1 NVLink switch connecting up to 8 GPUs
  - Rail-optimized topology: NIC channels routed to same rail as GPU peers
  - Reduces all-reduce latency by 40% vs. non-optimized topology
```

---

## Thermal and Power Constraints

```yaml
thermal_constraints:
  max_gpu_temperature_celsius: 85
  throttle_temperature_celsius: 80
  warning_temperature_celsius: 75

  data_center_thermal_design:
    cooling_type: "rear-door heat exchanger + in-row cooling"
    max_rack_power_kw: 40.0
    target_pue: 1.35  # Power Usage Effectiveness

power_constraints:
  h100_tdp_watts: 700
  a100_tdp_watts: 400
  l40s_tdp_watts: 350
  a10g_tdp_watts: 150

  power_per_node:
    large_training_node: "8 × 700W GPU + 300W CPU/DRAM = ~6000W total"
    standard_training_node: "8 × 400W GPU + 300W = ~3500W total"
    inference_node: "4 × 700W GPU + 200W = ~3000W total"
```

---

## Placement Constraint Rules

### Rule PC-001: Training Job Affinity

```
Large model training (> 70B parameters) REQUIRES:
  - All GPU nodes within same NVLink domain
  - InfiniBand rail alignment
  - < 3 hops between any two nodes

Constraint: node_count ≤ max_nodes_per_nVLink_domain[gpu_model]
  H100 NVLink domain: 8 nodes (64 GPUs) via NVLink Switch
  A100 NVLink domain: 8 nodes (64 GPUs) via NVSwitch
```

### Rule PC-002: Inference Job Distribution

```
Inference workloads SHOULD be distributed across racks for fault tolerance:
  - At least 2 racks per inference deployment
  - No single rack holds > 60% of inference capacity for a service
  - Exception: ultra-low latency requirements (< 5ms) may colocate all replicas
```

### Rule PC-003: Thermal Locality

```
Avoid colocating multiple high-TDP jobs on same cooling zone:
  total_power_per_cooling_zone = Σ(active_gpu_count × tdp_per_gpu)
  ASSERT total_power_per_cooling_zone ≤ cooling_zone_capacity × 0.85
```

### Rule PC-004: NUMA Alignment

```
Within each node, align GPU to CPU NUMA domain:
  numa_assignment:
    GPU 0-3: NUMA node 0 (CPU socket 0 + memory bank 0)
    GPU 4-7: NUMA node 1 (CPU socket 1 + memory bank 1)

  Violation causes: PCIe bottleneck, 20-30% throughput reduction
  Detection: nvidia-smi topo -m shows non-preferred paths
```

---

## Cluster Health Monitoring

```yaml
health_check_protocol:
  frequency: "every 60 seconds"

  checks:
    gpu_utilization:
      metric: "nvidia_gpu_utilization_pct"
      warning: "> 95% for > 10 minutes (possible OOM risk)"
      critical: "= 0% during active job (possible GPU hang)"

    gpu_memory:
      metric: "nvidia_gpu_memory_used_bytes"
      warning: "> 90% of total"
      critical: "> 98% of total"

    gpu_temperature:
      metric: "nvidia_gpu_temperature_celsius"
      warning: "> 75°C"
      critical: "> 80°C (throttling imminent)"

    infiniband_errors:
      metric: "ib_port_rcv_errors + ib_port_xmit_discards"
      warning: "error_rate > 1 per minute"
      critical: "error_rate > 100 per minute (link degradation)"

    nvlink_errors:
      metric: "nvlink_error_count"
      warning: "any nvlink errors"
      critical: "nvlink_error_count > 10 in 5 minutes"

  auto_remediation:
    gpu_hang: "nvidia-smi --gpu-reset then restart job on replacement node"
    high_temperature: "reduce job batch size by 20%; alert operator"
    ib_link_degradation: "migrate affected jobs to healthy nodes"
```