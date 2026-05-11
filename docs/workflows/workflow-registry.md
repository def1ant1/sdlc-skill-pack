# Local Workflow Registry and Fixture Conventions

## Directories

- `workflows/examples/`: executable reference workflow fixtures.
- `workflows/library/registry.yaml`: local registry index of known fixtures.
- `workflows/generated/`: planner-generated outputs (`.gitkeep` retained).

## Registering a workflow

```bash
python scripts/workflows/register_workflow.py workflows/examples/oldfarmtrucks-launch-readiness.json
```

This command inserts/updates the fixture by `fixture_id` and records:

- `id`
- fixture `file`
- `expected_artifacts`
- `failure_fixtures`

## Listing workflows

```bash
python scripts/workflows/list_workflows.py
python scripts/workflows/list_workflows.py --json
```

## Fixture schema conventions

Each fixture in `workflows/examples/` should include:

- `fixture_id`
- `objective`
- `canonical_governance_policies`
- `expected_artifacts`
- `failure_fixtures` (negative tests)
- `plan` (runtime executable subdocument)

`failure_fixtures` encode expected break modes (for example `missing-objective` and `empty-skill-chain`) to support deterministic regression testing.

## Dry-run validation loop

1. Register each fixture.
2. Execute `plan` with `scripts/runtime/execute_workflow.py --dry-run`.
3. Verify each run emits `run_id`, `status`, and `steps` artifacts.
4. Validate negative fixtures fail predictably in tests.
