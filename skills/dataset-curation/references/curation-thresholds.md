# Dataset Curation Thresholds Reference

## Quality Filter Thresholds

### Text Quality Filters

| Filter | Metric | Threshold | Action on Violation |
|---|---|---|---|
| Minimum length | character_count | ≥ 100 characters | REMOVE |
| Maximum length | character_count | ≤ 100,000 characters | TRUNCATE or REMOVE |
| Language detection | language_confidence | ≥ 0.90 for target language | REMOVE |
| Perplexity filter | ppl_score (KenLM) | ≤ 1000 for English | REMOVE |
| Repetition filter | unique_3gram_ratio | ≥ 0.30 | REMOVE |
| Toxicity filter | toxicity_score | ≤ 0.70 | REMOVE (training data) |
| PII filter | pii_detected | false | REDACT or REMOVE |
| HTML artifact filter | html_tag_ratio | ≤ 0.05 | CLEAN or REMOVE |
| Numeric ratio | digit_ratio | ≤ 0.60 | REMOVE (likely data tables) |

### Code Quality Filters

| Filter | Metric | Threshold | Action on Violation |
|---|---|---|---|
| Syntax validity | parse_error | false | REMOVE |
| Minimum line count | line_count | ≥ 5 | REMOVE |
| Maximum line count | line_count | ≤ 5000 | REMOVE |
| Comment ratio | comment_line_ratio | 0.05–0.40 | FLAG |
| Identifier quality | avg_identifier_length | ≥ 3 characters | REMOVE |
| License compliance | license_type | NOT IN blocked_licenses | REMOVE |

### Instruction-Response Quality Filters

| Filter | Metric | Threshold | Action on Violation |
|---|---|---|---|
| Instruction clarity | clarity_score | ≥ 0.70 | REMOVE |
| Response relevance | relevance_score | ≥ 0.80 | REMOVE |
| Response completeness | completeness_score | ≥ 0.75 | REMOVE |
| Factual consistency | factual_score | ≥ 0.85 | REMOVE (for factual tasks) |
| Instruction-response length ratio | ratio | 0.5–20× | FLAG |

---

## Deduplication Thresholds

### Exact Deduplication

```
exact_dedup_strategy: SHA-256 hash of normalized content
normalization:
  - lowercase
  - collapse whitespace
  - strip HTML
  - sort punctuation variants (—, –, -)

retention_policy: KEEP_FIRST occurrence (by timestamp)
```

### Near-Duplicate Detection (MinHash LSH)

```
minhash_config:
  n_permutations: 256
  band_size: 8  # Bands of 8 = ~32 bands
  jaccard_threshold: 0.80  # Items with Jaccard similarity ≥ 0.80 are near-duplicates

# Jaccard similarity ≥ threshold → mark as near-duplicate
# Retention: keep item with highest quality_score; remove rest
```

### Semantic Deduplication

```
embedding_model: "text-embedding-3-large"
similarity_threshold: 0.95  # Cosine similarity ≥ 0.95 = semantic duplicate

# Applied AFTER exact and near-duplicate dedup
# More expensive — run on remaining corpus only
```

---

## Annotation Consistency Thresholds

| Annotation Type | Agreement Metric | Minimum Threshold | Resolution |
|---|---|---|---|
| Binary classification | Cohen's κ | ≥ 0.80 | Adjudication by third annotator |
| Multi-class | Fleiss' κ | ≥ 0.70 | Majority vote ≥ 3 annotators |
| Rating scale | Krippendorff's α | ≥ 0.67 | Average with outlier removal |
| Span labeling | F1 (annotator pairs) | ≥ 0.85 | Merge with majority vote |
| Ranking | Kendall's τ | ≥ 0.60 | Borda count aggregation |

**When IAA falls below threshold:** Flag for annotator calibration session before continuing.

---

## Curation Pipeline Quality Gates

```
GATE 1 — Raw ingestion:
  total_items_ingested: N
  IF N < minimum_corpus_size:
    WARN "Corpus may be insufficient for target task"

GATE 2 — After quality filtering:
  retention_rate = items_after_filter / N
  ASSERT retention_rate >= 0.40  # Less than 40% retention = filter tuning needed
  ASSERT items_after_filter >= minimum_training_size[task_type]

GATE 3 — After deduplication:
  dedup_rate = (items_before - items_after) / items_before
  WARN IF dedup_rate > 0.60  # High duplication suggests poor data source diversity

GATE 4 — After annotation:
  ASSERT all_annotated_items_IAA >= iaa_threshold[annotation_type]
  ASSERT annotation_coverage >= 0.95  # 95% of items have annotations

GATE 5 — Final split validation:
  ASSERT no_overlap(train, validation, test)
  ASSERT test_size >= 0.10 × total  # Minimum 10% for test
  ASSERT class_balance_ratio(train) within 0.15 of class_balance_ratio(full_dataset)
```

---

## Dataset Card Required Fields

```yaml
dataset_card:
  name: "SDLC Code Generation v1.0"
  version: "1.0.0"
  task_type: "code_generation_complex"
  language: ["en", "python", "javascript"]

  size:
    train: 45000
    validation: 5000
    test: 5000
    total: 55000

  quality_metrics:
    retention_rate_after_filter: 0.67
    deduplication_rate: 0.12
    annotation_iaa_kappa: 0.83
    human_validation_sample_size: 500
    human_validation_accuracy: 0.91

  known_limitations:
    - "Underrepresents Rust and Go codebases (< 5% of corpus)"
    - "Instructions skew toward web development tasks"

  license: "CC BY 4.0"
  pii_status: "Fully redacted — validated by pii-detection skill"
```