---
name: benchmark-factory
description: Creates, curates, and governs evaluation benchmarks and synthetic datasets for model assessment, capability measurement, and continuous quality monitoring across the AI platform.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [synthetic-data, model-evaluation, data-fabric, knowledge-graph]

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

Benchmark lifecycle manager for the AI platform. Designs evaluation datasets, generates
synthetic test cases, governs benchmark versioning, tracks evaluation results over time,
and maintains the benchmark registry as the authoritative source for model quality assessment.

## Activation Triggers

- New model capability requires evaluation benchmark
- Existing benchmark shows distribution shift or staleness
- Model promotion gate requires benchmark evidence
- Capability regression suspected requiring targeted benchmark

## Execution Protocol

1. **Define benchmark specification**: Specify capability area, difficulty distribution (easy/
   medium/hard ratio), input/output types, scoring metric, and promotion pass threshold.

2. **Generate test cases**: Invoke synthetic-dataset-generation to produce diverse cases
   spanning the full difficulty distribution; include edge cases and adversarial cases.

3. **Curate dataset quality**: Apply quality filters — correctness verification, deduplication,
   near-duplicate removal, annotation consistency check.

4. **Balance distribution**: Sample to achieve specified difficulty balance; verify coverage
   across all target capability sub-areas.

5. **Version and register**: Assign benchmark-id, version number, and full metadata; write
   to benchmark registry with generation lineage and quality metrics.

6. **Execute and record evaluation**: Run model against benchmark; store per-case scores;
   compute aggregate metrics; trend against prior versions.

## Output Format

Benchmark registration confirmation with benchmark-id, size, distribution stats, and quality
metrics; or evaluation report with per-case scores, aggregate capability profile, and pass/fail.

## References

- `references/benchmark-governance.md` — benchmark versioning policy, difficulty calibration, evaluation reproducibility requirements