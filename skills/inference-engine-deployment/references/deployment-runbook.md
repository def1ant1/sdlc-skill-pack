# Inference Engine Deployment — Deployment Runbook

## Engine Deployment Runbook

### Standard Model Deployment

```
STEP 1: Pre-deployment validation
  □ Model artifact checksum verified against registry
  □ VRAM requirement ≤ available GPU memory × 0.85
  □ No active A/B tests on target engine slot
  □ Rollback version identified and pinned

STEP 2: Stage to warm pool
  □ Pull model artifact to engine node local storage
  □ Load model into warm (standby) slot
  □ Run smoke test: prompt "What is 2+2?", expect response containing "4"
  □ Verify P95 latency < 2× baseline

STEP 3: Traffic cut (blue/green)
  □ Set warm slot weight to 5% (canary)
  □ Monitor error rate for 10 min; abort if > 1%
  □ Ramp: 5% → 25% → 50% → 100% (10-min hold each)
  □ Decommission old slot after 30 min at 100%

STEP 4: Post-deployment validation
  □ Health check endpoint returns 200
  □ Token throughput ≥ 90% of pre-deployment baseline
  □ Error rate < 0.5%
  □ Memory utilization < 85% VRAM
  □ Deployment event logged to audit trail
```

---

## Rollback Procedure

```
TRIGGER CONDITIONS (auto-rollback):
  - Error rate > 5% for > 2 minutes
  - P95 latency > 3× baseline for > 5 minutes
  - OOM kill detected
  - Health check fails 3 consecutive times

ROLLBACK STEPS:
  1. Immediately route 100% traffic to previous stable slot
  2. Log ROLLBACK_TRIGGERED event with trigger details
  3. Alert on-call via notification-orchestration (P1)
  4. Preserve failed deployment artifacts for post-mortem
  5. Block re-deployment of same artifact until RCA complete
```

---

## Engine Sizing Guide

| Model Size | VRAM Needed | Recommended GPU | Max Throughput (tok/s) |
|------------|------------|----------------|----------------------|
| 1B (GGUF Q4) | < 2 GB | CPU (no GPU needed) | 50–100 |
| 3B (GGUF Q8) | 4 GB | RTX 3060 / A10 | 80–150 |
| 7B (BF16) | 16 GB | A10G / RTX 4080 | 40–80 |
| 8B (GGUF Q8) | 10 GB | A10G | 60–100 |
| 13B (BF16) | 26 GB | A100 40GB | 25–50 |
| 70B (GGUF Q4) | 40 GB | A100 80GB | 10–20 |

---

## Deployment Manifest Schema

```yaml
engine_deployment:
  deployment_id: "ENG-DEPLOY-2026-xxxxx"
  engine_type: vllm | ollama | llama_cpp | tgi
  model_id: "meta-llama/Llama-3.1-8B-Instruct"
  model_format: BF16 | GGUF | AWQ | GPTQ
  quantization: null | Q4_K_M | Q8_0 | INT8 | INT4

  target:
    cluster: apotheon-inference-prod
    node_pool: gpu-a10g
    replicas: 4

  engine_config:
    max_model_len: 8192
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.85
    max_num_seqs: 256
    enable_prefix_caching: true

  serving:
    port: 8000
    api_format: openai_compatible
    endpoint_path: "/v1/chat/completions"

  health_check:
    path: "/health"
    interval_seconds: 10
    failure_threshold: 3

  deployment_strategy:
    type: blue_green | rolling | canary
    canary_weight_pct: 5
    canary_hold_minutes: 10
    rollout_steps: [5, 25, 50, 100]

  rollback:
    previous_deployment_id: "ENG-DEPLOY-2026-yyyyy"
    auto_rollback_enabled: true
    rollback_triggers:
      error_rate_pct_threshold: 5.0
      latency_p95_degradation_pct: 200
```

---

## Inference Engine Fleet Health States

| State | Description | Action |
|-------|-------------|--------|
| `healthy` | All checks passing | None |
| `degraded` | 1+ checks failing but serving | Alert + investigate |
| `unhealthy` | Majority checks failing | Remove from rotation |
| `starting` | Warming up | Hold traffic until healthy |
| `draining` | Graceful shutdown in progress | No new requests |
| `failed` | Crashed or unresponsive | Restart + alert |

---

## Post-Deployment Metrics (30-min window)

```yaml
deployment_validation_metrics:
  - metric: error_rate_pct
    target: "< 0.5"
    alert_threshold: "> 2.0"

  - metric: p50_latency_ms
    target: "< 500"
    alert_threshold: "> 1500"

  - metric: p95_latency_ms
    target: "< 2000"
    alert_threshold: "> 5000"

  - metric: tokens_per_second
    target: "> 90% of baseline"
    alert_threshold: "< 70% of baseline"

  - metric: gpu_memory_utilization_pct
    target: "< 85"
    alert_threshold: "> 95"
```