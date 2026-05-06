# Apotheon SDLC Skill Platform

An advanced Claude Code skill-pack foundation for orchestrating the complete software development lifecycle.

## Phase 0 Scope

This repository contains the Phase 0 foundation:

- Repository architecture
- Skill packaging conventions
- Orchestration contracts
- Memory and token management contracts
- Governance and security baseline
- Documentation skeleton
- Example `system-architecture` skill
- Validation scripts and starter tests

## Design Principles

1. Progressive disclosure: keep `SKILL.md` concise and move detail to `references/`.
2. Composability: skills should cooperate instead of assuming they are the only active skill.
3. Deterministic validation: use scripts for repeatable checks.
4. Governance by default: security, architecture, and AI governance are built in.
5. Context efficiency: preserve decisions and constraints before verbose history.

## Repository Layout

```text
core/       Control-plane skills and workflow contracts
skills/     SDLC domain skills
shared/     Standards, policies, templates, prompts, frameworks
scripts/    Deterministic validation, orchestration, memory, analysis utilities
agents/     Specialist agent role definitions
assets/     Reusable visual and document assets
docs/       Human-facing documentation
examples/   Example workflows, packets, and governance outputs
tests/      Validation and regression tests
```

## Quick Start

1. Review `docs/onboarding/getting-started.md`.
2. Review `shared/standards/naming-conventions.md`.
3. Run validation:

```bash
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .
pytest
```

## Phase 0 Exit Criteria

- Repo structure exists.
- Core skill standards exist.
- Orchestration and memory contracts exist.
- Example skill validates.
- Basic tests pass.
