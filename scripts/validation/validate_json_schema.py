#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


class ValidationError(Exception):
    pass


def _type_name(schema: dict[str, Any]) -> str:
    t = schema.get("type")
    if isinstance(t, list):
        return " or ".join(t)
    if isinstance(t, str):
        return t
    if "enum" in schema:
        return f"enum{schema['enum']}"
    return "value"


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _resolve_ref(schema: dict[str, Any], schema_file: Path, cache: dict[Path, dict[str, Any]]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not ref:
        return schema
    if ref.startswith("#/"):
        node: Any = schema
        for part in ref[2:].split("/"):
            node = node[part]
        return node
    ref_file, _, pointer = ref.partition("#")
    target = (schema_file.parent / ref_file).resolve()
    if target not in cache:
        cache[target] = json.loads(target.read_text())
    node: Any = cache[target]
    if pointer.startswith("/"):
        for part in pointer[1:].split("/"):
            node = node[part]
    return node


def validate(value: Any, schema: dict[str, Any], path: str = "$", strict: bool = True) -> list[str]:
    errs: list[str] = []
    allowed_types = schema.get("type")
    if isinstance(allowed_types, str):
        allowed_types = [allowed_types]
    if allowed_types and not any(_matches_type(value, t) for t in allowed_types):
        errs.append(f"{path}: expected {_type_name(schema)}, got {type(value).__name__}")
        return errs

    if isinstance(value, dict):
        props = schema.get("properties", {})
        required = schema.get("required", [])
        for req in required:
            if req not in value:
                errs.append(f"{path}.{req}: missing required field (expected {_type_name(props.get(req, {}))})")
        if strict and schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(props))
            for key in unknown:
                errs.append(f"{path}.{key}: unknown field")
        for key, child in value.items():
            if key in props:
                errs.extend(validate(child, props[key], f"{path}.{key}", strict=strict))

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(value):
                errs.extend(validate(item, item_schema, f"{path}[{idx}]", strict=strict))

    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: expected one of {schema['enum']}, got {value!r}")

    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: expected constant value {schema['const']!r}, got {value!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        exclusive_minimum = schema.get("exclusiveMinimum")
        exclusive_maximum = schema.get("exclusiveMaximum")

        if minimum is not None and value < minimum:
            errs.append(f"{path}: expected >= {minimum}, got {value}")
        if maximum is not None and value > maximum:
            errs.append(f"{path}: expected <= {maximum}, got {value}")
        if exclusive_minimum is not None and value <= exclusive_minimum:
            errs.append(f"{path}: expected > {exclusive_minimum}, got {value}")
        if exclusive_maximum is not None and value >= exclusive_maximum:
            errs.append(f"{path}: expected < {exclusive_maximum}, got {value}")

    return errs


def load_doc(path: Path) -> Any:
    text = path.read_text()
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--schema", required=True)
    p.add_argument("files", nargs="+")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()

    schema_path = Path(args.schema)
    schema = json.loads(schema_path.read_text())

    failed = False
    for f in args.files:
        fpath = Path(f)
        doc = load_doc(fpath)
        errs = validate(doc, schema, strict=args.strict)
        if errs:
            failed = True
            for e in errs:
                print(f"{fpath}: {e}")
    if failed:
        return 1
    print(f"Validated {len(args.files)} file(s) against {schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
