# Evaluation Thresholds

Used by `core/model-evaluation/SKILL.md` to define per-dimension promotion thresholds,
drift alert levels, and verdict rules for model evaluation.

---

## Promotion Thresholds

A model receives a PROMOTE verdict only when ALL required dimensions pass.

| Dimension | Benchmark | Minimum to PROMOTE | HOLD Condition | REJECT Condition |
|---|---|---|---|---|
| Reasoning accuracy | MMLU | ≥ current baseline | 5–10% below baseline | > 10% below baseline |
| Code quality | HumanEval | ≥ current baseline | 10–15% below baseline | > 15% below baseline |
| Instruction following | IFEval | ≥ 85% instruction accuracy | 75–84% | < 75% |
| Hallucination rate | TruthfulQA + RAG suite | ≤ 5% hallucination | 5–10% | > 10% |
| Tool call accuracy | Tool-Call Suite | ≥ 90% combined | 80–89% | < 80% |
| Latency P95 | Load test | ≤ baseline + 20% | baseline + 20–50% | > baseline + 50% |
| Context fidelity | Long-Context Suite | ≥ 80% at 50% fill | 65–79% | < 65% |
| Orchestration accuracy | Orchestration Benchmark | ≥ 90% | 80–89% | < 80% |

---

## Verdict Rules

| Verdict | Condition | Action |
|---|---|---|
| PROMOTE | All required dimensions PASS | Register model; update local-runtime routing |
| HOLD | 1–2 dimensions in HOLD range; none in REJECT | Re-evaluate after 24h; do not promote yet |
| REJECT | Any dimension in REJECT range | Do not promote; alert operator; use previous version |

---

## Drift Detection Thresholds

For production models evaluated on the weekly schedule:

| Drift Signal | Warn Threshold | Alert Threshold | Alert Action |
|---|---|---|---|
| MMLU accuracy drop | > 5% from 30-day avg | > 10% from 30-day avg | Suspend & re-evaluate |
| HumanEval pass@1 drop | > 8% from 30-day avg | > 15% from 30-day avg | Suspend & re-evaluate |
| Hallucination spike | > 1.5× 30-day avg | > 2× 30-day avg | Immediate suspend |
| Tool call failure spike | > 2× 30-day avg | > 5× 30-day avg | Immediate suspend |
| TTFT regression | > 20% from 30-day avg | > 50% from 30-day avg | Check backend health |
| Throughput drop | > 15% from 30-day avg | > 30% from 30-day avg | Check VRAM pressure |

---

## Model-Size Adjusted Baselines

Thresholds are relative to the current production baseline, not absolute. However,
these floor values apply regardless of baseline — a model below the floor is never
promoted regardless of prior baseline:

| Model Size | MMLU Floor | HumanEval Floor | IFEval Floor |
|---|---|---|---|
| ≤ 7B | 55% | 45% | 70% |
| 8B–14B | 62% | 55% | 75% |
| 15B–32B | 70% | 65% | 80% |
| 33B–72B | 76% | 72% | 85% |
| > 72B | 80% | 78% | 87% |

---

## Version Registry Format

After a PROMOTE verdict, register the model with:

```yaml
model_registry_entry:
  model_id: [model name + quantization]
  version: [HuggingFace model version or Ollama tag]
  backend: [vLLM | Ollama | SGLang | llama.cpp]
  promoted_at: "YYYY-MM-DD"
  promoted_by: model-evaluation-skill
  benchmark_scores:
    mmlu: X%
    humaneval: X%
    ifeval: X%
    hallucination_rate: X%
    tool_call_accuracy: X%
    latency_p95_ms: X
  replaces: [previous model_id]
  status: active
```