#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validation.validate_json_schema import load_doc  # noqa: E402

MAPPINGS = ROOT / "examples" / "connector-mappings"
WORKFLOW_OUTPUTS = ROOT / "examples" / "workflow-outputs"


def _check_mapping(path: Path) -> list[str]:
    data = load_doc(path)
    errs: list[str] = []
    if "canonical_entity" not in data:
        errs.append("$.canonical_entity missing required field")
    fields = data.get("field_mappings")
    if not isinstance(fields, list):
        errs.append("$.field_mappings expected array")
        return errs
    for i, item in enumerate(fields):
        base = f"$.field_mappings[{i}]"
        if not isinstance(item, dict):
            errs.append(f"{base} expected object")
            continue
        for req in ("source_field", "target_field", "target_type"):
            if req not in item:
                errs.append(f"{base}.{req} missing required field")
        allowed = {"source_field", "target_field", "target_type", "transform", "required"}
        unknown = set(item) - allowed
        for key in sorted(unknown):
            errs.append(f"{base}.{key} unknown field")
    return errs


def _check_workflow_output(path: Path) -> list[str]:
    data = load_doc(path)
    errs: list[str] = []
    for req in ("schema_ref", "source", "lineage", "payload"):
        if req not in data:
            errs.append(f"$.{req} missing required field")
    return errs


def main() -> int:
    failures: list[str] = []
    if MAPPINGS.exists():
        for f in sorted(MAPPINGS.glob("*.json")):
            failures.extend([f"{f}: {e}" for e in _check_mapping(f)])
    if WORKFLOW_OUTPUTS.exists():
        for f in sorted(WORKFLOW_OUTPUTS.glob("*.json")):
            failures.extend([f"{f}: {e}" for e in _check_workflow_output(f)])

    if failures:
        print("\n".join(failures))
        return 1
    print("Connector mappings and workflow output lineage checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
