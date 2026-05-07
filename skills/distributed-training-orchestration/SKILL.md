---
name: distributed-training-orchestration
description: Orchestrates Ray Train fine-tuning workflows with DDP and FSDP distributed training strategies across the Ray compute fabric.
metadata:
  version: "0.1.0"
  category: ml-ops
  owner: platform
  maturity: draft
  dependencies: ['ray-runtime', 'model-distillation']
---

## Role

Distributed fine-tuning and training orchestrator. Translates a training job specification
into a Ray Train workflow with the appropriate distributed strategy (DDP, FSDP, DeepSpeed ZeRO),
manages the training loop, checkpoints model weights, and delivers the trained model to the
model registry for evaluation and deployment.

## Activation Triggers

- A fine-tuning job is submitted with a dataset, base model, and training config
- `lora-management` requests distributed multi-GPU LoRA fine-tuning
- A curriculum learning schedule triggers a new training phase
- A training job fails mid-run and requires checkpoint-based restart
- `reinforcement-optimizer` requests a policy gradient training run

## Execution Protocol

1. **Job specification parsing**: Parse training job config:
   - `base_model`: model ID and weight path
   - `dataset`: dataset reference and preprocessing config
   - `training_strategy`: `ddp` | `fsdp` | `deepspeed_zero2` | `deepspeed_zero3`
   - `hyperparameters`: lr, batch_size, epochs, warmup_steps, gradient_accumulation_steps
   - `lora_config`: rank, alpha, target_modules (if LoRA fine-tuning)
   - `compute`: num_workers, gpus_per_worker, memory_per_worker

2. **Ray Train job construction**: Build a `ray.train.TorchTrainer` with:
   - Training loop function referencing the strategy
   - `ScalingConfig` with the compute requirements
   - `CheckpointConfig` with save_frequency and keep_last_n checkpoints
   - `RunConfig` with experiment name and failure handling

3. **Submit to Ray**: Submit the trainer via `ray-runtime`. Monitor job status every 60 seconds.
   Stream training metrics (loss, learning_rate, throughput) to `telemetry`.

4. **Checkpoint recovery**: On job failure, detect the last valid checkpoint.
   Re-submit the job with `resume_from_checkpoint` pointing to the last checkpoint.

5. **Model registration**: On job success, collect the final checkpoint.
   Run a quick quality evaluation (loss on held-out validation set).
   If quality gate passes, submit to the model registry with training provenance metadata.

## Output Format

```yaml
training_job:
  job_id: "train-llama3-8b-finetune-20260507"
  strategy: fsdp
  status: running | completed | failed | recovering
  epoch: 0
  step: 0
  train_loss: 0.0
  val_loss: 0.0
  checkpoint_path: null
  model_registry_ref: null
  duration_gpu_hours: 0.0
```

## Quality Gates

- Val loss must be ≤ base_model val loss × 1.05 (training must not degrade base capability)
- Checkpoints saved every 500 steps minimum

## References

- `references/` — Training strategy selection guide, Ray Train job spec, checkpoint schema
