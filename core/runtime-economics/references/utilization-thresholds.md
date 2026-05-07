# Utilization Thresholds

## GPU Utilization Targets (DGX Spark)

| Resource | Target Utilization | Alert Threshold | Action |
|---|---|---|---|
| GPU SM Utilization | 70–85% | < 40% or > 95% | Rebalance workloads; alert if > 95% |
| GPU Memory (VRAM) | 80–90% | > 92% | Evict KV cache; defer non-urgent jobs |
| KV Cache Fill Rate | 60–80% | > 90% | Evict oldest Zone 3/4 entries |
| Inference queue depth | < 10 requests | > 20 requests | Activate cloud overflow routing |
| PCIe bandwidth | < 70% saturation | > 85% | Investigate transfer bottleneck |

---

## CPU Utilization Targets (Host Server)

| Resource | Target | Alert | Action |
|---|---|---|---|
| CPU utilization (avg) | 40–70% | > 85% | Scale or defer jobs |
| CPU utilization (peak) | < 90% | > 95% | Immediate load shedding |
| RAM utilization | 60–80% | > 90% | Evict caches; OOM risk |
| Disk I/O wait | < 5% | > 20% | Investigate; switch to faster storage path |

---

## Per-Model Capacity Limits

| Model | Batch Size | Max Concurrent | Max Sequence Length | Notes |
|---|---|---|---|---|
| Llama-3.1-70B (Q4) | 4 | 8 | 32K tokens | Default production model |
| Llama-3.1-8B (Q4) | 16 | 32 | 128K tokens | Fast path for simple tasks |
| LoRA adapter (active) | Same as base | Same as base | Same as base | Adapter loaded alongside base |
| Embedding (nomic) | 256 | Unlimited | 8K tokens | CPU or dedicated GPU |

---

## Overflow Routing Thresholds

When local GPU resources exceed these thresholds, route to cloud API:

| Condition | Overflow Action | Max Monthly Cloud Spend |
|---|---|---|
| Inference queue > 20 requests | Route to claude-haiku-4-5 | $500 |
| GPU memory > 92% | Route complex requests to claude-sonnet-4-6 | $2,000 |
| Local unavailable (maintenance) | Route all to cloud | $5,000 (emergency budget) |
| LoRA training in progress | Route all inference to cloud | $1,000 |

Overflow routing is logged per request. Monthly overflow spend is reviewed in runtime-economics weekly report.

---

## Batch Processing Windows

For non-latency-sensitive workloads, batch during low-utilization windows:

| Window | Days | Hours (UTC) | Allowed Batch Jobs |
|---|---|---|---|
| Primary batch | Mon–Fri | 02:00–06:00 | LoRA training, large RAG indexing, eval runs |
| Secondary batch | Sat–Sun | 00:00–08:00 | Model evaluations, synthetic data generation |
| Real-time only | Mon–Fri | 06:00–22:00 | Interactive inference only |

---

## Cost Efficiency Metrics

Track weekly:

| Metric | Formula | Target |
|---|---|---|
| GPU utilization efficiency | (active inference time / total uptime) × 100 | > 60% |
| Cost per workflow | total_compute_cost / workflows_completed | < $0.50 avg |
| Cloud overflow ratio | cloud_requests / total_requests | < 5% |
| Idle GPU time | hours_below_20%_util / total_hours | < 15% |