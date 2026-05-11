#!/usr/bin/env python3
"""Validate workflow plan files against schema and registry constraints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("plan", type=Path, help="Path to workflow plan file (yaml/json)")
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--schema", type=Path, default=Path("schemas/workflow-plan.schema.json"))
    p.add_argument("--registry", type=Path, default=Path("workflows/registry/workflow-plans.yaml"))
    return p.parse_args()


def load_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _check_type(value, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
    }.get(expected, True)


def validate_schema_instance(data, schema, path="$"):
    errors: list[str] = []
    if "type" in schema and not _check_type(data, schema["type"]):
        return [f"{path}: expected {schema['type']}"]

    if isinstance(data, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"{path}: missing required field '{field}'")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for key in data:
                if key not in allowed:
                    errors.append(f"{path}: unknown field '{key}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in data:
                errors.extend(validate_schema_instance(data[key], subschema, f"{path}.{key}"))

    if isinstance(data, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(data) < min_items:
            errors.append(f"{path}: expected at least {min_items} items")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                errors.extend(validate_schema_instance(item, item_schema, f"{path}[{i}]"))

    if isinstance(data, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(data) < min_length:
            errors.append(f"{path}: expected minimum length {min_length}")
        enum_vals = schema.get("enum")
        if enum_vals and data not in enum_vals:
            errors.append(f"{path}: value '{data}' not in {enum_vals}")

    return errors


def detect_cycles(graph: dict[str, list[str]]) -> bool:
    seen: set[str] = set()
    active: set[str] = set()

    def visit(node: str) -> bool:
        if node in active:
            return True
        if node in seen:
            return False
        seen.add(node)
        active.add(node)
        for dep in graph.get(node, []):
            if visit(dep):
                return True
        active.remove(node)
        return False

    return any(visit(node) for node in graph)


def validate_constraints(plan: dict, registry: dict, root: Path) -> list[str]:
    errors: list[str] = []
    registered = {item["id"]: item["file"] for item in registry.get("workflow_plans", [])}
    if plan.get("id") not in registered:
        errors.append(f"plan id '{plan.get('id')}' is not in registry")

    known_policies = set(registry.get("known_governance_policies", []))
    for gate in plan.get("governance_gates", []):
        if gate.get("policy_ref") not in known_policies:
            errors.append(f"unknown governance policy ref: {gate.get('policy_ref')}")

    available_skills = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    available_skills |= {p.parent.name for p in (root / "core").glob("*/SKILL.md")}

    step_ids = set()
    dep_graph: dict[str, list[str]] = {}
    for step in plan.get("steps", []):
        sid = step.get("id")
        if sid in step_ids:
            errors.append(f"duplicate step id: {sid}")
        step_ids.add(sid)
        skill = step.get("skill")
        if skill not in available_skills:
            errors.append(f"missing prerequisite skill: {skill} (step: {sid})")
        dep_graph[sid] = list(step.get("depends_on", []))

    for sid, deps in dep_graph.items():
        for dep in deps:
            if dep not in step_ids:
                errors.append(f"step '{sid}' depends on unknown step '{dep}'")

    if detect_cycles(dep_graph):
        errors.append("circular step dependencies detected")
    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    plan_path = (root / args.plan).resolve() if not args.plan.is_absolute() else args.plan
    schema_path = root / args.schema
    registry_path = root / args.registry

    plan = load_doc(plan_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = load_doc(registry_path)

    errors = validate_schema_instance(plan, schema)
    errors.extend(validate_constraints(plan, registry, root))

    result = {"valid": not errors, "errors": errors}
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
