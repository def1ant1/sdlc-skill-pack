# Skill Contract v9

This document defines the required manifest/frontmatter contract for every `SKILL.md` in `core/`, `skills/`, and `agents/`.

## Required fields

The canonical source of truth is `schemas/skill-manifest-v9.schema.json`. Every skill contract must provide:

- `name`, `type`, `domain`, `subdomain`, `version`, `owner`, `maturity`
- `dependencies`, `activation_triggers`, `required_context`, `optional_context`
- `input_contract`, `output_contract`, `memory_policy`, `token_budget`, `context_loading`
- `governance_level`, `human_approval_required`, `execution_mode`
- `latency_target`, `cost_target`, `determinism_level`
- `telemetry_events`, `eval_metrics`, `security_classification`
- `integration_targets`, `data_contracts`, `failure_modes`, `fallbacks`

## Implementation guidance

1. Use `scripts/migrate_frontmatter_to_manifest.py` to backfill missing fields at scale.
2. Run `scripts/validate_skill_contracts.py` to enforce required fields.
3. Run `scripts/generate_skill_inventory.py` to produce deterministic JSON/Markdown/CSV inventory outputs.
4. Keep schema-first changes in sync by updating this document and validator tests when adding/removing required fields.
