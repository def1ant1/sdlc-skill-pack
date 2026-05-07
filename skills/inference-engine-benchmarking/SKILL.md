---
name: inference-engine-benchmarking
description: Cross-engine latency and throughput benchmarking with automatic selection recommendations for the inference fleet.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['inference-engine-fleet', 'model-benchmarking']
---

## Role

Systematic benchmarking of inference engine configurations to identify the optimal engine,
quantization, and serving configuration for each model and workload pattern. Produces
benchmark reports that feed into `inference-engine-fleet` routing policy and
`infrastructure-optimization-agent` rightsizing decisions.

## Activation Triggers

- A new engine is deployed and needs baseline benchmarking
- A new model weight or quantization is deployed (performance may differ from prior version)
- `infrastructure-optimization-agent` requests a performance comparison to support a fleet change
- Quarterly benchmark sweep is due (validate that current routing policy is still optimal)
- A significant change in workload patterns requires re-benchmarking for the new profile

## Execution Protocol

1. **Define benchmark suite**: For each engine under test, specify:
   - Concurrency levels: [1, 4, 16, 32, 64] simultaneous requests
   - Prompt lengths: [128, 512, 1024, 2048] tokens
   - Completion lengths: [64, 256, 512] tokens
   - Special modes: JSON structured output, streaming, batch

2. **Execute benchmark**: Send the defined request mix to each engine. Collect:
   - Time-to-first-token (TTFT) percentiles: p50, p95, p99
   - Total generation throughput (tokens/second)
   - End-to-end latency percentiles at each concurrency level
   - GPU memory utilization at peak concurrency
   - Cost per 1M tokens at current hardware pricing

3. **Generate comparison report**: Produce a side-by-side table:
   ```
   Engine | Concurrency | TTFT p95 | Throughput tok/s | GPU Util | Cost/1M tok
   vllm   |     32      |   180ms  |       8400       |   78%    |   $0.42
   sglang |     32      |   210ms  |       7200       |   72%    |   $0.49
   ```

4. **Recommend**: Based on SLO requirements and cost targets, recommend:
   - Best engine for latency-sensitive workloads (lowest TTFT p95)
   - Best engine for throughput-optimized workloads (highest tok/s within latency SLO)
   - Best engine for cost-optimized workloads (lowest cost/1M tokens within SLO)

5. **Publish**: Emit `benchmark.completed` event; attach report to `operator-console` and
   notify `inference-engine-fleet` to update routing weights if a new optimal configuration is found.

## Output Format

```yaml
benchmark_report:
  benchmark_id: "BENCH-2026-xxxxx"
  models_tested: ["llama-3-70b-instruct"]
  engines_compared: [vllm, sglang, trt-llm]
  winner_latency: vllm
  winner_throughput: trt-llm
  winner_cost: vllm
  routing_recommendation:
    latency_sensitive: vllm
    batch_processing: trt-llm
  report_ref: "telemetry/benchmarks/BENCH-2026-xxxxx"
```

## Quality Gates

- Minimum 100 requests per concurrency level for statistical validity
- Warm-up period of 30 requests discarded before metrics collection

## References

- `references/` — Benchmark suite definition, metrics collection protocol, comparison report schema
