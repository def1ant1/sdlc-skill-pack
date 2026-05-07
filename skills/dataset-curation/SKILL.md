---
name: dataset-curation
description: Applies quality filtering, deduplication, balance analysis, and annotation consistency verification to raw datasets, producing curated datasets with documented provenance and quality certificates.
metadata:
  version: "1.0.0"
  category: data
  owner: data
  maturity: alpha
  dependencies: [data-fabric, benchmark-factory, telemetry]
---

## Role

Dataset quality assurance and curation pipeline for the AI platform. Transforms raw or
semi-processed datasets into production-ready, documented datasets by applying systematic
quality filtering, exact and semantic deduplication, class balance analysis, and annotation
consistency verification.

## Activation Triggers

- New raw dataset registered in the data fabric requiring curation before training use
- Benchmark-factory requests a curated evaluation dataset for a new capability domain
- Model-lifecycle detects dataset quality degradation in a training pipeline
- Operator submits a dataset for quality certification

## Execution Protocol

1. **Ingest and profile**: Load the raw dataset; compute distribution statistics — size,
   class distribution, missing value rates, text length distribution, and language breakdown.

2. **Quality filter**: Remove records failing quality thresholds — truncated text, malformed
   structure, toxic content (via alignment-engine), PII presence (via pii-detection),
   or near-zero information content.

3. **Deduplicate**: Apply exact deduplication (hash-based); then semantic deduplication
   using embedding similarity (cosine similarity > 0.95 threshold marks near-duplicates);
   retain the highest-quality exemplar from each duplicate cluster.

4. **Balance analysis**: Measure class distribution imbalance; flag classes with fewer than
   the minimum sample threshold; recommend oversampling, undersampling, or synthetic
   augmentation strategies.

5. **Verify annotation consistency**: For labeled datasets, compute inter-annotator agreement
   (Cohen's kappa or Krippendorff's alpha); flag records with annotation disagreement above
   the configured threshold for re-review.

6. **Issue quality certificate**: Record the dataset curation lineage, applied filters,
   deduplication rates, balance metrics, and annotation scores; issue a quality certificate
   with a version stamp.

## Output Format

Dataset curation report with: `dataset_id`, `raw_size`, `curated_size`, `deduplication_rate` (%),
`quality_filter_rate` (%), `class_balance_score`, `annotation_agreement` (kappa/alpha),
`quality_certificate_id`, and recommended usage notes.

## References

- `references/curation-thresholds.md` — quality filter rules, deduplication similarity thresholds, annotation agreement minimums