# Inference Engine Benchmarking — Benchmark Suite Specification

## Benchmark Suite Overview

| Suite ID | Name | Focus | Duration |
|----------|------|-------|----------|
| `BENCH-LATENCY` | Latency Profile | P50/P95/P99 at varied concurrency | ~30 min |
| `BENCH-THROUGHPUT` | Throughput Saturation | Max tokens/sec at full load | ~20 min |
| `BENCH-QUALITY` | Output Quality | MMLU, HumanEval, task accuracy | ~60 min |
| `BENCH-LONG-CTX` | Long Context | 8K/32K/128K context performance | ~45 min |
| `BENCH-COST` | Cost Efficiency | $/1K tokens at target quality | ~15 min |
| `BENCH-STABILITY` | Stability Soak | 4-hour sustained load | 4 hours |

---

## Latency Benchmark (`BENCH-LATENCY`)

```yaml
bench_latency:
  suite_id: BENCH-LATENCY
  prompts:
    - category: short
      input_tokens: 50
      output_tokens: 100
      count: 100
    - category: medium
      input_tokens: 500
      output_tokens: 500
      count: 100
    - category: long
      input_tokens: 2000
      output_tokens: 1000
      count: 50

  concurrency_levels: [1, 4, 8, 16, 32]

  metrics_collected:
    - ttft_ms            # Time to first token
    - tpot_ms            # Time per output token
    - e2e_latency_ms     # End-to-end latency
    - p50_ms
    - p95_ms
    - p99_ms

  pass_criteria:
    p95_latency_short_1c_ms: "< 800"
    p95_latency_medium_4c_ms: "< 2000"
    p99_latency_long_8c_ms: "< 8000"
```

---

## Throughput Benchmark (`BENCH-THROUGHPUT`)

```yaml
bench_throughput:
  suite_id: BENCH-THROUGHPUT
  load_profile:
    ramp_up_seconds: 60
    steady_state_seconds: 600
    ramp_down_seconds: 60

  concurrency_sweep: [1, 4, 8, 16, 32, 64]

  metrics_collected:
    - tokens_per_second_input
    - tokens_per_second_output
    - requests_per_second
    - gpu_utilization_pct
    - gpu_memory_utilization_pct
    - error_rate_pct

  pass_criteria:
    peak_output_tokens_per_second:
      "7B model, A10G GPU": "> 1500"
      "13B model, A100 GPU": "> 800"
    sustained_error_rate_pct: "< 0.1"
```

---

## Quality Benchmark (`BENCH-QUALITY`)

```yaml
bench_quality:
  suite_id: BENCH-QUALITY

  evaluations:
    - name: MMLU
      task_count: 200
      categories: [STEM, humanities, social_science, other]
      metric: accuracy_pct
      target: "> 65"   # Baseline for 7B models

    - name: HumanEval
      task_count: 164
      metric: pass_at_1_pct
      target: "> 30"   # Baseline for 7B models

    - name: task_completion
      description: "SDLC-specific eval set: code review, requirement extraction, test generation"
      task_count: 100
      metric: task_accuracy_pct
      target: "> 70"

    - name: instruction_following
      description: "IFEval benchmark subset"
      task_count: 50
      metric: strict_accuracy_pct
      target: "> 60"

  regression_threshold:
    max_quality_drop_vs_baseline_pct: 2.0   # Flag if >2% drop vs. previous deployment
```

---

## Benchmark Result Schema

```yaml
benchmark_result:
  result_id: "BENCH-RES-2026-xxxxx"
  run_at: "2026-05-07T10:00:00Z"
  engine_type: vllm
  model_id: "meta-llama/Llama-3.1-8B-Instruct"
  model_format: BF16
  hardware: "4× A10G 24GB"
  suite_ids: [BENCH-LATENCY, BENCH-THROUGHPUT, BENCH-QUALITY]

  latency:
    p50_ms: 320
    p95_ms: 890
    p99_ms: 1450
    ttft_p50_ms: 85

  throughput:
    peak_output_tokens_per_second: 1820
    requests_per_second: 28
    gpu_utilization_pct: 88

  quality:
    mmlu_accuracy_pct: 68.2
    humaneval_pass_at_1_pct: 34.1
    task_completion_accuracy_pct: 74.5

  pass: true
  regressions_detected: []

  comparison:
    baseline_result_id: "BENCH-RES-2026-yyyyy"
    latency_delta_pct: -3.2    # Negative = improvement
    throughput_delta_pct: +5.1
    quality_delta_pct: +0.8
```

---

## Benchmark Scheduling Policy

```yaml
benchmark_triggers:
  pre_deployment:
    suites: [BENCH-LATENCY, BENCH-THROUGHPUT, BENCH-QUALITY]
    blocking: true        # Deployment blocked if any suite fails

  post_deployment_24h:
    suites: [BENCH-STABILITY]
    blocking: false       # Non-blocking; alert on failure

  weekly_regression:
    suites: [BENCH-LATENCY, BENCH-THROUGHPUT, BENCH-QUALITY, BENCH-LONG-CTX]
    schedule: "0 1 * * 0"  # Sunday 1 AM UTC
    blocking: false

  on_demand:
    suites: all
    initiated_by: human_or_agent
    blocking: false
```

---

## Comparison Matrix Template

| Metric | Engine A (vLLM) | Engine B (TGI) | Engine C (Ollama) | Winner |
|--------|----------------|----------------|-------------------|--------|
| P95 Latency (ms) | 890 | 1050 | 1200 | Engine A |
| Peak Throughput (tok/s) | 1820 | 1640 | 920 | Engine A |
| MMLU Accuracy (%) | 68.2 | 68.0 | 67.8 | Engine A |
| GPU Utilization (%) | 88 | 82 | 71 | Engine B (efficient) |
| Cost/1K tok (USD) | $0.0012 | $0.0014 | $0.0009 | Engine C |
| Setup Complexity | Medium | Medium | Low | Engine C |