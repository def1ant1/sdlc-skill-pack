# Contributing

## Branch Strategy

- `main`: stable releases
- `develop`: integration
- `feature/*`: new features
- `hotfix/*`: urgent fixes
- `experimental/*`: R&D

## Commit Convention

Use scoped conventional commits:

```text
feat(orchestration): add workflow routing contract
fix(memory): preserve accepted decisions in compression
security(devsecops): add secret-handling rule
docs(standards): clarify naming conventions
test(skills): add frontmatter validation test
```

Allowed types:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `security`
- `governance`
- `orchestration`
- `memory`

## Pull Request Checklist

Every PR must include:

- objective
- affected skills
- standards impacted
- test evidence
- governance implications
- token/context impact
- rollback considerations

## Skill Contribution Rules

Every skill folder must:

- use kebab-case
- contain exact `SKILL.md`
- include valid YAML frontmatter
- include `name` and `description`
- avoid XML angle brackets in frontmatter
- use `references/` for long material
- include examples when workflow behavior is non-trivial

## Skill maturity and certification
- Run `python scripts/grade_skill_maturity.py` to generate `reports/skill_maturity_report.md` and enforce MVP/critical thresholds.
- Run `python scripts/certify_skill.py <skill_dir> ...` with check flags to generate `reports/skill_certification_report.md` with repeatable criteria and evidence pointers.


## Skill registry workflow

Use the registry flow for repeatable skill versioning and CI checks:

1. Add/update a skill in `skills/<skill-name>/`.
2. Register or update the skill in `skill_registry/skills.index.json`.
3. Validate registry entries: `python scripts/registry/validate_registry_entry.py --index skill_registry/skills.index.json`.
4. Package and lock a version: `python scripts/registry/package_skill.py --skill-dir skills/<skill-name> --version <semver>`.
5. Public publishing is optional and disabled by default. To opt in explicitly: `python scripts/registry/publish_skill.py --artifact <artifact> --enable-public-publish`.


## Documentation quality checks
Run these before opening a PR:

```bash
python scripts/docs/validate_docs_integrity.py
python scripts/docs/validate_readme_claims.py
python scripts/docs/validate_doc_uniqueness.py
```
