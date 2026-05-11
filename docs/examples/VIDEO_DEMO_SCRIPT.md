# Video Demo Script (Operator Walkthrough)

1. Introduce local-first architecture and governance-first execution.
2. Show `python cli.py doctor` and `python cli.py diagnostics`.
3. Validate profiles and schedules.
4. Plan and dry-run OldFarmTrucks workflow.
5. Show generated runtime evidence artifacts and reports.

## Command track

```bash
python cli.py doctor
python cli.py diagnostics
python scripts/validation/validate_profiles.py
python scripts/schedules/run_due_schedules.py --dry-run
python scripts/runtime/execute_workflow.py --plan workflows/examples/oldfarmtrucks-weekly-operating-review.json --dry-run
```
