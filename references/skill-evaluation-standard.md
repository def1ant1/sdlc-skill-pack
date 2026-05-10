# Skill Evaluation Standard

## Purpose
All **P0/P1** skills must have a machine-readable evaluation specification for regression and release gating.

## Location
- `skills/<skill-name>/eval.spec.json`
- Schema: `schemas/skill-eval.schema.json`

## Requirements
1. `priority` MUST match the skill frontmatter priority.
2. At least one dataset and one metric are required.
3. Acceptance gates must be explicit and release-actionable.
4. `last_updated` should be refreshed whenever thresholds or datasets change.

## Enforcement
Use `scripts/validate_skill_evals.py` in CI. It will fail when:
- Any P0/P1 skill is missing `eval.spec.json`.
- Any `eval.spec.json` has malformed JSON.
- Priority in spec and skill metadata diverge.
