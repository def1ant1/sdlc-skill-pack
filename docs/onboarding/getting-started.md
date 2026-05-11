# Getting Started

Phase 0 starter documentation. Expand this document as the platform matures.

## CLI quickstart

Copy/paste examples:

```bash
# List workflow execution history (human-readable)
apotheon workflows list

# List workflow execution history as JSON
apotheon workflows list --json

# Plan a workflow (dry-run by default)
apotheon workflows run "Harden CI pipeline security posture"

# Plan and execute workflow (opt-in)
apotheon workflows run --execute "Harden CI pipeline security posture"

# Preview schedule windows
apotheon schedules preview --count 3

# Execute due schedules for the lookback window
apotheon schedules run-due --lookback-minutes 120

# List schedule run artifacts
apotheon runs list

# List schedule run artifacts as JSON
apotheon runs list --output json
```

## Profile selection and validation

Use product profiles to constrain capabilities and align Compose runtime behavior.

```bash
# Validate profile definitions
python scripts/validation/validate_profiles.py

# Choose a profile and run compose with the mapped profile set
COMPOSE_PROFILES=local-solo,core docker compose up -d
```

See `docs/reference/profile-selection.md` for profile boundaries, high-risk defaults, and constraints.

## Chat UI MVP quickstart

Use the Streamlit Chat UI for browser-based planning with safe defaults.

```bash
streamlit run apps/chat-ui/streamlit_app.py
```

In the UI:

1. Select a domain planner and submit an objective.
2. Review dry-run plan output and artifacts.
3. Import an OldFarmTrucks template for seeded examples.
4. Review schedules, app health, cost status, and rate-limit warnings.

By default, live writes are blocked unless explicit approval flow is satisfied.


## OldFarmTrucks template import demo

Provision the OldFarmTrucks template in safe dry-run mode:

```bash
python scripts/company_templates/import_template.py --validate-workflows
```

This imports/provisions workflows, schedules, dashboards, connectors, approvals, budgets, and sample data into `reports/company_templates/oldfarmtrucks-import.json`, and validates one short-term plus one long-term workflow with runtime dry-runs.


## OSS vs commercial boundary

To avoid confusion between current local open-source capabilities and potential future hosted/cloud/enterprise offerings, review:

- `COMMERCIAL.md`
- `LICENSE_REVIEW.md`
- `docs/commercial/open-core-boundary.md`

Use these documents as the source of truth for licensing and feature-boundary interpretation during onboarding and deployment planning.


## VS Code extension developer flow

Use the extension commands for developer operations inside the repo:

- `Apotheon: Validate Skill Manifests`
- `Apotheon: Dry-Run Workflow Launch`
- `Apotheon: Generate Runtime Diagnostics`
- `Apotheon: Skill Maturity Report`
- `Apotheon: Import OldFarmTrucks Template`

See `docs/onboarding/VSCODE_EXTENSION_DEVELOPER.md` and `extensions/vscode/README.md` for command details and compile instructions.
