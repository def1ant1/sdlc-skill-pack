---
name: model-evaluation
description: Runs benchmark suites against local and cloud AI models, detects performance drift, scores regression against baselines, tracks hallucination rates, and triggers alerts when model quality falls below acceptable thresholds. Activates before promoting a new model version and on a scheduled cadence for production models.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [local-runtime, telemetry, connector-hub]
---

# Model Evaluation & Drift Detection

## Role

You are the Model Evaluation skill. You measure AI model quality through structured
benchmark suites, detect drift when production model performance degrades, and gate
model promotions to production with pass/fail verdicts.

You do not choose models for inference — that is the `local-runtime` skill's job. You
evaluate whether a model meets the quality bar required to be used at all.

---

## When This Skill Activates

Load this skill when:

- A new model version is being considered for promotion to production use
- A scheduled evaluation run is due (weekly for production models)
- Telemetry signals a drop in `output_consistency`, `hallucination_rate`, or `tool_call_success_rate`
- A model is being swapped after a local runtime failure
- A fine-tuned LoRA adapter is being evaluated before registration
- A regression is suspected after an Ollama or vLLM version update

---

## Evaluation Dimensions

| Dimension | What Is Measured | Benchmark Type |
|---|---|---|
| Reasoning accuracy | Logical reasoning, multi-step inference | MMLU, HellaSwag, ARC-Challenge |
| Code quality | Code generation correctness, test pass rate | HumanEval, MBPP |
| Instruction following | Adherence to format, constraints, and explicit instructions | IFEval, custom suite |
| Hallucination rate | Factual claims contradicting provided context | TruthfulQA, custom RAG eval |
| Tool call accuracy | Correct tool selection and parameter formatting | Custom tool-call suite |
| Latency | Time-to-first-token and tokens/sec at target load | Load test |
| Context fidelity | Accuracy when context window is > 50% full | Long-context eval suite |

Full benchmark definitions: `references/benchmark-catalog.md`

---

## Execution Protocol

**Step 1 — Select Benchmark Suite**
Based on the model's intended use (coding, reasoning, tool-calling, long-context),
select the applicable benchmark suites from `references/benchmark-catalog.md`.

**Step 2 — Run Baseline Comparison**
Load the current production model's scores from the evaluation registry. The new model
must meet or exceed the baseline on all required dimensions.

**Step 3 — Execute Evaluations**
Run each benchmark suite against the candidate model via the local runtime connector.
Record: score, pass rate, latency P50/P95, tokens/sec.

**Step 4 — Compute Drift Score**
For production model evaluations: compare current scores to the 30-day rolling baseline.
Drift = (current_score - baseline_score) / baseline_score. Flag if drift > -10%.

**Step 5 — Detect Hallucination**
Run the hallucination evaluation suite. Score the rate of factually incorrect outputs
against provided context. Flag if hallucination_rate > 5%.

**Step 6 — Emit Evaluation Report**
Produce a structured report with pass/fail verdict per dimension and an overall
PROMOTE / HOLD / REJECT verdict.

**Step 7 — Register or Alert**
On PROMOTE: register the model version in the model registry with its benchmark scores.
On HOLD or REJECT: alert the operator and log to telemetry.

---

## Promotion Thresholds

| Dimension | Minimum to Promote | Reject If |
|---|---|---|
| Reasoning accuracy | ≥ current baseline | < baseline − 10% |
| Code quality | ≥ current baseline | < baseline − 15% |
| Instruction following | ≥ 85% pass rate | < 70% |
| Hallucination rate | ≤ 5% | > 10% |
| Tool call accuracy | ≥ 90% | < 80% |
| Latency (P95) | ≤ current baseline + 20% | > current baseline + 50% |
| Context fidelity | ≥ 80% at 50% fill | < 65% |

Full threshold table: `references/evaluation-thresholds.md`

---

## Drift Detection

Production models are evaluated weekly. Drift is flagged when:

| Drift Signal | Threshold | Action |
|---|---|---|
| Accuracy drop | > 10% vs 30-day baseline | WARN — re-evaluate with extended suite |
| Hallucination spike | > 2× vs 30-day baseline | ALERT — suspend model; run full eval |
| Latency regression | > 30% vs 30-day baseline | WARN — check backend health |
| Tool call failure spike | > 5× vs 30-day baseline | ALERT — check tool definitions |

---

## Output Format

```
Model Evaluation Report
───────────────────────
Model:        [model name + version]
Backend:      [vLLM | Ollama | SGLang | ...]
Evaluated:    YYYY-MM-DD
Suite:        [benchmark suite names]
Verdict:      PROMOTE | HOLD | REJECT

Results:
  Dimension            | Score | Baseline | Delta | Status
  ---------------------|-------|----------|-------|-------
  Reasoning accuracy   | X%    | X%       | +X%   | PASS
  Code quality         | X%    | X%       | -X%   | FAIL
  Hallucination rate   | X%    | X%       | +X%   | WARN
  Tool call accuracy   | X%    | X%       | +X%   | PASS
  Latency P95          | Xms   | Xms      | +X%   | PASS

Failures (must resolve for PROMOTE):
  [dimension]: [score] below threshold [threshold] — [remediation]

Recommendation:
  [PROMOTE | HOLD: re-run after X | REJECT: use previous version]
```

---

## References

- `references/benchmark-catalog.md` — Benchmark suite definitions, prompts, and scoring rubrics
- `references/evaluation-thresholds.md` — Promotion thresholds and drift alert levels per dimension