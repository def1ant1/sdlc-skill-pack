# API & CLI Reference Index

Apotheon is CLI-first today. This page maps stable command surfaces to runnable examples that reflect the current repository layout.

## Primary command surface

```bash
python cli.py --help
python cli.py doctor --help
python cli.py diagnostics --help
python cli.py connectors --help
python cli.py workflows --help
python cli.py schedules --help
```

## Runtime and planning APIs

```bash
python scripts/orchestration/plan_workflow.py --help
python scripts/orchestration/plan_gtm_workflow.py --help
python scripts/runtime/execute_workflow.py --help
python scripts/validation/validate_workflow_plan.py --help
```

## Profile and schedule APIs

```bash
python scripts/validation/validate_profiles.py
python scripts/schedules/run_due_schedules.py --help
python scripts/schedules/run_due_schedules.py --dry-run
```

## Governance and approvals APIs

```bash
python scripts/governance/validate_high_risk_boundaries.py
python scripts/governance/validate_hitl_for_actions.py
python scripts/governance/validate_policy_links.py
```

## Diagnostics APIs

```bash
python scripts/reports/generate_runtime_diagnostics.py
python scripts/docs/validate_docs_integrity.py
```

## Related examples

- `docs/examples/RUNNABLE_CLI_EXAMPLES.md`
- `docs/examples/OLDFARMTRUCKS_DEMO_TUTORIAL.md`
- `docs/onboarding/OPERATOR_RUNBOOK.md`
