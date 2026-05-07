---
name: prompt-optimization
description: Evaluates prompt variants systematically and applies automated improvement using outcome-feedback loops from the reinforcement-optimizer.
metadata:
  version: "0.1.0"
  category: ml-ops
  owner: platform
  maturity: draft
  dependencies: ['reinforcement-optimizer', 'benchmark-factory']
---

## Role

Systematic prompt engineering automation. Generates prompt variants for a target task,
evaluates them against a quality rubric using `benchmark-factory`, and feeds results to
`reinforcement-optimizer` to converge on the highest-performing prompt. Replaces manual
prompt iteration with a data-driven optimization loop.

## Activation Triggers

- A skill owner registers a prompt for optimization
- A prompt's quality score drops below threshold (performance regression detected)
- `reinforcement-optimizer` requests a new variant to evaluate in an active experiment
- Operator requests a prompt audit and improvement pass for a business-critical skill
- A new model is deployed and existing prompts may need re-optimization for the new model

## Execution Protocol

1. **Baseline establishment**: Evaluate the current (baseline) prompt on a held-out
   evaluation set from `benchmark-factory`. Record: accuracy, quality score, cost, latency.

2. **Variant generation**: Generate candidate prompt variants using:
   - Instruction reformulation (different phrasing of the task)
   - Chain-of-thought insertion (add reasoning scaffolding)
   - Role assignment variations (different persona in system prompt)
   - Few-shot example addition (add 1, 3, or 5 examples)
   - Format constraint changes (structured vs. free-form output)

3. **Variant evaluation**: For each variant, run the evaluation suite. Collect the same
   metrics as the baseline.

4. **Register with optimizer**: Submit variants as arms in a `reinforcement-optimizer`
   experiment with `algorithm: thompson_sampling`. The optimizer selects which variant
   to run next on live traffic.

5. **Convergence and promotion**: When the optimizer declares convergence, compare the
   winner against the baseline. If improvement > `min_improvement_threshold` (default 5%),
   promote the winner as the new default and archive the old prompt with provenance metadata.

## Output Format

```yaml
prompt_optimization:
  prompt_id: "skill/code-review/system-prompt"
  experiment_id: "PROMPT-EXP-2026-xxxxx"
  baseline_score: 0.0
  best_variant_score: 0.0
  improvement_pct: 0.0
  status: running | converged | promoted | no_improvement
  promoted_variant_id: null
  trials_completed: 0
```

## Quality Gates

- Minimum 50 trials before declaring convergence
- Winner must beat baseline by > 5% on primary quality metric to qualify for promotion
- Human review required before promoting prompts for P0 skills or HITL-facing outputs

## References

- `references/` — Variant generation strategies, evaluation rubric, promotion criteria
