# Inference Batching Policy Reference

## Batching Strategy Decision Tree

```
INPUT: request with (task_type, latency_budget_ms, batch_eligible)

IF batch_eligible == false:
    USE: immediate_dispatch (batch_size=1)

ELIF latency_budget_ms < 500:
    USE: micro_batch (batch_size=2-4, wait_time_ms=10)

ELIF latency_budget_ms < 3000:
    USE: standard_batch (batch_size=8-16, wait_time_ms=50)

ELIF task_type == "background" OR latency_budget_ms > 30000:
    USE: large_batch (batch_size=32-128, wait_time_ms=500)

ELSE:
    USE: adaptive_batch (see Adaptive Batching Algorithm)
```

---

## Batching Configuration by Task Class

| Task Class | Max Batch Size | Max Wait Time (ms) | Padding Strategy | Priority |
|---|---|---|---|---|
| P0 — incident response | 1 (no batching) | 0 | N/A | Immediate |
| P1 — interactive | 4 | 20 | Right-pad to max | High |
| P1 — streaming | 8 | 50 | Bucket padding | High |
| P2 — SDLC | 16 | 100 | Bucket padding | Normal |
| P3 — analytics | 64 | 500 | Left-pad to fixed | Low |
| Background | 128 | 2000 | Left-pad to fixed | Lowest |

### Bucket Padding

Group requests into length buckets to minimize padding waste:

```
buckets = [128, 256, 512, 1024, 2048, 4096]

FOR each request r:
    bucket = min(b FOR b IN buckets IF b >= len(r.tokens))
    assign_to_batch(r, bucket)

# Within each bucket: batch up to max_batch_size requests
# Pad shorter requests to bucket boundary
```

---

## Adaptive Batching Algorithm

```python
class AdaptiveBatcher:
    def __init__(self):
        self.current_batch_size = 8  # Start with moderate batch
        self.throughput_history = []  # (batch_size, throughput_tokens_per_sec)
        self.latency_history = []     # (batch_size, p95_latency_ms)

    def adjust_batch_size(self, latency_budget_ms, utilization_target=0.80):
        # Measure current throughput and latency
        current_throughput = self.measure_throughput()
        current_p95 = self.measure_p95_latency()

        # Latency constraint: never exceed budget
        if current_p95 > latency_budget_ms * 0.90:
            self.current_batch_size = max(1, self.current_batch_size // 2)
            return

        # GPU utilization target: scale up if underutilized
        gpu_util = self.measure_gpu_utilization()
        if gpu_util < utilization_target * 0.90:
            self.current_batch_size = min(
                self.max_batch_size,
                int(self.current_batch_size * 1.25)
            )

        # Throughput hill-climbing: compare with previous batch size
        if len(self.throughput_history) >= 2:
            prev_throughput = self.throughput_history[-2][1]
            if current_throughput < prev_throughput * 0.95:
                # Throughput degraded — revert direction
                self.current_batch_size = self.throughput_history[-2][0]
```

---

## Continuous Batching (Iteration-Level)

For streaming token generation, use continuous batching to maximize GPU utilization:

```
ITERATION-LEVEL SCHEDULING:
  Each GPU forward pass = one iteration
  New requests can JOIN mid-batch when existing requests FINISH

  Sequence states:
    WAITING: In queue, not yet in batch
    RUNNING: Currently generating (in active batch)
    SWAPPED: Paged out to CPU memory (KV cache overflow)
    FINISHED: Generation complete

  Scheduler priorities:
    1. RUNNING sequences get GPU slots by default
    2. SWAPPED sequences are brought back before WAITING
    3. WAITING sequences fill remaining GPU memory capacity

  KV cache management:
    page_size = 16 tokens  # Each page holds 16 token KV pairs
    max_pages_per_sequence = context_length / page_size
    eviction_policy = LRU when memory pressure > 90%
```

---

## Throughput vs. Latency Trade-off Model

```
throughput_gain(batch_size) = log2(batch_size) × hardware_efficiency_factor
  hardware_efficiency_factor: A100=1.0, H100=1.15, T4=0.75

latency_overhead(batch_size) = base_latency × (1 + padding_overhead(batch_size))
  padding_overhead = avg_padding_tokens / avg_sequence_length

# Optimal batch size for latency budget L:
optimal_batch_size = max(b) such that P95_latency(b) ≤ L
```

---

## Batching Performance Metrics

| Metric | Formula | Target |
|---|---|---|
| GPU MFU (Model FLOP Utilization) | actual_flops / theoretical_peak_flops | ≥ 0.45 |
| Batch efficiency | useful_tokens / total_tokens_including_padding | ≥ 0.75 |
| Queue wait time P95 | percentile(wait_times, 95) | ≤ max_wait_policy |
| Tokens per second (TPS) | total_output_tokens / wall_time | Maximize subject to latency SLO |
| Batch fill rate | avg_batch_size / max_batch_size | ≥ 0.60 |

---

## Monitoring Alerts

```yaml
alerts:
  - name: "batch_efficiency_low"
    condition: "batch_efficiency_5m_avg < 0.60"
    severity: WARN
    action: "Review bucket padding configuration"

  - name: "queue_depth_high"
    condition: "queue_depth > max_batch_size × 5"
    severity: WARN
    action: "Consider increasing batch size or scaling replicas"

  - name: "gpu_underutilized"
    condition: "gpu_mfu_5m_avg < 0.30"
    severity: WARN
    action: "Reduce max_wait_time or increase throughput load"

  - name: "latency_slo_breach"
    condition: "p95_latency > latency_budget × 1.10"
    severity: CRITICAL
    action: "Reduce batch size immediately; investigate root cause"
```