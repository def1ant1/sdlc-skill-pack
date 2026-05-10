---
name: inference-batching-optimization
description: Dynamically tunes inference batch sizes and scheduling windows to maximize GPU utilization and throughput while maintaining latency SLOs across model tiers and request priorities.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [cluster-management, model-routing, telemetry]

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

Dynamic batch size and scheduling optimizer for the inference runtime. Continuously adjusts
batch formation windows, maximum batch sizes, and priority queuing strategies to maximize
GPU utilization without violating per-tier latency SLOs.

## Activation Triggers

- GPU utilization drops below 70% for more than 60 seconds (underutilization alert)
- Latency SLO breach detected for any priority tier (over-batching signal)
- Traffic pattern change detected requiring batch parameter reconfiguration
- Scheduled optimization cycle (default: every 30 minutes)

## Execution Protocol

1. **Collect inference telemetry**: Gather current batch sizes, queue depths, per-request
   latencies, GPU utilization, and token throughput per model and priority tier.

2. **Identify optimization opportunity**: Classify current state — underutilization (increase
   batch size), SLO breach (decrease batch size or add capacity), or queue imbalance
   (adjust priority scheduling weights).

3. **Compute candidate parameters**: Run throughput-latency trade-off model to identify
   optimal batch size and window duration for each model tier at current traffic volume.

4. **Apply continuous batching**: Implement continuous batching (iteration-level scheduling)
   where supported; calculate optimal max_tokens_per_batch to prevent OOM while maximizing
   parallelism.

5. **Tune priority scheduling**: Adjust scheduling weights so P0/P1 requests are served
   within latency budget while P2/P3 requests are batched more aggressively.

6. **Validate and emit**: Monitor metrics for 5 minutes post-adjustment; roll back if SLO
   breach persists; emit optimization record with before/after metrics.

## Output Format

Batching optimization record with: `model_id`, `previous_batch_config`, `new_batch_config`,
`gpu_utilization_before/after` (%), `p95_latency_before/after` (ms), `throughput_before/after`
(tokens/s), and optimization outcome (IMPROVED/ROLLED_BACK/UNCHANGED).

## References

- `references/batching-policy.md` — batch size limits, latency SLO targets by tier, continuous batching parameters