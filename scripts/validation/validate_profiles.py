#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "profile.schema.json"
PROFILES_DIR = ROOT / "profiles"
EXPECTED_PROFILES = [
    "local-solo.yaml",
    "mvp.yaml",
    "team.yaml",
    "enterprise.yaml",
    "full-domain-lab.yaml",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def validate_with_jsonschema(schema: dict, document: dict) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        required = ["profile_id","display_name","tier","description","compose_profiles","capability_boundaries","high_risk"]
        missing = [k for k in required if k not in document]
        return [f"missing required key: {k}" for k in missing]

    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'.'.join([str(p) for p in error.path]) or '<root>'}: {error.message}" for error in validator.iter_errors(document)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate product profile definitions.")
    parser.add_argument("--profiles-dir", type=Path, default=PROFILES_DIR)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    args = parser.parse_args()

    schema = load_json(args.schema)
    errors: list[str] = []

    for filename in EXPECTED_PROFILES:
      path = args.profiles_dir / filename
      if not path.exists():
          errors.append(f"missing profile: {path}")
          continue
      data = load_yaml(path)
      profile_errors = validate_with_jsonschema(schema, data)
      errors.extend([f"{filename}: {msg}" for msg in profile_errors])

    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1

    print(json.dumps({"valid": True, "profiles": EXPECTED_PROFILES}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
