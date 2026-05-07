# Ray Serve Management — Deployment Patterns & Configuration

## Core Deployment Patterns

### Pattern 1: Single Model Endpoint

```python
import ray
from ray import serve
from ray.serve.handle import DeploymentHandle

@serve.deployment(
    name="llm-endpoint",
    num_replicas=4,
    ray_actor_options={"num_gpus": 0.5, "num_cpus": 2},
    autoscaling_config={
        "min_replicas": 2,
        "max_replicas": 16,
        "target_num_ongoing_requests_per_replica": 4,
    },
)
class LLMEndpoint:
    def __init__(self, model_id: str):
        from vllm import AsyncLLMEngine, EngineArgs
        args = EngineArgs(model=model_id, gpu_memory_utilization=0.85)
        self.engine = AsyncLLMEngine.from_engine_args(args)

    async def __call__(self, request):
        body = await request.json()
        # ... inference logic
        return {"output": "..."}
```

### Pattern 2: Multi-Model Router

```python
@serve.deployment(name="model-router")
class ModelRouter:
    def __init__(self):
        self.small: DeploymentHandle = serve.get_deployment_handle("llm-3b")
        self.large: DeploymentHandle = serve.get_deployment_handle("llm-8b")

    async def __call__(self, request):
        body = await request.json()
        complexity = body.get("complexity", "standard")
        if complexity == "complex":
            return await self.large.remote(body)
        return await self.small.remote(body)
```

### Pattern 3: Composition Pipeline

```python
@serve.deployment(name="rag-pipeline")
class RAGPipeline:
    def __init__(self):
        self.retriever: DeploymentHandle = serve.get_deployment_handle("vector-retriever")
        self.generator: DeploymentHandle = serve.get_deployment_handle("llm-endpoint")

    async def __call__(self, request):
        body = await request.json()
        # Step 1: retrieve context
        context = await self.retriever.remote(body["query"])
        # Step 2: generate with context
        augmented = {**body, "context": context}
        return await self.generator.remote(augmented)
```

---

## Deployment Configuration Schema

```yaml
serve_deployment:
  name: "llm-endpoint"
  version: "2026-05-07"

  scaling:
    num_replicas: 4
    autoscaling:
      enabled: true
      min_replicas: 2
      max_replicas: 16
      target_num_ongoing_requests_per_replica: 4
      downscale_delay_s: 300   # Wait 5 min before scaling down
      upscale_delay_s: 30

  resources_per_replica:
    num_cpus: 2
    num_gpus: 0.5
    memory: 8_000_000_000    # 8 GB

  health_check:
    initial_delay_s: 30      # Wait for model load
    period_s: 10
    timeout_s: 5
    failure_threshold: 3
    success_threshold: 1

  graceful_shutdown:
    wait_loop_period_s: 2
    timeout_s: 30

  logging:
    access_log: true
    request_response_log: false   # Too verbose for production
```

---

## Traffic Management Policies

### Canary Deployment

```yaml
traffic_policy:
  type: canary
  deployments:
    - name: "llm-endpoint-stable"
      weight: 0.90
    - name: "llm-endpoint-canary"
      weight: 0.10

  promotion_schedule:
    - after_minutes: 10
      new_canary_weight: 0.25
    - after_minutes: 30
      new_canary_weight: 0.50
    - after_minutes: 60
      new_canary_weight: 1.00

  abort_if:
    error_rate_delta_pct: "> 2.0"    # Canary vs stable
    latency_delta_pct: "> 50"
```

### A/B Split

```yaml
traffic_policy:
  type: ab_split
  deployments:
    - name: "llm-endpoint-a"
      weight: 0.50
      variant_id: "variant-A"
    - name: "llm-endpoint-b"
      weight: 0.50
      variant_id: "variant-B"
  experiment_id: "RL-EXP-2026-xxxxx"   # Linked to reinforcement-optimizer
```

---

## Serve Metrics & Alerting

| Metric | Description | Alert Threshold |
|--------|-------------|----------------|
| `serve_num_ongoing_requests` | Active in-flight requests | > `max_replicas × target × 1.2` |
| `serve_deployment_error_rate` | Error rate per deployment | > 1% |
| `serve_p95_latency_ms` | P95 end-to-end latency | > 3,000 ms |
| `serve_replica_restart_count` | Replica crash restarts | > 2 in 10 min |
| `serve_queue_length` | Queued but not started | > 20 |

All metrics scraped by Prometheus; alert rules in `apotheon-serve-alerts.yaml`.

---

## Deployment Lifecycle Commands

```bash
# Deploy / update
serve deploy serve_config.yaml

# Status
serve status

# List deployments
serve list

# Scale manually
serve scale llm-endpoint --num-replicas 8

# Roll back to previous version
serve rollback llm-endpoint

# Delete deployment
serve delete llm-endpoint

# Fetch logs
serve logs llm-endpoint --tail 100
```

---

## Graceful Update Protocol

```
1. Submit new deployment config
        │
        ▼
2. Ray Serve starts new replicas with new config
   (old replicas continue serving)
        │
        ▼
3. Health checks pass on new replicas
        │
        ▼
4. Traffic gradually shifted to new replicas
   (configurable via `max_surge_replicas`)
        │
        ▼
5. Old replicas drained:
   - Accept no new requests
   - Complete in-flight requests (up to graceful_shutdown.timeout_s)
   - Terminate
        │
        ▼
6. Update complete; emit deployment_updated event
```