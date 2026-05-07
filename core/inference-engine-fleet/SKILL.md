---
name: inference-engine-fleet
description: Manages deployment, configuration, health monitoring, failover, and autoscaling of sovereign inference engines (vLLM, SGLang, TRT-LLM, Ollama, llama.cpp, DeepSpeed).
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['cluster-management', 'telemetry', 'event-bus']
---

## Role

Fleet manager for sovereign inference engines deployed in the enterprise AI stack. Manages
deployment manifests, live configuration, health monitoring, automatic failover, and
autoscaling for vLLM, SGLang, TensorRT-LLM, Ollama, llama.cpp, and DeepSpeed engines.
Exposes a unified routing interface so callers request model capability without knowing
which engine instance will serve the request.

## Activation Triggers

- New engine deployment requested via operator directive or `inference-engine-deployment`
- Engine health check fails (triggers failover evaluation)
- Fleet p95 latency exceeds SLO threshold (triggers scale-out)
- Fleet utilization drops below floor threshold for cooldown period (triggers scale-in)
- `inference-engine-benchmarking` completes a cross-engine benchmark (may trigger routing policy update)
- Model weight version update is available requiring rolling restart

## Execution Protocol

1. **Fleet registry**: Maintain the engine registry with: engine type, model loaded, GPU
   assignment, current status (healthy/warming/degraded/failed), version, and SLO parameters.

2. **Health monitoring**: Poll each engine endpoint every 15 seconds:
   - `/health` HTTP check (timeout 5s → mark degraded after 3 consecutive failures)
   - Latency probe: send a synthetic request and record time-to-first-token
   - GPU memory utilization from engine metrics endpoint

3. **Routing**: On an inference request, select the best healthy engine instance:
   - Filter to engines serving the requested model or compatible capability tier
   - Apply round-robin within the filtered set weighted by current queue depth
   - If all engines for the requested model are degraded, fail over to a fallback capability tier
     and annotate the response with `fallback: true`

4. **Autoscaling**: Evaluate scale triggers every 60 seconds (see `references/` for thresholds).
   Invoke `cluster-management` to add or remove engine pods. Enforce min/max replica bounds.

5. **Rolling updates**: On model weight update, perform a rolling restart:
   warm the new version on 1 replica → health check passes → shift traffic → drain old replicas.

## Output Format

```yaml
fleet_status:
  engines:
    - engine_id: "vllm-0"
      engine_type: vllm
      model: "llama-3-70b"
      status: healthy
      gpu_utilization_pct: 72
      queue_depth: 4
      p95_latency_ms: 420
  routing_decision:
    selected_engine: "vllm-0"
    fallback_used: false
  autoscaling_action: none | scale_out | scale_in
  fleet_p95_latency_ms: 0
  fleet_slo_met: true
```

## References

- `references/` — Engine deployment manifests, routing policy spec, autoscaling thresholds, health check parameters
