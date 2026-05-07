# Uncertainty Thresholds Reference

## Confidence Scoring Methods

### Method 1: Logit Entropy (Token-Level Uncertainty)

**How it works:** Measures the Shannon entropy of the model's output token probability
distribution. Low entropy = high confidence; high entropy = low confidence.

```
entropy = -Σ p(token) × log2(p(token))
normalized_confidence = 1 - (entropy / log2(vocab_size))
```

**When to use:** Available when model returns logprobs. Best for short, discrete outputs
(classification, single-token answers).

**Availability:** OpenAI API (logprobs=True), local models via vLLM or llama.cpp.

---

### Method 2: Self-Consistency (Multi-Sample Agreement)

**How it works:** Generate N samples (N=5–10) at temperature > 0; measure agreement
among samples. High agreement = high confidence.

```
consistency_score = (most_common_answer_count / N)
```

**When to use:** When logprobs are unavailable. Works best for reasoning chains and
factual questions where the correct answer is stable across samples.

**Cost:** N× inference cost. Use N=5 for standard tasks; N=10 for high-stakes decisions.

---

### Method 3: Embedding Distance from Training Distribution

**How it works:** Compute the embedding of the input; measure distance to the nearest
training-distribution exemplars in an embedding index. Far from training distribution
= likely out-of-distribution (OOD) = lower confidence.

```
ood_score = cosine_distance(query_embedding, knn_neighbor_embeddings)
confidence = 1 - ood_score
```

**When to use:** Detecting OOD inputs where the model may hallucinate due to lack of
training coverage. Requires a pre-built embedding index of training distribution samples.

---

### Method 4: Stated Uncertainty (Model Self-Report)

**How it works:** Prompt the model to explicitly state its confidence after providing
an answer. Calibration varies by model — requires historical calibration check.

```
Prompt addition: "After your answer, state your confidence as HIGH, MEDIUM, or LOW."
```

**When to use:** Fallback when other methods are unavailable. Calibrate against held-out
data before trusting self-reported confidence.

---

## Per-Tier Confidence Thresholds

| Capability Tier | Confidence Threshold for Escalation | Method Priority |
|---|---|---|
| Nano | Escalate if < 0.70 | Self-consistency (N=3) |
| Micro | Escalate if < 0.75 | Logit entropy → Self-consistency |
| Standard | Escalate if < 0.80 | Logit entropy → Self-consistency |
| Advanced | Escalate if < 0.85 | Logit entropy |
| Reasoning | Never escalates (highest tier) | N/A |

**Escalation direction:** Always escalate to the next higher tier. Reasoning tier
outputs with low confidence are flagged as GENUINELY_AMBIGUOUS and returned with
uncertainty annotation.

---

## Aleatoric vs. Epistemic Uncertainty Classification

| Uncertainty Type | Definition | Resolution | Detection Signal |
|---|---|---|---|
| Aleatoric | Inherent ambiguity in the task; more information or better model won't help | Cannot be resolved — annotate output | Low self-consistency AND logit entropy high EVEN for Reasoning tier |
| Epistemic | Model capability gap for this type of task | Resolved by escalating to a more capable model | Low confidence for lower tiers; higher tiers are more confident |

**Classification heuristic:**
- If escalating from Standard to Advanced improves confidence by > 15 points → EPISTEMIC
- If escalating to Reasoning and confidence remains < 0.75 → ALEATORIC
- Apply "oracle test": would a perfect model be confident? If not, it's aleatoric.

---

## Escalation Loop Prevention Rules

To prevent infinite escalation cycles:

1. Each request carries a `max_escalations` counter (default: 2)
2. Counter is decremented on each escalation attempt
3. At counter = 0: return result with uncertainty annotation; no further escalation
4. A request already at the Reasoning tier cannot be escalated further
5. Escalation cooldown: if the same request has been escalated in the past 60 seconds,
   return the highest-tier result obtained so far

---

## Uncertainty Annotation Format

When a request returns GENUINELY_AMBIGUOUS:

```yaml
inference_result:
  request_id: "REQ-WF042-STEP3"
  model_id: "reasoning-cloud-001"
  output: "..."

  uncertainty:
    type: GENUINELY_AMBIGUOUS
    confidence_score: 0.62
    confidence_method: "self-consistency(N=10)"
    escalations_attempted: 2
    escalation_path: ["standard-local → advanced-local → reasoning-cloud"]
    annotation: "This question may have multiple valid answers depending on
                  interpretation. The provided answer reflects the most common
                  response across 10 samples; consider human review for
                  high-stakes use of this output."
    recommendation: "human_review_recommended"
```