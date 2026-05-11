# Quickstart (15 minutes)

1. Install dependencies.
2. Start local stack.
3. Validate runtime and docs integrity.
4. Run a dry-run OldFarmTrucks workflow.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
scripts/docker/init-local-stack.sh
apotheon doctor
python scripts/docs/validate_docs_integrity.py
python scripts/validation/validate_workflow_plan.py --workflow-plan workflows/registry/workflow-plans.yaml
```

OldFarmTrucks dry-run:

```bash
python scripts/workflows/execute_workflow.py --workflow workflows/examples/oldfarmtrucks-weekly-operating-review.json --dry-run
```
