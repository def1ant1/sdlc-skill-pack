---
name: ray-runtime
description: Manages Ray cluster and KubeRay operator for distributed workload scheduling, training, serving, and data processing across the enterprise compute fabric.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['cluster-management', 'distributed-agent-runtime', 'event-bus']

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

Distributed compute fabric manager for the Enterprise OS. Deploys and operates Ray clusters
via the KubeRay operator, schedules distributed workloads (training, batch inference, data
processing, agent coordination), and exposes a unified task submission API so callers do not
need to know Ray's internal topology.

## Activation Triggers

- A training job is submitted via `distributed-training-orchestration`
- `ray-serve-management` requests a Ray Serve deployment or update
- A batch inference job exceeds single-node capacity and requires Ray distribution
- Ray cluster health check fails (triggers recovery or scale-out)
- `cluster-management` detects a node failure in the Ray cluster
- Operator requests a cluster resize or configuration change

## Execution Protocol

1. **Cluster management**: Operate the KubeRay `RayCluster` CRD. Maintain head node and
   worker node pools. Scale worker nodes via the autoscaler based on pending task queue depth.

2. **Job submission**: Accept job definitions with:
   - `job_type`: `training` | `batch_inference` | `data_processing` | `agent_task`
   - `entrypoint`: Python script or Ray remote function reference
   - `resource_requirements`: `{"num_cpus": N, "num_gpus": N, "memory_gb": N}` per task
   - `priority`: `high` | `normal` | `low`
   Submit to Ray job API. Return job_id for tracking.

3. **Resource scheduling**: Ray's distributed scheduler allocates tasks to available workers.
   Monitor queue depth and pending resource requests. Trigger autoscaler when queue depth
   exceeds `max_queue_depth_before_scale` threshold for > 2 minutes.

4. **Health monitoring**: Poll Ray head node `/api/cluster_info` every 30 seconds.
   Check: node count, total resources, pending tasks, failed workers.
   Trigger node replacement via `cluster-management` on worker failures.

5. **Result collection**: Stream job logs to `telemetry`. On job completion, collect metrics:
   total_duration, node_count_used, gpu_hours, peak_memory. Emit `ray.job.completed` event.

## Output Format

```yaml
ray_job:
  job_id: "raysubmit_xxxxx"
  job_type: training
  status: pending | running | succeeded | failed
  submitted_at: "2026-05-07T10:00:00Z"
  completed_at: null
  resources_used:
    gpu_hours: 0.0
    cpu_hours: 0.0
    peak_memory_gb: 0
  result_ref: null
  logs_ref: "telemetry/ray-job-xxxxx"
```

## References

- `references/` — RayCluster CRD spec, autoscaling policy, resource request schema
