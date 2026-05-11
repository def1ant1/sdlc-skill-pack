# Skill Registry

This directory contains CI-validated metadata for skills that can be packaged and optionally published.

## Layout

- `skills.index.json`: registry index of known skills.
- `locks/<skill>.lock.json`: resolved lockfiles for packaged skill artifacts.
- `templates/entry.template.json`: starter registry entry template.

## Contributor workflow

1. Add or update a skill under `skills/<skill-name>/`.
2. Add/update a registry entry in `skill_registry/skills.index.json`.
3. Validate registry metadata:
   - `python scripts/registry/validate_registry_entry.py --index skill_registry/skills.index.json`
4. Package a skill + generate lockfile:
   - `python scripts/registry/package_skill.py --skill-dir skills/<skill-name> --version <semver>`
5. (Optional) Publish with explicit opt-in:
   - `python scripts/registry/publish_skill.py --artifact dist/<artifact>.tar.gz --enable-public-publish`

Public publishing is **disabled by default** and requires an explicit flag.
