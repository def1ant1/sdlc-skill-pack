# Ray Runtime — Cluster Configuration & Task Routing

## Ray Cluster Configuration Schema

```yaml
ray_cluster:
  cluster_name: "apotheon-ray-prod"
  ray_version: "2.9.x"
  namespace: "apotheon-ray"

  head_node:
    instance_type: "n2-standard-8"   # 8 vCPU, 32GB RAM
    resources:
      CPU: 8
      memory: 30_000_000_000         # 30 GB (leave headroom)
    dashboard_port: 8265
    redis_port: 6379

  worker_pools:
    - pool_name: "cpu-workers"
      min_replicas: 2
      max_replicas: 20
      instance_type: "n2-standard-4"
      resources:
        CPU: 4
        memory: 14_000_000_000
      autoscaling_metric: pending_tasks
      scale_up_threshold: 5          # Scale when >5 tasks queued
      scale_down_delay_seconds: 120

    - pool_name: "gpu-workers"
      min_replicas: 0
      max_replicas: 8
      instance_type: "a2-highgpu-1g"
      resources:
        CPU: 12
        memory: 85_000_000_000
        GPU: 1
      autoscaling_metric: pending_gpu_tasks
      scale_up_threshold: 1
      scale_down_delay_seconds: 300  # Keep alive longer (GPU warm-up cost)

  object_store:
    plasma_store_memory_bytes: 10_000_000_000   # 10 GB per node

  logging:
    log_level: INFO
    export_to: "gs://apotheon-ray-logs/"
    retention_days: 14
```

---

## Task Routing Policy

```python
# Ray remote task definitions with resource requirements

import ray

@ray.remote(num_cpus=1, num_gpus=0, max_retries=3)
def cpu_inference_task(prompt: str, model_config: dict) -> dict:
    """Light inference — routes to cpu-workers pool."""
    ...

@ray.remote(num_cpus=2, num_gpus=1, max_retries=2)
def gpu_inference_task(prompt: str, model_config: dict) -> dict:
    """Heavy inference — routes to gpu-workers pool."""
    ...

@ray.remote(num_cpus=1, memory=4_000_000_000, max_retries=5)
def document_processing_task(doc_uri: str) -> dict:
    """Memory-intensive doc processing."""
    ...
```

---

## Distributed Training Job Schema

```yaml
training_job:
  job_id: "TRAIN-2026-xxxxx"
  job_type: fine_tune | rlhf | reward_model | adapter

  model:
    base_model_id: "meta-llama/Llama-3.1-8B"
    adapter_type: lora | full_finetune
    lora_rank: 16
    lora_alpha: 32

  data:
    train_uri: "gs://apotheon-datasets/train-v3.jsonl"
    eval_uri: "gs://apotheon-datasets/eval-v3.jsonl"
    format: alpaca | sharegpt | raw_completion

  compute:
    num_workers: 4
    gpus_per_worker: 1
    framework: deepspeed | fsdp
    deepspeed_stage: 2

  hyperparameters:
    learning_rate: 2.0e-4
    num_epochs: 3
    batch_size_per_gpu: 4
    gradient_accumulation_steps: 8
    warmup_ratio: 0.03
    lr_scheduler: cosine

  checkpointing:
    save_every_n_steps: 500
    output_uri: "gs://apotheon-checkpoints/"
    keep_last_n: 3

  evaluation:
    eval_every_n_steps: 100
    metrics: [loss, perplexity, task_accuracy]
```

---

## Ray Serve Deployment Config

```yaml
ray_serve_deployment:
  name: "inference-endpoint"
  num_replicas: 4
  max_concurrent_queries: 16

  autoscaling_config:
    min_replicas: 2
    max_replicas: 16
    target_num_ongoing_requests_per_replica: 4

  ray_actor_options:
    num_cpus: 2
    num_gpus: 0.5

  health_check:
    endpoint: "/health"
    period_s: 10
    timeout_s: 5
    failure_threshold: 3

  graceful_shutdown:
    wait_loop_period_s: 2
    timeout_s: 20
```

---

## Monitoring Metrics

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| `ray_cluster_pending_tasks` | Ray dashboard | > 50 for > 2 min |
| `ray_worker_utilization_pct` | Ray dashboard | > 90% for > 5 min |
| `ray_object_store_used_pct` | Ray dashboard | > 80% |
| `training_job_loss` | Job logs | Diverging (NaN or > 1000) |
| `serve_p99_latency_ms` | Ray Serve metrics | > 2000 ms |
| `gpu_memory_used_pct` | NVML | > 95% |

All metrics exported to Prometheus; dashboards in Grafana under `apotheon-ray-*` namespace.