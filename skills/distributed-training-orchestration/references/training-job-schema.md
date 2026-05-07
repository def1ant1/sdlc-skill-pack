# Distributed Training Orchestration — Training Job Schema & Protocols

## Training Job Schema

```yaml
training_job:
  job_id: "TRAIN-2026-xxxxx"
  submitted_by: "ml-ops-agent"
  submitted_at: "2026-05-07T10:00:00Z"
  status: queued | running | completed | failed | cancelled

  # What to train
  model:
    base_model_id: "meta-llama/Llama-3.1-8B"
    base_model_uri: "gs://apotheon-models/Llama-3.1-8B/"
    training_type: full_finetune | lora | qlora | reward_model | dpo | rlhf
    lora_config:
      rank: 16
      alpha: 32
      target_modules: [q_proj, v_proj, k_proj, o_proj]
      dropout: 0.05

  # Training data
  data:
    train_uri: "gs://apotheon-datasets/sdlc-v3-train.jsonl"
    eval_uri: "gs://apotheon-datasets/sdlc-v3-eval.jsonl"
    format: alpaca | sharegpt | raw_completion | preference_pairs
    max_seq_length: 4096
    packing: true          # Pack short sequences for efficiency

  # Compute allocation
  compute:
    framework: deepspeed | fsdp | accelerate
    deepspeed_stage: 2     # ZeRO-2
    num_nodes: 1
    gpus_per_node: 4
    gpu_type: A100_80GB

  # Hyperparameters
  hyperparameters:
    num_epochs: 3
    learning_rate: 2.0e-4
    lr_scheduler: cosine_with_warmup
    warmup_ratio: 0.03
    batch_size_per_gpu: 4
    gradient_accumulation_steps: 8
    effective_batch_size: 128    # = 4 × 8 × 4 GPUs
    weight_decay: 0.01
    gradient_clipping: 1.0
    bf16: true

  # Checkpointing
  checkpointing:
    strategy: steps            # steps | epoch | best_metric
    save_every_n_steps: 500
    output_uri: "gs://apotheon-checkpoints/TRAIN-2026-xxxxx/"
    keep_last_n: 3
    save_optimizer_state: true

  # Evaluation
  evaluation:
    eval_every_n_steps: 100
    metrics: [eval_loss, perplexity, task_accuracy]
    early_stopping:
      enabled: true
      metric: eval_loss
      patience: 3            # Stop if no improvement for 3 eval cycles
      min_delta: 0.001

  # Outputs
  output:
    merged_model_uri: null    # Populated on completion for LoRA merges
    adapter_uri: "gs://apotheon-checkpoints/TRAIN-2026-xxxxx/final-adapter/"
    training_report_uri: "gs://apotheon-reports/TRAIN-2026-xxxxx.yaml"
```

---

## Training Run Lifecycle

```
TRAINING JOB LIFECYCLE

1. Job submitted → status: queued
        │
        ▼
2. Resource allocation (Ray cluster)
   ├── GPU nodes available → status: running
   └── No capacity → wait in queue (max 6h before alert)
        │
        ▼
3. Data preprocessing
   ├── Tokenize + pack sequences
   └── Validate dataset integrity (no corrupted records)
        │
        ▼
4. Training loop
   ├── Emit metrics every N steps to MLflow
   ├── Checkpoint every N steps to GCS
   └── Evaluate every N steps; check early stopping
        │
        ├── Normal completion → status: completed
        ├── Early stopping triggered → status: completed (early_stopped: true)
        ├── OOM → status: failed; alert ops
        └── Divergence (loss=NaN) → status: failed; alert ml-ops
        │
        ▼
5. Post-training
   ├── Merge LoRA adapter into base model (if applicable)
   ├── Run eval suite (BENCH-QUALITY)
   └── Publish artifact to model registry
```

---

## Distributed Strategy Selection Guide

| Training Type | Model Size | Recommended Strategy | ZeRO Stage |
|--------------|------------|---------------------|------------|
| LoRA finetune | Any | DeepSpeed | 2 |
| QLoRA finetune | Any (4-bit base) | Accelerate + bitsandbytes | N/A |
| Full finetune | ≤ 7B, single GPU | Accelerate | N/A |
| Full finetune | 7B–13B, multi-GPU | DeepSpeed | 2 |
| Full finetune | > 13B | DeepSpeed | 3 or FSDP |
| RLHF / DPO | Any | TRL + DeepSpeed | 2 |
| Reward model | ≤ 7B | Accelerate | N/A |

---

## Training Health Checks

```yaml
training_health_checks:
  loss_divergence:
    trigger: "loss is NaN OR loss > 100"
    action: terminate_immediately
    notify: ml-ops

  gradient_explosion:
    trigger: "gradient_norm > 10 for > 10 consecutive steps"
    action: alert + continue   # Gradient clipping should handle it
    notify: ml-ops

  gpu_oom:
    trigger: "CUDA out of memory error"
    action: terminate + suggest_remediation
    remediation:
      - "Reduce batch_size_per_gpu"
      - "Increase gradient_accumulation_steps"
      - "Switch to QLoRA or ZeRO-3"

  data_stall:
    trigger: "No training step for > 5 min"
    action: alert + investigate
    notify: ml-ops

  cost_overrun:
    trigger: "Estimated cost > 2× budget"
    action: alert + pause for human approval
    notify: cfo-agent
```

---

## Training Metrics Schema (MLflow)

```yaml
mlflow_experiment:
  experiment_name: "apotheon-sdlc-finetune"
  run_name: "TRAIN-2026-xxxxx"

  logged_metrics:
    every_step:
      - train/loss
      - train/learning_rate
      - train/gradient_norm
      - train/tokens_per_second
      - train/gpu_memory_allocated_gb

    every_eval:
      - eval/loss
      - eval/perplexity
      - eval/task_accuracy

  logged_params:
    model_id: ~
    training_type: ~
    num_epochs: ~
    learning_rate: ~
    batch_size_effective: ~
    lora_rank: ~

  artifacts:
    - path: "final-adapter/"
      description: "Trained LoRA adapter weights"
    - path: "training-report.yaml"
      description: "Full training report including eval results"
```