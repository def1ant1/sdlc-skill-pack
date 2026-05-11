# Workflow Plan Standard

Workflow plans must validate against `schemas/workflow-plan.schema.json` and pass `scripts/validation/validate_workflow_plan.py`.

## Required format

- `id`: kebab-case identifier.
- `objectives`: non-empty list.
- `steps`: ordered execution units with:
  - `id`
  - `order` (1..N, unique, contiguous)
  - `skill` (must map to an installed `skills/*/SKILL.md` or `core/*/SKILL.md`)
  - `depends_on` (known step IDs only; dependencies must have lower order)
  - `governance_policy_refs` (non-empty; all refs must exist in workflow registry policy list)
- `governance_gates`: non-empty list where each `policy_ref` is known.
- `dry_run_safety`: must enforce `no_external_writes: true` and `require_human_approval_for_mutations: true`.
- `deterministic_artifacts`: output paths must live under `artifacts/` or `reports/`.

## Strict validation checks

The validator enforces:

1. Schema structure and required fields.
2. Registry membership by plan id.
3. Known governance policy references for both gates and steps.
4. Skill existence.
5. Duplicate step IDs and duplicate step order.
6. Non-contiguous ordering.
7. Unknown dependencies.
8. Ordering violations (`depends_on` must point backward).
9. Circular dependencies.

## CLI usage

```bash
python scripts/validation/validate_workflow_plan.py tests/fixtures/workflow-plans/valid-plan.yaml
```

Optional flags:

- `--root` repository root (default: auto-detected)
- `--schema` schema path (default: `schemas/workflow-plan.schema.json`)
- `--registry` workflow registry path (default: `workflows/registry/workflow-plans.yaml`)
