# LoRA Registry

Used by `core/lora-lifecycle/SKILL.md` to define the adapter registry schema,
benchmark thresholds, training config format, and version management rules.

---

## Adapter Registry Entry Schema

```yaml
adapter:
  id: "LORA-YYYYMMDD-NNN"
  name: "<task-type>-<base-model-short>-v<N>"   # e.g. code-review-coder32b-v3
  task_type: "<task type from use case table>"
  base_model: "<model name>"                     # e.g. qwen2.5-coder-32b
  base_model_quantization: "Q4_K_M | Q8 | FP16"
  status: "candidate | active | deprecated | degraded | rejected"
  version: <integer>                             # increment per adapter per task slot

  training:
    dataset_id: "DS-YYYYMMDD-NNN"
    dataset_size: <number>          # training examples
    eval_split: 0.10                # 10% held out for eval
    config:
      rank: 16                      # LoRA rank (r)
      alpha: 32                     # LoRA alpha
      target_modules: ["q_proj", "v_proj"]
      learning_rate: 0.0002
      epochs: 3
      batch_size: 8
      gradient_accumulation_steps: 4
      warmup_ratio: 0.05
    trained_at: "YYYY-MM-DDThh:mm:ssZ"
    training_duration_hours: <number>
    gpu_hours_used: <number>

  benchmark_scores:
    task_quality: <0.0–1.0>         # domain-specific quality score
    instruction_following: <0.0–1.0>
    hallucination_rate: <0.0–1.0>   # lower is better (inverted in threshold check)
    latency_overhead_pct: <number>  # % overhead vs base model
    safety_pass_rate: <0.0–1.0>     # red-team eval pass rate
    promotion_verdict: "PROMOTE | HOLD | REJECT"

  promotion:
    promoted_at: "YYYY-MM-DDThh:mm:ssZ | null"
    approved_by: "<operator | null>"
    human_sample_approval: true | false

  drift_monitoring:
    last_checked_at: "YYYY-MM-DDThh:mm:ssZ"
    scores_at_last_check: {}        # same structure as benchmark_scores
    drift_alert_threshold: 0.05    # 5% decline triggers re-evaluation

  serving:
    adapter_path: "/models/loras/<adapter_id>/"
    backend: "vllm | llama.cpp | transformers"
    load_on_startup: true | false
    max_concurrent_requests: 10

  notes: "<optional>"
```

---

## Benchmark Thresholds

### Promotion Thresholds (must meet ALL to PROMOTE)

| Dimension | PROMOTE (min) | HOLD range | REJECT (max) |
|---|---|---|---|
| Task quality | ≥ 0.80 | 0.70–0.79 | < 0.70 |
| Instruction following | ≥ 0.85 | 0.75–0.84 | < 0.75 |
| Hallucination rate | ≤ 0.02 (≤ 2%) | 0.02–0.05 | > 0.05 |
| Latency overhead | ≤ 10% | 10–20% | > 20% |
| Safety pass rate | ≥ 0.98 | 0.95–0.97 | < 0.95 |

**HOLD** means: do not promote; retrain with more data or adjust hyperparameters.
**REJECT** means: discard adapter; start new training run.

### Regression Check

Before promoting a new adapter version: compare scores against the currently active
adapter. Fail condition: any dimension drops > 2% compared to active adapter.
On regression: verdict = HOLD regardless of absolute threshold.

---

## Training Config Templates

### Code Generation / Review (32B base)

```yaml
lora_config:
  task: code-generation
  base: qwen2.5-coder-32b-Q4_K_M
  rank: 32          # higher rank for complex task
  alpha: 64
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]
  learning_rate: 0.00015
  epochs: 5
  batch_size: 4
  gradient_checkpointing: true
  min_training_examples: 1000
```

### Fast Intent Classification (7B base)

```yaml
lora_config:
  task: intent-classification
  base: qwen2.5-7b-Q4_K_M
  rank: 8           # low rank sufficient for classification
  alpha: 16
  target_modules: ["q_proj", "v_proj"]
  learning_rate: 0.0003
  epochs: 3
  batch_size: 16
  min_training_examples: 500
```

### Long-Context Tasks (72B base)

```yaml
lora_config:
  task: compliance-drafting
  base: qwen2.5-72b-Q4_K_M
  rank: 16
  alpha: 32
  target_modules: ["q_proj", "v_proj"]
  learning_rate: 0.0001
  epochs: 2
  batch_size: 2
  gradient_accumulation_steps: 16
  min_training_examples: 800
```

---

## Version Management Rules

1. Each task type has one `status: active` adapter at a time
2. On promotion: old `active` adapter moves to `status: deprecated`
3. Deprecated adapters retained for 90 days (for rollback), then purged
4. Rejected adapters retained for 14 days (for debugging), then purged
5. Version numbers are monotonically increasing per task slot — never reuse
6. Maximum active adapters simultaneously: 6 (DGX Spark VRAM budget)

### VRAM Budget for LoRA Adapters

| Base Model | Adapter VRAM overhead | Max concurrent |
|---|---|---|
| 7B Q4_K_M | ~100MB | 8 adapters |
| 32B Q4_K_M | ~300MB | 4 adapters |
| 72B Q4_K_M | ~600MB | 2 adapters |

Total adapter budget: 4GB of the 128GB DGX Spark VRAM pool.
If budget would be exceeded: deprecate lowest-priority adapter before promoting new one.

---

## Adapter Audit

Run monthly:
```
[ ] All active adapters have benchmark scores < 90 days old
[ ] All deprecated adapters are within 90-day retention window or purged
[ ] No adapters in status: candidate for > 14 days without promotion decision
[ ] VRAM budget not exceeded by active adapter set
[ ] Rollback chain is intact: prior_adapter_version exists for each active adapter
```