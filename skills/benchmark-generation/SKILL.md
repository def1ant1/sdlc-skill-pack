---
name: benchmark-generation
description: Generates calibrated benchmark datasets for AI capability evaluation, including adversarial edge cases, difficulty-stratified samples, and contamination-resistant variants, with full provenance documentation.
metadata:
  version: "1.0.0"
  category: evaluation
  owner: platform
  maturity: alpha
  dependencies: [benchmark-factory, synthetic-dataset-generation, dataset-curation, telemetry]
---

## Role

Calibrated benchmark dataset generator for the benchmarking platform. Produces evaluation
datasets that accurately measure specific AI capabilities through difficulty stratification,
adversarial case inclusion, and contamination-resistant construction — each with full
provenance documentation enabling reproducible evaluation.

## Activation Triggers

- Benchmark-factory registers a new capability domain requiring a benchmark dataset
- Model-lifecycle requires a benchmark for a novel capability before promotion
- Evaluation-dataset-curation identifies gaps in an existing benchmark's coverage
- Operator requests a new benchmark for a specific evaluation objective

## Execution Protocol

1. **Define benchmark specification**: Capture the target capability, evaluation objective,
   difficulty distribution target, adversarial case ratio, and any contamination constraints
   (known test set sources to avoid).

2. **Generate core items**: Produce benchmark items at each difficulty level (Easy/Medium/Hard/Expert)
   in the specified distribution; ensure items unambiguously test the target capability.

3. **Generate adversarial cases**: Produce edge-case items targeting known model failure modes
   for the capability — distribution shift, negation handling, long-context, and compositional
   reasoning challenges.

4. **Apply contamination guards**: Check all generated items against known public test sets
   using similarity detection; replace contaminated items; document any known contamination risks.

5. **Calibrate difficulty**: Validate difficulty labels by running items against reference
   models at known capability levels; adjust labels based on empirical pass rates.

6. **Issue benchmark record**: Register the benchmark in the benchmark-factory with version,
   provenance, item statistics, and calibration metadata.

## Output Format

Benchmark record with: `benchmark_id`, `capability`, `version`, `item_count` (total and by
difficulty tier), `adversarial_ratio`, `contamination_check_status`, `calibration_metrics`
(empirical difficulty distribution), and `provenance` documentation.

## References

- `references/benchmark-spec-format.md` — benchmark specification schema, difficulty calibration protocol, contamination detection thresholds