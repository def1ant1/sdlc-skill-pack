# Single-User Tutorial

## Objective
Run Apotheon as one operator on a laptop in dry-run-safe mode.

## Steps

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
scripts/docker/init-local-stack.sh
python cli.py doctor
python scripts/orchestration/plan_workflow.py "Prepare weekly operating review" > workflows/generated/single-user-plan.json
python scripts/runtime/execute_workflow.py --plan workflows/generated/single-user-plan.json --dry-run
```

## Validate docs/runtime alignment

```bash
python scripts/docs/validate_docs_integrity.py
python scripts/reports/generate_runtime_diagnostics.py
```
