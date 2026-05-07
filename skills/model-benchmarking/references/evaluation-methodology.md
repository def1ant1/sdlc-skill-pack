# Evaluation Methodology Reference

## Evaluation Framework Overview

Model benchmarking follows a structured evaluation cycle:

```
1. Define evaluation scope (capabilities, task types, domains)
2. Select evaluation datasets (certified benchmarks + task-specific)
3. Run evaluations with standardized protocols
4. Score with primary + secondary metrics
5. Analyze results (capability profile, failure modes)
6. Compare across models and versions
7. Document and publish in model card
```

---

## Evaluation Protocol Standards

### Protocol 1: Zero-Shot Evaluation

**Use for:** Measuring base capability without examples.

```yaml
zero_shot_protocol:
  prompt_format: "{instruction}\n\nAnswer:"
  system_prompt: null  # No system prompt unless testing system prompt following
  temperature: 0.0
  max_tokens: 2048
  n_samples: 1  # Deterministic
  evaluation_metric: "exact_match" | "f1" | "pass@1"
```

### Protocol 2: Few-Shot Evaluation

**Use for:** Measuring in-context learning ability.

```yaml
few_shot_protocol:
  n_shots: [0, 1, 3, 5, 10]  # Evaluate at multiple shot counts
  shot_selection: "random"  # random | balanced | difficulty_stratified
  shot_format: "Q: {question}\nA: {answer}\n\n"
  randomization: "fixed_seed_42 for reproducibility"
  evaluation_metric: "accuracy"

  reporting:
    - "Report at 0, 3, and 5-shot"
    - "Report learning curve slope"
```

### Protocol 3: Chain-of-Thought Evaluation

**Use for:** Assessing reasoning quality on complex tasks.

```yaml
cot_protocol:
  prompt_suffix: "Let's think step by step."
  temperature: 0.0  # For greedy CoT
  evaluate:
    - final_answer_accuracy
    - reasoning_coherence_score  # LLM-as-judge or rubric
    - intermediate_step_correctness  # If ground truth CoT available

  self_consistency_variant:
    temperature: 0.7
    n_samples: 10
    aggregation: "majority_vote"
    metric: "self_consistency_accuracy"
```

---

## Metric Definitions

### Classification Metrics

```python
# For classification tasks
accuracy = correct / total
precision = TP / (TP + FP)
recall = TP / (TP + FN)
f1 = 2 × (precision × recall) / (precision + recall)
macro_f1 = mean(f1 per class)  # Equal weight per class
weighted_f1 = weighted_mean(f1 per class, weight=class_frequency)
```

### Generation Metrics

```python
# Lexical overlap
bleu_4 = bleu_score(references, hypotheses, max_n=4)
rouge_l = rouge_l_score(references, hypotheses)

# Semantic similarity
bertscore_f1 = bertscore(references, hypotheses, model="microsoft/deberta-xlarge-mnli")

# Code-specific
pass_at_k = 1 - C(n-c, k) / C(n, k)  # n=samples, c=correct, k=budget

# LLM-as-judge (for open-ended generation)
judge_score = mean(judge_model.evaluate(output, rubric) for output in outputs)
judge_model = "claude-opus-4-6"  # Use highest-tier available
judge_rubric = "rate 1-10: {dimension}"
```

### Calibration Metrics

```python
# Expected Calibration Error
def ece(predictions, labels, n_bins=15):
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (predictions >= bins[i]) & (predictions < bins[i+1])
        if mask.sum() > 0:
            acc = labels[mask].mean()
            conf = predictions[mask].mean()
            ece += (mask.sum() / len(predictions)) * abs(acc - conf)
    return ece

# Target: ECE < 0.05 for well-calibrated model
```

---

## Capability Profile Matrix

Score each model on a standardized 0-100 scale per capability:

```yaml
capability_profile:
  model_id: "advanced-local-001"
  evaluation_date: "2026-05-07"

  capabilities:
    reasoning:
      mathematical: 72
      logical: 85
      causal: 78
      commonsense: 88

    language:
      reading_comprehension: 91
      summarization: 87
      translation: 82
      creative_writing: 76

    code:
      python_generation: 83
      javascript_generation: 79
      code_explanation: 90
      debugging: 81

    knowledge:
      world_knowledge: 84
      scientific: 79
      legal: 65
      medical: 70

    safety:
      alignment_score: 94
      refusal_accuracy: 96
      calibration_ece: 0.042

  aggregate_scores:
    overall: 81.4
    reasoning: 80.8
    language: 84.0
    code: 83.3
    knowledge: 74.5
    safety: 95.0
```

---

## Comparative Analysis Protocol

When comparing model versions or candidates:

```
COMPARISON PROTOCOL:
  1. Use identical evaluation sets (no contamination between runs)
  2. Run all models with identical inference parameters
  3. Report absolute scores AND delta vs. baseline
  4. Statistical significance testing:
       bootstrap_ci(scores_model_a, scores_model_b, n_bootstrap=10000)
       report if p < 0.05 (two-tailed)
  5. Regression detection:
       FOR each capability c:
         IF score_new < score_baseline - 2 points AND p < 0.05:
           FLAG as REGRESSION
       Any regression blocks promotion unless explicitly accepted

REPORTING:
  - Radar chart: capability profile comparison
  - Delta table: new vs. baseline per capability
  - Regression summary: capabilities that regressed
  - Improvement summary: capabilities that improved significantly
```

---

## Evaluation Run Record

```yaml
evaluation_run:
  run_id: "EVAL-20260507-ADV-001"
  model_id: "advanced-local-001"
  model_version: "3.2.0"
  baseline_model: "advanced-local-001-v3.1.0"
  run_date: "2026-05-07"
  evaluator: "model-benchmarking skill"

  datasets_used:
    - id: "EVAL-CODE-COMPLEX-v1.0"
      items: 500
    - id: "EVAL-REASONING-v2.0"
      items: 300
    - id: "EVAL-SAFETY-v1.0"
      items: 200

  regressions_detected: 0
  significant_improvements: 2  # code debugging (+3.1), calibration (+0.008 ECE)

  promotion_recommendation: APPROVE
  promotion_tier: "Advanced"
```