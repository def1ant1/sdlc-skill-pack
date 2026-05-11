# OldFarmTrucks Demo Tutorial

## Goal
Run a safe, governance-aware OldFarmTrucks demo from planning through dry-run execution.

## Steps
1. Validate workflow plan contracts.
2. Run fixture-backed dry-run flows.
3. Review artifacts and governance evidence.

```bash
python scripts/validation/validate_workflow_plan.py --workflow-plan workflows/registry/workflow-plans.yaml
pytest tests/scripts/test_oldfarmtrucks_workflow_fixtures.py
python scripts/workflows/execute_workflow.py --workflow workflows/examples/oldfarmtrucks-market-scarcity-scan.json --dry-run
```

## Expected outcomes
- Planner/validator accepts workflow definitions.
- Dry-run executes without side effects.
- Governance boundaries remain enforced for external actions.
