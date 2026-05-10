---
name: evaluation-dataset-curation
description: Rigorously curates evaluation datasets through correctness verification, deduplication, class balance enforcement, and coverage analysis to ensure evaluation validity and prevent benchmark overfitting.
metadata:
  version: "1.0.0"
  category: evaluation
  owner: platform
  maturity: alpha
  dependencies: [benchmark-factory, dataset-curation, telemetry]

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

Evaluation dataset quality assurance specialist for the benchmarking platform. Applies
rigorous curation standards — correctness verification, near-duplicate removal, class balance
enforcement, and capability coverage analysis — to ensure evaluation datasets produce valid,
unbiased capability assessments and resist overfitting.

## Activation Triggers

- Benchmark-generation produces a raw benchmark requiring quality certification
- Benchmark-factory flags declining evaluation validity (high variance, unexpected ceiling effects)
- Model-lifecycle requires a vetted evaluation dataset for a promotion gate
- Scheduled quarterly benchmark quality audit

## Execution Protocol

1. **Correctness verification**: For each item, verify the reference answer is unambiguously
   correct; flag ambiguous items, multiple valid answers, and items where the reference
   answer is disputed; remove or reclassify flagged items.

2. **Deduplicate**: Apply exact and semantic deduplication (similarity threshold > 0.90);
   remove near-duplicates from both train-split leakage (contamination) and within-set
   redundancy.

3. **Balance analysis**: Measure class distribution, difficulty tier distribution, and
   capability sub-skill coverage; enforce minimum representation thresholds; flag gaps.

4. **Coverage verification**: Map items to the capability taxonomy; identify sub-skills
   with insufficient coverage (< minimum item count); recommend benchmark-generation
   to fill gaps.

5. **Anti-gaming audit**: Check for items that can be solved by surface heuristics
   (length bias, format patterns, keyword matching) without actually exercising the
   target capability; remove or redesign compromised items.

6. **Issue curation certificate**: Record all curation actions, removal rates, balance
   metrics, and coverage scores; issue a versioned curation certificate.

## Output Format

Curation report with: `dataset_id`, `items_before/after` (counts), `removal_reasons` (breakdown),
`balance_scores` (per dimension), `coverage_gaps` (list), `anti-gaming_issues_resolved`,
and `curation_certificate_id`.

## References

- `references/evaluation-curation-standards.md` — correctness verification protocol, balance thresholds, anti-gaming detection rules