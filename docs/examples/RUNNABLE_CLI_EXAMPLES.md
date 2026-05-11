# Runnable CLI Examples

This page provides copy/paste examples for current profile, schedule, approval, governance, and diagnostics workflows.

## 1) Profiles

```bash
python scripts/validation/validate_profiles.py
```

## 2) Schedule preview/run-due

```bash
python scripts/schedules/run_due_schedules.py --dry-run
python scripts/schedules/run_due_schedules.py --registry schedules/registry.yaml --dry-run
```

## 3) Workflow planning + dry-run execution

```bash
python scripts/orchestration/plan_workflow.py "Build a secure REST API" > workflows/generated/example-plan.json
python scripts/runtime/execute_workflow.py --plan workflows/generated/example-plan.json --dry-run
```

## 4) Governance and approvals checks

```bash
python scripts/governance/validate_high_risk_boundaries.py
python scripts/governance/validate_hitl_for_actions.py
```

## 5) Diagnostics and health evidence

```bash
python scripts/reports/generate_runtime_diagnostics.py
python scripts/docs/validate_docs_integrity.py
python scripts/docker/check-compose-health.py
```

## 6) OldFarmTrucks demo schedule

```bash
python scripts/schedules/run_due_schedules.py --dry-run --schedule schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
python scripts/runtime/execute_workflow.py --plan workflows/examples/oldfarmtrucks-weekly-operating-review.json --dry-run
```
