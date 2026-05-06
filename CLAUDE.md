# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Apotheon SDLC Skills is a Claude Code skill-pack for orchestrating the complete software development lifecycle. It is a **prompt/markdown-based framework** — there is no runtime application, only structured skill definitions, validation scripts, and tests.

## Commands

```bash
# Validate skill folder structure (kebab-case names, SKILL.md presence)
python scripts/validation/validate_skill_structure.py .

# Validate YAML frontmatter in all SKILL.md files
python scripts/validation/validate_frontmatter.py .

# Run all tests
pytest

# Run a single test file
pytest tests/skills/test_skill_files.py

# Scaffold a new skill
python scripts/generators/create_skill.py <skill-name>

# Route an objective to a skill plan
python scripts/orchestration/plan_workflow.py "<objective>"

# Build a context packet (reads JSON from stdin)
python scripts/memory/build_context_packet.py
```

Linting uses Ruff (configured in `pyproject.toml`, line-length 100). The pre-commit hook runs Ruff automatically.

## Architecture

### Skill Structure

Every skill lives under `skills/<kebab-case-name>/SKILL.md` (domain skills) or `core/<kebab-case-name>/SKILL.md` (control-plane skills). Each `SKILL.md` must open with YAML frontmatter:

```yaml
---
name: kebab-case-name
description: one-line description (max 1024 chars, no angle brackets)
metadata:
  version: "x.y.z"
  category: ...
  owner: ...
  maturity: ...
  dependencies: [...]
---
```

### Core vs. Domain Skills

- **`core/`** — Control-plane: `sdlc-orchestration` (routes requests to domain skills) and `sdlc-memory-token-management` (preserves decisions across phases).
- **`skills/`** — 13 domain skill placeholders covering the full SDLC (requirements → architecture → ai-engineering → backend → frontend → code-review → qa → devsecops → release → observability → sre → compliance → executive-reporting).

### Agents

`agents/` contains 6 specialist role definitions (architect, optimizer, researcher, reviewer, security, tester). These are role contracts consumed by the orchestration skill.

### Shared Resources

`shared/` holds cross-cutting content referenced by skills:
- `standards/` — 6 documents (AI governance, architecture principles, markdown, naming, prompt engineering, security)
- `policies/` — 4 documents (AI safety, architectural review, data governance, secure development)
- `frameworks/`, `prompts/`, `templates/`, `ontologies/`, `examples/`, `references/`

### Validation Rules (enforced by scripts and CI)

- All skill folder names must be kebab-case
- Every `SKILL.md` must have valid YAML frontmatter (opening/closing `---`, required `name` and `description` fields)
- `name` must be kebab-case; `description` max 1024 chars; no angle brackets (`<>`) anywhere in frontmatter

### CI Pipeline

`.github/workflows/validate.yml` runs on every push/PR: installs deps → `validate_skill_structure.py` → `validate_frontmatter.py` → `pytest`.

## Conventions

- Branch strategy: `main` / `develop` / `feature/*` / `hotfix/*` / `experimental/*`
- Conventional commits with scopes: `feat`, `fix`, `refactor`, `docs`, `test`, `security`, `governance`, `orchestration`, `memory`
- New skills use the generator script (`create_skill.py`) to ensure correct scaffold
