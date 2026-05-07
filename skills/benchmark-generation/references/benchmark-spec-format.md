# Benchmark Specification Format Reference

## Benchmark Package Structure

```
benchmark-<name>-v<version>/
├── metadata.yaml          # Benchmark identity and governance
├── items/
│   ├── item-001.yaml      # Individual test item
│   ├── item-002.yaml
│   └── ...
├── scoring/
│   ├── rubric.yaml        # Scoring rubric and thresholds
│   └── evaluation.py      # Deterministic scoring function (optional)
├── splits/
│   ├── train.txt          # Item IDs for training/calibration
│   ├── validation.txt     # Item IDs for validation
│   └── test.txt           # Item IDs for held-out evaluation
└── README.md              # Human-readable description
```

---

## metadata.yaml Schema

```yaml
benchmark:
  id: "BM-CODE-COMPLEX-001"
  name: "Complex Code Generation Benchmark"
  version: "1.0.0"
  task_type: "code_generation_complex"
  capability_tier: "Advanced"

  governance:
    created_by: "benchmark-generation skill"
    created_at: "2026-05-07T00:00:00Z"
    certified_by: null  # Set by benchmark-governance process
    certification_date: null
    lifecycle_stage: "DRAFT"  # DRAFT | REVIEW | CERTIFIED | DEPRECATED

  quality_metrics:
    total_items: 500
    items_human_validated: 0  # Updated by QA process
    inter_annotator_agreement: null
    difficulty_distribution:
      easy: 0.20
      medium: 0.50
      hard: 0.30
    domain_coverage: ["web", "systems", "ml", "data"]

  contamination_controls:
    internet_scrape_excluded: true
    training_data_overlap_checked: false  # Set after decontamination
    synthetic_generation_model: "reasoning-cloud-001"
    generation_date: "2026-05-07"
    embargo_period_days: 90  # Days before public release

  evaluation_protocol:
    metric_primary: "pass@1"
    metric_secondary: ["pass@5", "pass@10"]
    judge_model: null  # If LLM-as-judge, specify model
    deterministic_scoring: true
    execution_environment: "python3.11-sandbox"
```

---

## Item Schema (item-NNN.yaml)

```yaml
item:
  id: "BM-CODE-COMPLEX-001-0042"
  benchmark_id: "BM-CODE-COMPLEX-001"
  version: "1.0.0"

  content:
    prompt: |
      Implement a thread-safe LRU cache in Python with the following requirements:
      - Maximum capacity configurable at initialization
      - O(1) get and put operations
      - Thread-safe for concurrent read/write
      - Evict least recently used item when at capacity
    context: null  # Additional context documents if needed
    constraints:
      - "Must use only Python standard library"
      - "Must include type hints"
      - "Must pass all provided test cases"

  evaluation:
    type: "execution"  # execution | llm_judge | human | hybrid
    test_cases:
      - input: "cache = LRUCache(2); cache.put(1,'a'); cache.get(1)"
        expected_output: "'a'"
      - input: "cache.put(2,'b'); cache.put(3,'c'); cache.get(1)"
        expected_output: "-1"  # Key 1 evicted
    scoring_function: "all_tests_pass"  # all_tests_pass | partial_credit | rubric

  metadata:
    difficulty: "hard"
    domain: "systems"
    skills_tested: ["data_structures", "concurrency", "python"]
    created_at: "2026-05-07T00:00:00Z"
    human_validated: false
    gold_solution: null  # Added by human annotators

  anti_gaming:
    permutation_variants: 3  # Number of paraphrased variants generated
    surface_form_randomized: true
    variable_names_randomized: false
```

---

## Scoring Rubric Schema (rubric.yaml)

```yaml
rubric:
  benchmark_id: "BM-CODE-COMPLEX-001"
  scoring_type: "pass_at_k"

  pass_at_k:
    k_values: [1, 5, 10]
    formula: |
      pass@k = 1 - C(n-c, k) / C(n, k)
      where n = total_samples, c = correct_samples
    correctness_criterion: "all_test_cases_pass"

  capability_thresholds:
    tier_nano: {pass_at_1: 0.10}
    tier_micro: {pass_at_1: 0.25}
    tier_standard: {pass_at_1: 0.45}
    tier_advanced: {pass_at_1: 0.65}
    tier_reasoning: {pass_at_1: 0.80}

  quality_floor:
    minimum_human_pass_rate: 0.85  # Human experts must achieve this
    maximum_random_pass_rate: 0.05  # Random baseline must be below this
```

---

## Benchmark Item Generation Prompt Template

```
SYSTEM: You are generating benchmark items for [{task_type}] evaluation.
Each item must be:
- Unambiguous: exactly one correct answer or well-defined rubric
- Calibrated: difficulty = [{difficulty}] per rubric definitions
- Non-contaminated: do not use examples from public benchmarks
- Domain: [{domain}]

Generate a benchmark item in YAML format following this schema:
[item schema above]

The item must include at least 3 executable test cases with expected outputs.
```

---

## Quality Gate Criteria

| Gate | Criterion | Threshold | Blocking |
|---|---|---|---|
| G1 | Human expert pass rate | ≥ 85% | Yes |
| G2 | Random baseline pass rate | ≤ 5% | Yes |
| G3 | Inter-annotator agreement (κ) | ≥ 0.75 | Yes |
| G4 | Contamination check clean | 0 overlapping items | Yes |
| G5 | Difficulty distribution | Within 10% of target | No |