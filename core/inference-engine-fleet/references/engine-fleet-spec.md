# Inference Engine Fleet Specification

## Supported Engines

| Engine | Best For | GPU Memory Model | Max Throughput | Sovereign? |
|--------|----------|-----------------|----------------|------------|
| vLLM | High-throughput serving, large models | Paged KV cache | Very high | Yes |
| SGLang | Structured generation, JSON mode | Radix attention | High | Yes |
| TensorRT-LLM | NVIDIA-optimized latency-critical | FP8/INT8 quantized | Very high | Yes |
| Ollama | Local/edge single-model serving | Standard | Low-medium | Yes |
| llama.cpp | CPU/edge, small models | GGUF quantized | Low | Yes |
| DeepSpeed | Training + inference, very large models | ZeRO stages | Medium | Yes |

---

## Engine Deployment Manifest

```yaml
engine_deployment:
  engine_id: "vllm-prod-0"
  engine_type: vllm                    # vllm | sglang | trt-llm | ollama | llama-cpp | deepspeed
  version: "0.4.2"

  model:
    name: "llama-3-70b-instruct"
    weight_path: "/models/llama-3-70b"
    quantization: bfloat16             # bfloat16 | fp8 | int8 | int4 | gguf-q4_k_m
    context_length: 8192
    max_batch_size: 64

  compute:
    gpu_count: 4
    gpu_type: H100-80GB
    tensor_parallel_degree: 4         # Must equal gpu_count for tensor parallelism
    pipeline_parallel_degree: 1

  serving:
    host: "0.0.0.0"
    port: 8000
    api_format: openai                 # openai | native
    max_concurrent_requests: 256

  health_check:
    endpoint: "/health"
    interval_seconds: 15
    timeout_seconds: 5
    failure_threshold: 3               # Mark degraded after N consecutive failures

  slo:
    p95_latency_ms: 500
    availability_target: 0.999

  autoscaling:
    min_replicas: 2
    max_replicas: 8
    scale_out_trigger: "p95_latency > slo.p95_latency_ms * 0.85 OR avg_utilization > 0.75"
    scale_in_trigger: "avg_utilization < 0.40 for 15m"
    cooldown_scale_out_minutes: 5
    cooldown_scale_in_minutes: 15
```

---

## Routing Policy

```yaml
routing_policy:
  strategy: weighted_least_connections  # round_robin | least_connections | weighted_least_connections

  capability_tiers:
    - tier: nano
      max_params_b: 8
      eligible_engines: [ollama, llama-cpp, vllm]
      latency_budget_ms: 200

    - tier: standard
      max_params_b: 35
      eligible_engines: [vllm, sglang]
      latency_budget_ms: 500

    - tier: advanced
      max_params_b: 200
      eligible_engines: [vllm, trt-llm, deepspeed]
      latency_budget_ms: 2000

  fallback_chain:
    - Try requested tier
    - IF all engines degraded → try next tier down (nano → fail; standard → nano; advanced → standard)
    - IF all engines failed → return 503 with retry_after header

  affinity:
    session_affinity: false            # Stateless — no session affinity needed
    gpu_locality: prefer               # Prefer engines on same node as requester
```

---

## Health Check & Failover Protocol

```
HEALTH STATES:
  HEALTHY:  /health returns 200 within timeout; latency probe within SLO
  DEGRADED: ≥ 1 health check failed in last 3 attempts OR latency 2× SLO
  FAILED:   3 consecutive /health failures; removed from routing pool

FAILOVER:
  On DEGRADED:
    - Reduce routing weight to 0.1 (still serves requests but deprioritized)
    - Alert operator console
    - Attempt restart after 60s if still degraded

  On FAILED:
    - Remove from routing pool immediately
    - Trigger scale-out if total healthy replicas < min_replicas
    - Page on-call if healthy replicas = 0 for any tier

RECOVERY:
  - Engine marked FAILED can attempt self-heal restart (max 3 attempts)
  - Return to HEALTHY state only after 5 consecutive clean health checks
```

---

## Autoscaling Thresholds

```yaml
autoscaling:
  evaluation_interval_seconds: 60

  scale_out:
    p95_latency_breach: "p95_latency > slo.p95_latency_ms * 0.85 for 2 intervals"
    utilization_high: "avg_gpu_utilization > 0.75 for 5 intervals"
    queue_depth: "queue_depth > max_batch_size * 3"
    action: "add 2 replicas"
    max_scale_out_per_hour: 4          # Prevent runaway scaling

  scale_in:
    utilization_low: "avg_gpu_utilization < 0.40 for 15 intervals"
    off_peak: "hour in [22, 23, 0, 1, 2, 3, 4, 5] AND utilization < 0.30"
    action: "remove 1 replica"
    min_replicas_floor: 2              # Never below 2

  warm_up_period_minutes: 5           # New replicas excluded from scaling decisions during warm-up
```