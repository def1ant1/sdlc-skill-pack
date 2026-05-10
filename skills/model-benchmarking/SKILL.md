---
name: model-benchmarking
description: Executes standardized capability benchmarks against AI models, produces scored evaluation reports, and tracks performance trends across model versions and fine-tuning iterations.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [benchmark-factory, model-lifecycle, synthetic-data, telemetry]

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

## Role

Model benchmarking specialist. Runs registered evaluation benchmarks against target models,
computes per-capability scores, aggregates results into model scorecards, and maintains
performance trend history for model comparison and promotion gate decisions.

## Activation Triggers

- Model promotion gate evaluation required
- New benchmark registered requiring baseline evaluation
- Periodic model quality monitoring cycle
- Fine-tuning run completed requiring capability validation

## Execution Protocol

1. **Select benchmark suite**: Retrieve applicable benchmarks from benchmark-factory based on
   model capabilities and promotion gate requirements.

2. **Configure evaluation run**: Set model endpoint, batch size, temperature (0.0 for eval),
   and per-benchmark pass criteria.

3. **Execute benchmark**: Run model against each benchmark case; collect raw outputs for
   scoring; track latency and token usage per case.

4. **Score responses**: Apply benchmark-specific scoring function (exact match, F1, BLEU,
   LLM-as-judge, or custom rubric) to each case; aggregate to per-benchmark scores.

5. **Compute capability profile**: Aggregate scores across benchmarks into a capability profile;
   compare to prior version and gate thresholds.

6. **Produce evaluation report**: Per-benchmark scores, capability profile radar chart, trend
   vs. prior versions, pass/fail against gate thresholds, and promotion recommendation.

## Output Format

Model evaluation report with: per-benchmark scores, aggregate capability profile, pass/fail
gate status, performance trend over last N versions, and promotion or block recommendation.

## References

- `references/evaluation-methodology.md` — scoring functions per benchmark type, gate threshold definitions, trend analysis methodology