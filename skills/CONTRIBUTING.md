# Skill Contribution Guide

## Add a skill

1. Create `skills/<kebab-case-skill-name>/SKILL.md`.
2. Add supporting files as needed (`manifest.v9.json`, `routing.yaml`, `eval.spec.json`, `examples/`, `references/`).
3. Ensure safety/governance boundaries are explicit in the skill description.
4. Register the skill in `skill_registry/skills.index.json`.
5. Run:
   - `python scripts/registry/validate_registry_entry.py --index skill_registry/skills.index.json`
   - `python scripts/registry/package_skill.py --skill-dir skills/<skill-name> --version <semver>`

See `skill_registry/README.md` for the registry and publishing flow.
