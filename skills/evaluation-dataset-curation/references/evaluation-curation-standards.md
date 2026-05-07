# Evaluation Dataset Curation Standards Reference

## Evaluation Dataset Requirements

Unlike training datasets, evaluation datasets have stricter requirements:

| Requirement | Training Dataset | Evaluation Dataset |
|---|---|---|
| Human validation | Sample (≥ 5%) | Full (100%) |
| Contamination check | Best effort | Mandatory — blocks release |
| Ground truth quality | Model-generated acceptable | Human-verified only |
| Difficulty distribution | Task-appropriate | Stratified across all difficulty levels |
| Adversarial examples | Optional | Required (≥ 10% of items) |
| Anti-gaming variants | Optional | Required (≥ 3 variants per item) |
| Public disclosure | Allowed | Embargo until evaluation complete |

---

## Item Correctness Verification Protocol

### Level 1: Automated Verification (required for all items)

```
FOR each item i:
    # Step 1: Execute reference solution against test cases
    reference_result = execute(item.gold_solution, item.test_cases)
    ASSERT all(reference_result.passed)

    # Step 2: Check for degenerate items
    ASSERT item.difficulty_estimate != "trivially_easy"  # Random baseline < 50%
    ASSERT item.difficulty_estimate != "unsolvable"  # Expert baseline > 20%

    # Step 3: Uniqueness of correct answer
    IF item.item_type == "open_generation":
        ASSERT len(item.acceptable_answers) >= 1
        ASSERT item.rubric_is_deterministic  # Scoring is reproducible
```

### Level 2: Human Expert Verification (required for all items)

```
For each item, two independent expert annotators must:
  1. Confirm the question is unambiguous
  2. Independently solve the problem without looking at gold solution
  3. Confirm their independent solution matches gold solution
  4. Rate item difficulty: [easy | medium | hard | expert]
  5. Confirm the item is not from public benchmarks

  AGREEMENT REQUIRED:
    Both experts must solve correctly OR both must flag the item for revision.
    Disagreement → third expert arbitration → revise or discard item.
```

### Level 3: Cross-Model Calibration (required before release)

```
Run 3 models of known capability against the evaluation dataset:
  - nano_model: expected pass@1 ≈ 0.10-0.20
  - standard_model: expected pass@1 ≈ 0.45-0.60
  - reasoning_model: expected pass@1 ≈ 0.75-0.90

IF actual_scores outside expected ranges (± 0.15):
    FLAG items outside expected range for review
    Revise dataset difficulty calibration
```

---

## Anti-Gaming Requirements

### Variant Generation

For each canonical item, generate ≥ 3 surface variants:

```
Variant types (apply in order):
  V1: Variable renaming — same problem, different variable/function names
  V2: Domain transfer — isomorphic problem in different domain
  V3: Inverse problem — given output, find input
  V4: Constraint relaxation — remove or modify one constraint

Variant quality check:
  - Variant must have the same difficulty as canonical
  - Variant must have distinct surface form (< 60% token overlap)
  - Variant must have same gold solution structure (not just different answer)
```

### Contamination Check Protocol

```
STEP 1: n-gram overlap check
  FOR each item i:
    overlap_score = max_jaccard_similarity(
        item.prompt, public_benchmark_corpus, n=8  # 8-gram overlap
    )
    IF overlap_score > 0.30:
        FLAG as POTENTIALLY_CONTAMINATED

STEP 2: Semantic similarity check
  FOR flagged items:
    embedding_similarity = max_cosine_similarity(
        embed(item.prompt), embed(public_benchmark_items)
    )
    IF embedding_similarity > 0.90:
        DISCARD item (contaminated)

STEP 3: Model memorization test
  Run items against a model known to have memorized target benchmarks.
  IF pass@1 > expected_calibrated_pass_rate + 0.20:
    FLAG as LIKELY_MEMORIZED → discard

CONTAMINATION THRESHOLD: < 1% of items may show any overlap signal
```

---

## Evaluation Dataset Stratification Requirements

```yaml
stratification_requirements:
  difficulty:
    easy: 0.20 ± 0.05
    medium: 0.50 ± 0.10
    hard: 0.25 ± 0.05
    expert: 0.05 ± 0.02

  domain_coverage:
    # Must represent all domains in scope
    minimum_items_per_domain: 50

  adversarial_fraction:
    minimum: 0.10  # At least 10% adversarial or edge-case items
    adversarial_types: [prompt_injection, edge_case, ambiguous, misleading_context]

  demographic_balance:
    # For tasks involving people or social contexts
    gender_neutral_fraction: ≥ 0.50
    geographic_diversity: ≥ 3 cultural contexts represented
```

---

## Release Criteria

A dataset may be released for model evaluation when ALL of the following are met:

```
□ 100% of items human-verified by ≥ 2 expert annotators
□ Inter-annotator agreement κ ≥ 0.85
□ Contamination check passed: < 1% contaminated items
□ Cross-model calibration within expected ranges
□ Stratification requirements met
□ All anti-gaming variants generated and verified
□ Metadata complete: item count, difficulty distribution, domain coverage
□ License and usage terms documented
□ 90-day embargo on item details enforced post-release
```

---

## Evaluation Report Schema

```yaml
evaluation_dataset_card:
  dataset_id: "EVAL-CODE-COMPLEX-v1.0"
  version: "1.0.0"
  task_type: "code_generation_complex"
  release_date: "2026-05-07"
  embargo_expiry: "2026-08-05"

  size:
    total_items: 500
    adversarial_items: 55
    total_variants: 1500

  quality:
    human_verified: 500  # 100%
    expert_iaa_kappa: 0.88
    contamination_rate: 0.002  # 0.2%
    calibration_check: PASSED

  model_calibration:
    nano_model_pass_at_1: 0.12
    standard_model_pass_at_1: 0.51
    reasoning_model_pass_at_1: 0.82

  access_control:
    public: false
    authorized_users: ["benchmark-governance-committee"]
    item_details_embargoed: true
```