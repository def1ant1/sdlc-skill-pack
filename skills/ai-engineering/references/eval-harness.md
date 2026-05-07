# Evaluation Harness

## Overview

Every AI feature requires an evaluation suite before production deployment. This
document defines the evaluation harness structure, metric definitions, quality floors,
and the evaluation-to-deployment gate.

---

## Evaluation Suite Structure

```
evals/
  <feature-name>/
    suite.yaml          # eval definition: tasks, metrics, thresholds
    dataset/
      golden.jsonl      # golden examples (input → expected output)
      adversarial.jsonl # adversarial/edge cases
    results/
      <date>-<model>-results.json
```

### suite.yaml Format

```yaml
eval_id: "EVAL-<feature>-<version>"
feature: "<feature name>"
model_under_test: "<model id>"
prompt_version: "<prompt_id>@<version>"
dataset:
  golden: "dataset/golden.jsonl"
  adversarial: "dataset/adversarial.jsonl"
metrics:
  - name: accuracy
    type: exact_match | rouge | llm_judge | custom
    weight: 0.4
    floor: 0.85          # minimum to pass
  - name: hallucination_rate
    type: llm_judge
    weight: 0.3
    ceiling: 0.05        # maximum to pass (lower is better)
  - name: latency_p95_ms
    type: performance
    weight: 0.1
    ceiling: 2000
  - name: cost_per_1k
    type: cost
    weight: 0.2
    ceiling: 0.50
thresholds:
  overall_score: 0.80   # weighted average must exceed this to PROMOTE
  hard_fails:           # any failure here blocks promotion regardless of score
    - hallucination_rate > 0.10
    - accuracy < 0.70
```

---

## Metric Definitions

### Accuracy (Exact Match)

For structured outputs: compare model output to golden answer exactly after
normalization (lowercase, strip whitespace, normalize numbers).

`accuracy = correct / total`

### ROUGE-L (Text Similarity)

For summarization and paraphrase tasks: compute longest common subsequence overlap.

`rouge_l = lcs_length / reference_length`

### LLM-as-Judge

For tasks where exact match is insufficient: use a separate LLM call to evaluate
quality on a 1–5 scale. Use a calibrated judge prompt with rubric.

```
Judge prompt: "Rate the following response on [criteria] from 1 (very poor) to 5
(excellent). Respond with only a number."
Score normalization: (score - 1) / 4 → [0.0, 1.0]
```

Minimum judge agreements (self-consistency): run 3 judge calls; take median.

### Hallucination Rate

Proportion of responses containing claims not supported by the provided context
or that contradict known ground truth.

`hallucination_rate = hallucinated_responses / total_responses`

---

## Promotion Gate

| Result | Condition | Action |
|---|---|---|
| PROMOTE | Overall ≥ threshold AND no hard fails | Deploy to staging; log eval report |
| HOLD | Overall ≥ 0.70 AND no hard fails AND < 3 metrics at risk | Investigate weak metrics; re-eval after fix |
| REJECT | Overall < 0.70 OR any hard fail triggered | Block deployment; root cause analysis required |

All eval results must be logged with: `eval_id`, `model`, `prompt_version`, `dataset_hash`,
`scores`, `decision`, and `evaluator`. Immutable audit log entry required.

---

## Regression Testing

Before any prompt version change in production:

1. Run eval suite against both old and new prompt versions
2. Compute delta for all metrics
3. Flag any metric that degrades > 5% as a regression
4. A regression in a hard-fail metric blocks promotion regardless of overall score
5. Post comparison report to hitl-dashboard for Level-2 approval

---

## Adversarial Test Cases

Every eval suite must include adversarial cases covering:

| Category | Examples |
|---|---|
| Prompt injection | User input attempting to override system prompt |
| Boundary inputs | Empty input, max-length input, non-ASCII |
| Hallucination triggers | Questions about facts not in context |
| Jailbreak attempts | Requests to ignore safety instructions |
| Ambiguous instructions | Underspecified inputs requiring clarification |