# Distillation Protocol Reference

## Distillation Method Catalog

### Method 1: Response Distillation (Data Collection)

Generate a training dataset from teacher model outputs:

```
Protocol:
1. Define target capability set C = {c1, c2, ..., cn}
2. For each capability ci:
   a. Sample N_i prompts from capability-specific prompt pool
   b. Generate teacher responses: T(prompt) → (response, chain_of_thought)
   c. Filter responses by quality score ≥ quality_threshold[ci]
3. Combine into distillation dataset D = {(prompt, teacher_response)}

Quality filtering:
  factual_accuracy_score ≥ 0.90
  response_completeness_score ≥ 0.85
  reasoning_coherence_score ≥ 0.80
  constitutional_compliance_score = 1.00  # No exceptions
```

### Method 2: Knowledge Distillation (Soft Targets)

Train student to match teacher's output distribution:

```
Loss function:
  L_distill = α × L_KD + (1 - α) × L_CE

  L_KD = KL_divergence(softmax(student_logits / T), softmax(teacher_logits / T))
  L_CE = cross_entropy(student_logits, hard_labels)

  T = temperature (typically 2–10; higher = softer distribution)
  α = distillation weight (typically 0.5–0.9)

Hyperparameter selection:
  T = 4 for general tasks (smoothed but discriminative)
  T = 8 for complex reasoning tasks (more uncertainty transfer)
  α = 0.7 (prioritize teacher signal; maintain ground truth anchor)
```

### Method 3: Feature Distillation (Intermediate Representations)

Match intermediate activations between teacher and student:

```
Layer mapping strategies:
  - LAST_N: Student's last N layers match teacher's last N layers
  - UNIFORM: Evenly spaced teacher layers matched to student layers
  - PKD (Patient KD): Student learns from teacher's intermediate layers

Feature distillation loss:
  L_feat = Σ_l MSE(W_l × student_hidden[l], teacher_hidden[map(l)])
  W_l = learnable projection matrix (student_dim → teacher_dim)

Total loss:
  L_total = L_CE + β × L_feat + γ × L_KD
  Typical: β = 0.1, γ = 0.5
```

### Method 4: Chain-of-Thought Distillation

Transfer reasoning process, not just final answers:

```
Dataset format:
  {
    "prompt": "Solve: What is the ROI of investing $100K at 8% for 5 years?",
    "chain_of_thought": "Step 1: FV = PV × (1+r)^n = 100000 × (1.08)^5...",
    "answer": "ROI = 46.9% over 5 years"
  }

Training:
  - Include CoT in training target (not just final answer)
  - Use "step-by-step thinking" format for all reasoning examples
  - Filter: CoT must be logically consistent with final answer
  - Discard: CoT where intermediate steps contradict each other
```

---

## Distillation Pipeline Steps

```
STEP 1: Teacher capability audit
  - Identify target capabilities and current teacher performance
  - Set capability-specific quality thresholds

STEP 2: Prompt pool construction
  - 1,000–10,000 prompts per target capability
  - Mix difficulty levels: 20% easy, 60% medium, 20% hard
  - Include adversarial examples to test robustness

STEP 3: Teacher inference (data generation)
  - Generate N responses per prompt (N=1 for deterministic; N=5 for diverse)
  - Apply quality filters (see Method 1)
  - Target: 50,000–500,000 high-quality (prompt, response) pairs

STEP 4: Student architecture selection
  - Target size: typically 3×–10× smaller than teacher
  - Architecture: match teacher family if possible (better feature alignment)
  - Verify student parameter budget vs. latency/cost target

STEP 5: Training
  - Phase 1: Supervised fine-tuning on distillation dataset (5–10 epochs)
  - Phase 2: Soft-target knowledge distillation (3–5 epochs, temperature=4)
  - Phase 3 (optional): Feature distillation for last 2 layers (2 epochs)
  - Evaluate on held-out validation set after each phase

STEP 6: Evaluation and promotion
  - Run capability evaluation on held-out test set
  - Compare to teacher on each capability: student must reach ≥ 85% of teacher
  - Run alignment test suite: all suites must pass
  - Run latency benchmark: verify target P95 latency achieved
  - If all gates pass → submit for model-lifecycle promotion process
```

---

## Quality Gates

| Gate | Criterion | Threshold | Blocking |
|---|---|---|---|
| G1 | Student capability score / Teacher capability score | ≥ 85% per capability | Yes |
| G2 | Alignment test suite pass rate | 100% (all suites) | Yes |
| G3 | P95 inference latency | ≤ target_latency_ms | Yes |
| G4 | Student vs. teacher output divergence on safety scenarios | KL < 0.1 | Yes |
| G5 | Hallucination rate (vs. teacher) | ≤ teacher rate + 5% | Yes |
| G6 | Cost per inference | ≤ target_cost_per_1k_tokens | No (advisory) |

---

## Distillation Run Record

```yaml
distillation_run:
  run_id: "DIST-20260507-001"
  teacher_model: "reasoning-cloud-001"
  student_model: "standard-local-distilled-001"
  target_capabilities: [code_generation, summarization, qa]

  dataset:
    total_examples: 125000
    examples_per_capability:
      code_generation: 50000
      summarization: 40000
      qa: 35000
    quality_filter_retention_rate: 0.82

  training:
    method: "response_distillation + soft_targets"
    temperature: 4
    alpha: 0.7
    epochs: 8
    final_validation_loss: 0.234

  evaluation:
    capability_score_ratios:
      code_generation: 0.89
      summarization: 0.93
      qa: 0.87
    alignment_pass: true
    p95_latency_ms: 1240
    target_latency_ms: 1500
    status: PROMOTED
```