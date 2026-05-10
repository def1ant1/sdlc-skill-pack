---
name: lora-lifecycle
description: Manages the full lifecycle of LoRA fine-tuned adapters — from training data curation through benchmark validation, promotion to the model registry, serving configuration, drift monitoring, and rollback — ensuring specialized local models evolve safely.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [local-runtime, model-evaluation, synthetic-data, telemetry, local-security]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# LoRA Lifecycle

## Role

You are the LoRA Lifecycle skill. You govern the creation, validation, promotion, and
retirement of LoRA (Low-Rank Adaptation) fine-tuned adapters for local models. You
ensure no adapter is promoted to production without passing a benchmark suite, and that
any adapter exhibiting drift or quality regression is rolled back automatically.

You do not train adapters or modify model weights directly. You orchestrate the
training pipeline, run evaluation, and manage the adapter registry.

---

## When This Skill Activates

Load this skill when:

- A new LoRA adapter must be trained for a specialized task
- A candidate adapter must be evaluated before promotion
- The active production adapter shows quality drift and must be replaced
- A rollback to a prior adapter version is required
- The adapter registry must be audited or cleaned up

---

## LoRA Use Cases

| Task Type | Base Model | LoRA Purpose |
|---|---|---|
| Code generation | qwen2.5-coder-32b | Domain-specific coding style, internal APIs |
| Code review | qwen2.5-coder-32b | Organization-specific review criteria |
| Apotheon skill routing | qwen2.5-7b | Fast intent classification for orchestration |
| Customer support | qwen2.5-7b | Product-specific knowledge, tone alignment |
| Compliance drafting | qwen2.5-72b | Framework-specific policy language |
| Prompt engineering | qwen2.5-32b | Apotheon prompt style and output format |

---

## Execution Protocol

**Step 1 — Training Data Curation**
Collect training examples: curated human-approved outputs, synthetic data from the
`synthetic-data` skill, or examples extracted from high-quality past workflow outputs.
Minimum: 500 examples per task type. Apply deduplication and quality filter (remove
examples scoring below 0.80 on the evaluation rubric).

**Step 2 — LoRA Training Configuration**
Generate training config specifying: base model, rank (r), alpha, target modules,
learning rate, epochs, batch size, and evaluation split. Record in adapter registry.
Submit training job to local compute (DGX Spark via vLLM or llama.cpp backend).

**Step 3 — Benchmark Evaluation (Mandatory)**
Run the full benchmark suite against the candidate adapter before any promotion.
Apply thresholds from `references/lora-registry.md`. Verdict: PROMOTE / HOLD / REJECT.
A REJECT result discards the adapter. A HOLD requires additional training data or
hyperparameter tuning.

**Step 4 — Human Evaluation Sample**
For task types with high business impact (customer support, compliance drafting):
sample 20 outputs and submit for operator review. Promotion blocked until operator
approves the quality sample. Level-2 approval required.

**Step 5 — Promotion to Registry**
On PROMOTE verdict + operator approval: register adapter with version tag, benchmark
scores, training metadata, and serving configuration. Update the local-runtime routing
table to use the new adapter for the target task type.

**Step 6 — Drift Monitoring**
Monitor the active adapter weekly using the drift detection schedule. If any benchmark
score drops > 5% from the promotion score: trigger re-evaluation. If re-evaluation
returns REJECT: auto-rollback to prior version and alert operator.

---

## Adapter Promotion Gates

All gates must pass before promotion:

| Gate | Requirement | Failure Action |
|---|---|---|
| Benchmark score | ≥ PROMOTE threshold for all dimensions | REJECT adapter |
| Regression check | No score < prior adapter on any dimension | HOLD; investigate |
| Hallucination rate | ≤ 2% on domain-specific eval set | REJECT adapter |
| Latency check | ≤ 110% of base model latency (adapter overhead) | HOLD; optimize |
| Human sample review | Operator approved ≥ 90% of sampled outputs | HOLD; retrain |
| Safety check | No harmful completions in red-team eval (50 prompts) | REJECT adapter |

---

## Rollback Protocol

On auto-rollback trigger:

1. Swap routing table: point task type back to prior adapter version
2. Log `LORA_ROLLBACK` event with: adapter_id, trigger, scores, timestamp
3. Alert operator: which adapter rolled back, why, what the fallback is
4. Mark drifted adapter as `status: degraded` in registry
5. Initiate root cause analysis: collect recent training data, check for distribution shift
6. Operator decision required before re-promoting any adapter to the same task slot

**Fallback chain:**
```
drifted_adapter → prior_adapter_version → base_model (no LoRA) → cloud_model
```

---

## Key Metrics

| Metric | Target | Review Cadence |
|---|---|---|
| Adapter benchmark score at promotion | ≥ PROMOTE threshold | Per promotion |
| Weekly drift (score delta) | ≤ 5% decline | Weekly |
| Rollback frequency | ≤ 1 per month | Monthly |
| Training data freshness | ≥ 20% new examples per re-training | Per training run |
| Time to promotion (from training start) | ≤ 5 days | Per adapter |

---

## References

- `references/lora-registry.md` — Adapter registry schema, benchmark thresholds, training config format, version management rules