# Skill Specification Standard (`skill.yaml`)

## Purpose

Defines a hardened, machine-readable skill specification that supports:

- deterministic token-budget enforcement,
- machine-readable governance policy metadata,
- metadata-only loading for orchestration/planning paths.

## Canonical Files

- `schemas/skill.yaml.schema.json`
- `schemas/skill-metadata.schema.json`
- `scripts/validation/validate_skill_yaml.py`

## Required Model

`skill.yaml` must include:

1. `schema_version` (`"1.0"`)
2. `metadata` object (validated by `skill-metadata.schema.json`)
3. `runtime` object with at least one `entrypoints` item

### Required Metadata Fields

- `name`, `version`, `owner`, `maturity`, `domain`
- `token_budget`
  - `input_tokens`
  - `output_tokens`
  - `budget_strategy` (`fixed|adaptive|tiered`)
- `governance`
  - `policy_refs[]`
  - `risk_tier` (`low|medium|high|critical`)
  - `requires_hitl` (boolean)
- `load_modes[]`
  - must include `metadata_only`
  - supports `runtime`

## Metadata-Only Load Mode Contract

When the orchestrator requests `metadata_only`, skill loading must not require
runtime reference hydration (e.g., deep `references/`, connectors, or examples).
The planner/routing stack can decide eligibility from metadata alone.

## MVP Manifest Parity Rule

Until every skill migrates to `skill.yaml`, `manifest.v9.json` is accepted as an
intermediate format only if it includes parity fields under `metadata`:

- `metadata.token_budget`
- `metadata.governance`
- `metadata.load_modes` including `metadata_only`

## Validation Commands

```bash
python scripts/validation/validate_skill_yaml.py --mvp
python scripts/validation/validate_skill_yaml.py --skill-file skills/<skill>/skill.yaml
```

## Migration Requirements for Non-Compliant Skills

For each non-compliant MVP skill:

1. Add missing required top-level V9 fields if absent.
2. Add `metadata.token_budget` object with integer input/output budgets.
3. Add `metadata.governance` object with policy refs and HITL requirement.
4. Add `metadata.load_modes` and include `metadata_only`.
5. Optionally add `skill.yaml` and validate against `schemas/skill.yaml.schema.json`.

