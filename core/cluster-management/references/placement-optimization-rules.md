# Placement Optimization Rules

## Overview

Rules and algorithms used by `cluster-management` and `model-placement-optimization` to
score and select optimal GPU placements for model shards.

---

## Placement Scoring Algorithm

Each candidate placement is scored 0–100. Higher scores are preferred.

```
placement_score = (
    nvlink_affinity_score   × 0.35 +
    vram_efficiency_score   × 0.25 +
    thermal_balance_score   × 0.20 +
    latency_locality_score  × 0.15 +
    cost_score              × 0.05
)
```

### Component Score Definitions

**nvlink_affinity_score (0–100)**
- 100: All shards within a single NVLink domain
- 70: All shards within same node (PCIe only)
- 30: Shards split across nodes (InfiniBand required)
- 0: Shards on nodes with > 2 hops

**vram_efficiency_score (0–100)**
- Score = 100 × (1 − fragmentation_ratio) where fragmentation_ratio = fragmented_free / total_free
- Minimum acceptable score: 40 (fragmentation_ratio ≤ 0.60)

**thermal_balance_score (0–100)**
- Score = 100 × (1 − coefficient_of_variation(gpu_temps)) across target GPUs
- Score = 0 if any target GPU is in throttle state

**latency_locality_score (0–100)**
- 100: KV cache producer and consumer on same GPU
- 75: Same node, different GPUs
- 40: Adjacent nodes (1 IB hop)
- 0: Non-adjacent nodes (2+ IB hops)

**cost_score (0–100)**
- 100: On-premise node within normal budget period
- 50: On-premise node in constrained budget period
- 10: Cloud overflow (any provider)

---

## Migration Cost Model

Before executing a placement change, calculate the migration cost:

```
migration_cost_seconds = (
    shard_size_gb / transfer_bandwidth_gbps +
    warmup_latency_seconds
)
```

| Transfer Path | Bandwidth | Warmup |
|---|---|---|
| NVLink (same node) | 900 GB/s | 2 s |
| PCIe (same node) | 32 GB/s | 5 s |
| InfiniBand HDR (inter-node) | 25 GB/s | 15 s |
| InfiniBand EDR (inter-node) | 12 GB/s | 20 s |

**Migration is approved only if:** `expected_latency_improvement_seconds > migration_cost_seconds × 2`

---

## Migration Triggers

| Condition | Trigger | Min Score Delta Required |
|---|---|---|
| Reactive (degradation) | GPU > 85°C OR VRAM > 90% | Any improvement |
| Scheduled (optimization cycle) | Every 4 hours | Score improvement ≥ 15 points |
| Operator-requested | On demand | Any improvement |
| Post-defragmentation | After VRAM compaction | Score improvement ≥ 5 points |

---

## Rollback Criteria

A placement change is automatically rolled back if, within 10 minutes of completion:

- P95 inference latency increases by > 20% vs pre-migration baseline
- GPU utilization drops by > 15 percentage points (migration introduced overhead)
- VRAM OOM errors occur on the destination node
- Any destination GPU enters thermal throttle state

Rollback restores the previous placement from the placement registry snapshot taken
before migration began.

---

## Anti-patterns to Avoid

| Anti-pattern | Description | Detection |
|---|---|---|
| Tensor-parallel split | TP shards on non-NVLink-connected GPUs | placement_score < 50 |
| VRAM overcommit | Sum of model sizes > 85% of available VRAM | vram_utilization > 0.85 |
| Hot-node concentration | > 3 high-power models on same node | avg_gpu_temp > 78°C |
| Cloud dependency | All serving capacity on cloud overflow | cost_score average < 20 |