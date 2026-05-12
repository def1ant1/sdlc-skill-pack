#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas" / "artifacts"
FIXTURES = ROOT / "fixtures" / "artifacts"

MAP = {
    "plan": "plan.schema.json",
    "workflow": "workflow.schema.json",
    "skill_proposal": "skill-proposal.schema.json",
    "task": "task.schema.json",
    "schedule": "schedule.schema.json",
    "knowledge_note": "knowledge-note.schema.json",
    "decision": "decision.schema.json",
    "approval_request": "approval-request.schema.json",
    "assistant_action": "assistant-action.schema.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    common = load_json(SCHEMAS / "common-envelope.schema.json")
    failures: list[str] = []
    for artifact_type, schema_name in MAP.items():
        schema_path = SCHEMAS / schema_name
        fixture_path = FIXTURES / f"{artifact_type}.json"
        schema = load_json(schema_path)
        store = {
            common.get("$id"): common,
            schema.get("$id"): schema,
            "./common-envelope.schema.json": common,
        }
        resolver = RefResolver(base_uri=f"file://{SCHEMAS}/", referrer=schema, store=store)
        validator = Draft202012Validator(schema, resolver=resolver)
        data = load_json(fixture_path)
        errs = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errs:
            failures.append(f"{artifact_type}: {errs[0].message}")

    if failures:
        for f in failures:
            print(f"ERROR: {f}")
        return 1

    print(f"PASS: validated {len(MAP)} artifact fixtures against schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
