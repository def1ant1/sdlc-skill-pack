# API Reference

This repository is primarily CLI-first. API integration points are currently:

- `cli.py` command surface for local operators.
- local app manifests under `local_apps/manifests/`.
- workflow plan/contracts in `schemas/`.

## Command sanity checks

```bash
python cli.py --help
python scripts/validation/validate_workflow_plan.py --help
```

## Profiles and workflows

Profiles are validated by:

```bash
python scripts/validation/validate_profiles.py
```

Workflows are validated by:

```bash
python scripts/validation/validate_workflow_plan.py --workflow-plan workflows/registry/workflow-plans.yaml
```
