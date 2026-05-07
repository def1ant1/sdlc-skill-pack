# Placement Scoring Algorithm Reference

## Placement Score Computation

Each candidate (node, rack, or cluster) receives a composite placement score:

```
placement_score(candidate) = (
    capability_match_score × 0.35 +
    locality_score × 0.25 +
    resource_fit_score × 0.20 +
    thermal_headroom_score × 0.10 +
    network_topology_score × 0.10
)
```

---

## Score Component Definitions

### 1. Capability Match Score (0–100)

```python
def capability_match_score(job, candidate_node):
    # GPU tier match
    if job.required_gpu_tier > candidate_node.gpu_tier:
        return 0  # Hard block — cannot run

    tier_bonus = 15 if candidate_node.gpu_tier == job.required_gpu_tier else 0
    # Penalty for over-provisioning (waste)
    tier_over_provision_penalty = max(0, (candidate_node.gpu_tier - job.required_gpu_tier) * 5)

    # Memory fit (hard constraint)
    if candidate_node.gpu_memory_gb < job.required_gpu_memory_gb:
        return 0  # Hard block — insufficient memory

    memory_fit = min(100, (candidate_node.gpu_memory_gb / job.required_gpu_memory_gb) * 80)
    # Penalize excessive over-allocation
    memory_overalloc_penalty = max(0, (candidate_node.gpu_memory_gb / job.required_gpu_memory_gb - 1.5) * 10)

    return min(100, memory_fit + tier_bonus - tier_over_provision_penalty - memory_overalloc_penalty)
```

### 2. Locality Score (0–100)

```python
def locality_score(job, candidate_node):
    # For multi-node jobs: measure NVLink/InfiniBand topology proximity
    if job.node_count == 1:
        return 100  # Single-node: locality not relevant

    # For distributed jobs: prefer nodes within same NVLink domain
    same_nvlink_domain = all(
        node in candidate_node.nvlink_domain
        for node in job.assigned_nodes
    )
    if same_nvlink_domain:
        return 100

    # Penalize by hop count to furthest assigned node
    max_hops = max(topology.hop_count(candidate_node, n) for n in job.assigned_nodes)
    locality_score = max(0, 100 - max_hops * 20)
    return locality_score
```

### 3. Resource Fit Score (0–100)

```python
def resource_fit_score(job, candidate_node):
    # CPU utilization fit
    cpu_available = candidate_node.cpu_cores_total × (1 - candidate_node.cpu_utilization)
    if cpu_available < job.required_cpu_cores:
        return 0  # Hard block

    # Memory fit
    mem_available_gb = candidate_node.memory_gb × (1 - candidate_node.memory_utilization)
    if mem_available_gb < job.required_memory_gb:
        return 0  # Hard block

    # Score: maximize fit without over-allocation
    cpu_fit = min(1.0, cpu_available / job.required_cpu_cores)
    mem_fit = min(1.0, mem_available_gb / job.required_memory_gb)

    # Bin-packing score: reward nodes that use remaining capacity efficiently
    packing_score = 1 - abs(1.0 - (cpu_fit + mem_fit) / 2)

    return packing_score * 100
```

### 4. Thermal Headroom Score (0–100)

```python
def thermal_headroom_score(candidate_node):
    current_temp = candidate_node.gpu_temperature_celsius
    throttle_temp = 80  # From cluster topology

    if current_temp >= throttle_temp:
        return 0  # At or above throttle: do not schedule here

    headroom_fraction = (throttle_temp - current_temp) / throttle_temp
    return min(100, headroom_fraction * 100)
```

### 5. Network Topology Score (0–100)

```python
def network_topology_score(job, candidate_node):
    if not job.network_intensive:
        return 75  # Neutral for non-network-bound jobs

    # For all-reduce heavy jobs (distributed training):
    same_rail = is_rail_aligned(candidate_node, job.assigned_nodes)
    same_rack = all(node.rack == candidate_node.rack for node in job.assigned_nodes)
    same_pod = all(node.pod == candidate_node.pod for node in job.assigned_nodes)

    if same_rail: return 100
    if same_rack: return 80
    if same_pod: return 60
    return 30  # Cross-pod: high latency
```

---

## Scheduling Algorithm

```python
def schedule_job(job, cluster):
    # Step 1: Filter candidates (hard constraints)
    candidates = [
        node for node in cluster.nodes
        if node.is_healthy
        and capability_match_score(job, node) > 0
        and resource_fit_score(job, node) > 0
    ]

    if not candidates:
        return JobResult(status="QUEUE_PENDING", reason="No suitable nodes available")

    # Step 2: Score candidates
    scored = [
        (node, placement_score(job, node, candidates))
        for node in candidates
    ]
    scored.sort(key=lambda x: -x[1])

    # Step 3: Apply anti-affinity rules
    if job.anti_affinity_groups:
        scored = apply_anti_affinity(scored, job.anti_affinity_groups)

    # Step 4: Select top-scoring candidate
    selected_node, score = scored[0]

    if score < JOB_MINIMUM_PLACEMENT_SCORE:
        return JobResult(status="QUEUE_PENDING", reason=f"Best score {score} below minimum")

    # Step 5: Reserve resources
    cluster.reserve(selected_node, job)
    return JobResult(status="SCHEDULED", node=selected_node, score=score)
```

---

## Placement Decision Log

```yaml
placement_decision:
  decision_id: "PLC-20260507-001"
  job_id: "JOB-TRAINING-042"
  job_type: "model_training"
  required_gpus: 32
  required_gpu_memory_gb: 80
  node_count: 4

  candidates_evaluated: 24
  candidates_eliminated:
    - reason: "Insufficient GPU memory (< 80GB)"
      count: 8
    - reason: "CPU overcommit"
      count: 3
    - reason: "Thermal headroom = 0 (throttling)"
      count: 1

  scored_candidates:
    - node_ids: ["gpu-node-07", "gpu-node-08", "gpu-node-09", "gpu-node-10"]
      capability_match: 95
      locality: 100  # Same NVLink domain
      resource_fit: 88
      thermal_headroom: 82
      network_topology: 100  # Same rail
      composite_score: 93.5

  selected_nodes: ["gpu-node-07", "gpu-node-08", "gpu-node-09", "gpu-node-10"]
  placement_score: 93.5
  estimated_training_time_hours: 4.2
```