# Apotheon VS Code Extension (Developer)

## Command palette flows

- `Apotheon: Validate Skill Manifests` → runs `scripts/validation/validate_skill_yaml.py --mvp`.
- `Apotheon: Dry-Run Workflow Launch` → runs graph executor in dry-run mode using the company operating system fixture.
- `Apotheon: Generate Runtime Diagnostics` → runs diagnostics generator and opens `runtime/diagnostics/runtime_diagnostics.json`.
- `Apotheon: Skill Maturity Report` → runs `scripts/grade_skill_maturity.py --profile mvp`.
- `Apotheon: Import OldFarmTrucks Template` → runs the template importer for `oldfarmtrucks`.

## Compiler command

- `npm --prefix extensions/vscode run compile`

## Validation against repo structure

The extension commands target scripts and fixtures currently present under `scripts/`, `workflows/examples/`, `company_templates/`, and `runtime/diagnostics/`.
