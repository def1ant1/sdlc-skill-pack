# Skill Authoring Guidelines

Rules for writing SKILL.md files that remain concise, reusable, and efficient
in a Claude Code context window. Enforced in part by
`scripts/validation/validate_skill_structure.py`.

---

## The Core Principle: Progressive Disclosure

A SKILL.md is a **behavioral contract**, not a knowledge repository. It tells
Claude what role to play, what protocol to follow, and where to find detail —
it does not contain the detail itself.

Detailed content belongs in referenced files under the skill's directory:

```
skills/<name>/
  SKILL.md              ← behavioral contract (concise)
  references/           ← deep detail, rules, matrices, catalogs
  scripts/              ← deterministic logic
  templates/            ← reusable output formats
  examples/             ← worked instances
  assets/               ← diagrams, schemas, static files
```

---

## What Belongs in SKILL.md

### Include

- **Role definition** — one concise paragraph stating what the skill does and
  what it does not do.
- **Activation conditions** — when this skill should and should not load.
- **Protocol steps** — the ordered procedure the skill follows (step numbers,
  not prose).
- **Output format** — the structure Claude must produce (headings only, not
  full templates).
- **References** — the list of files to load for deep detail on each topic.

### Exclude

- Full standards text (link to `shared/standards/`)
- Full policy text (link to `shared/policies/`)
- Long decision matrices, classification tables, or scoring rubrics (move to
  `references/`)
- Reusable output templates (move to `templates/`)
- Worked examples (move to `examples/`)
- Repeated content that appears in another skill (extract to `shared/`)

---

## Size Limits

| Tier | Skill Type | Warning Threshold | Hard Limit |
|---|---|---|---|
| Control-plane | `core/` skills | 300 lines | 500 lines |
| Domain | `skills/` skills | 150 lines | 300 lines |

These limits exclude the YAML frontmatter block.

When a SKILL.md approaches its warning threshold, audit it using the checklist
below before adding more content.

---

## Progressive Disclosure Audit Checklist

Run this checklist before committing changes to any SKILL.md:

```
[ ] Every section heading has a corresponding reference file for deep detail.
[ ] No section contains a table with more than 10 rows — long tables belong in references/.
[ ] No section reproduces content already in shared/standards/ or shared/policies/.
[ ] No output template exceeds 15 lines inline — longer templates belong in templates/.
[ ] No example output is included — worked examples belong in examples/.
[ ] Protocol steps reference external files rather than embedding their full content.
[ ] The file could be read in under 5 minutes and still give Claude a complete behavioral contract.
```

---

## Frontmatter Requirements

Every SKILL.md must open with a valid YAML frontmatter block:

```yaml
---
name: kebab-case-name
description: one-line description (max 1024 chars, no angle brackets)
metadata:
  version: "x.y.z"
  category: ...
  owner: ...
  maturity: foundation | alpha | beta | stable
  dependencies: [skill-name, ...]
---
```

Rules:
- `name` must be kebab-case and match the folder name.
- `description` max 1024 characters. No `<` or `>`.
- `version` must be a quoted semantic version string.
- `maturity` must be one of: `foundation`, `alpha`, `beta`, `stable`.
- `dependencies` lists the skill names (not file paths) this skill requires to
  be loaded first.

---

## Reference File Conventions

Reference files in `references/` follow these conventions:

1. **One topic per file** — `intent-classification.md` covers classification;
   `skill-dependency-graph.md` covers dependencies. Do not combine topics.
2. **Named for their content, not their consumer** — `quality-attributes.md`,
   not `what-architecture-skill-needs.md`.
3. **Always include a purpose line** — the first paragraph of every reference
   states which skill(s) use it and for what.
4. **Tables over prose for decision rules** — signal tables, gate criteria, and
   dependency lists are more scannable and easier to update.
5. **No duplication of shared content** — reference files may link to
   `shared/standards/` and `shared/policies/` but must not copy their content.

---

## Templates and Examples

**Templates** in `templates/` are reusable output structures. They contain
placeholders, not real data. They must be referenced from SKILL.md, not
embedded in it.

**Examples** in `examples/` are fully worked instances. They demonstrate correct
skill output for a realistic scenario. They are optional but strongly recommended
for complex skills. They must not appear inline in SKILL.md.

---

## Dependency Declarations

The `dependencies` field in frontmatter must list every skill whose output this
skill assumes is available. These must match entries in the skill registry
(`core/orchestration/references/skill-dependency-graph.md`).

Do not list `shared/` resources as dependencies — those are always available.

---

## Versioning

Version increments follow this convention:

| Change | Version Impact |
|---|---|
| Add or change a protocol step | Minor (`x.Y.z`) |
| Add or remove a reference file | Patch (`x.y.Z`) |
| Breaking change to output format | Major (`X.y.z`) |
| Frontmatter-only change | Patch |

The `core/orchestration/SKILL.md` version gates downstream skill loading.
Always increment its version when the routing or handoff protocol changes.

---

## Validation

`scripts/validation/validate_skill_structure.py` enforces:

- Kebab-case folder names
- Presence of `SKILL.md` in every skill folder
- Progressive disclosure size limits (warning at threshold, error at hard limit)

`scripts/validation/validate_frontmatter.py` enforces:

- Valid YAML frontmatter
- Required fields (`name`, `description`)
- No angle brackets in frontmatter values
- Kebab-case `name`
- Description length ≤ 1024 characters

Both validators run in CI on every push and PR.
---


## `skill.yaml` / Manifest Metadata Parity (MVP Requirement)

For MVP shipping compatibility, each skill must provide either:

- `skill.yaml` validated by `schemas/skill.yaml.schema.json`, or
- `manifest.v9.json` with metadata parity fields:
  - `metadata.token_budget`
  - `metadata.governance`
  - `metadata.load_modes` containing `metadata_only`

Use:

```bash
python scripts/validation/validate_skill_yaml.py --mvp
```

This enables metadata-only planner loading without hydrating full runtime references.

