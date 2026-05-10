---
name: inference-engine-deployment
description: Engine-specific deployment playbooks for vLLM, SGLang, TRT-LLM, Ollama, llama.cpp, and DeepSpeed sovereign inference engines.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['inference-engine-fleet', 'cluster-management']

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

Operator-level deployment playbooks for each supported sovereign inference engine. Translates
a model deployment request into engine-specific configuration, Kubernetes manifests, and
startup procedures. Handles quantization format selection, GPU tensor parallelism configuration,
serving endpoint setup, and warm-up validation before handing off to `inference-engine-fleet`.

## Activation Triggers

- A new model is approved for deployment to the inference fleet
- An existing engine deployment requires a version update or configuration change
- `inference-engine-fleet` requests a new engine replica for autoscaling
- Operator triggers a migration from one engine type to another for a model
- A model weight update is available and requires rolling deployment

## Execution Protocol

1. **Engine selection**: If engine type is not specified, recommend based on model characteristics:
   - Model size ≤ 8B, CPU-only: `llama.cpp` with GGUF quantization
   - Model size ≤ 13B, single-GPU: `Ollama`
   - Production high-throughput, multi-GPU: `vLLM` with PagedAttention
   - Structured generation / JSON mode required: `SGLang`
   - NVIDIA-only, latency-critical: `TensorRT-LLM` with FP8 quantization
   - Very large model (70B+), multi-node: `DeepSpeed` with tensor+pipeline parallelism

2. **Manifest generation**: Generate engine-specific deployment manifests:
   - Kubernetes Deployment + Service + ConfigMap
   - GPU resource requests (nvidia.com/gpu)
   - Environment variables for engine configuration (tensor parallel degree, max batch, context length)
   - Model weight PVC mount or S3 download init container

3. **Deploy**: Apply manifests via `cluster-management`. Wait for pod readiness.

4. **Warm-up validation**: Send 10 synthetic requests through the new deployment.
   Verify: response is valid, p99 latency within engine SLO, no OOM errors in logs.
   Fail the deployment and rollback on validation failure.

5. **Register**: On success, register the new engine instance in `inference-engine-fleet` registry.

## Output Format

```yaml
engine_deployment:
  deployment_id: "deploy-vllm-llama3-70b-20260507"
  engine_type: vllm
  model: "llama-3-70b-instruct"
  status: success | failed | rolled_back
  manifest_ref: "k8s/deployments/vllm-llama3-70b"
  warmup_p99_latency_ms: 0
  registered_in_fleet: true
```

## Quality Gates

- Warm-up validation must pass before fleet registration
- Rollback must complete within 5 minutes if validation fails

## References

- `references/` — Engine-specific manifest templates, quantization selection matrix, warm-up test suite
