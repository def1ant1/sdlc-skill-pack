#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validation.validate_json_schema import validate

SKILL_SCHEMA = ROOT / "schemas" / "skill.yaml.schema.json"
MANIFEST_SCHEMA = ROOT / "schemas" / "skill-manifest-v9.schema.json"

REQUIRED_MANIFEST_PATHS = [
    "metadata.token_budget",
    "metadata.governance",
    "metadata.load_modes",
]


def _load(path: Path) -> Any:
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def _has_path(obj: dict[str, Any], dotted: str) -> bool:
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


def validate_skill_file(path: Path, schema_path: Path) -> list[str]:
    doc = _load(path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return validate(doc, schema, strict=True, root_schema=schema, schema_file=schema_path)


def validate_manifest_extension(path: Path) -> list[str]:
    doc = _load(path)
    errors: list[str] = []
    for dotted in REQUIRED_MANIFEST_PATHS:
        if not _has_path(doc, dotted):
            errors.append(f"$.{dotted}: missing required field for skill.yaml parity")

    load_modes = doc.get("metadata", {}).get("load_modes", [])
    if "metadata_only" not in load_modes:
        errors.append("$.metadata.load_modes: must include 'metadata_only'")
    return errors


def discover_mvp_skill_manifests(root: Path) -> list[Path]:
    return sorted((root / "skills").glob("*/manifest.v9.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill.yaml and MVP manifest parity requirements.")
    parser.add_argument("--skill-file", action="append", default=[], help="Path to a skill.yaml file")
    parser.add_argument("--manifest-file", action="append", default=[], help="Path to a manifest.v9.json file")
    parser.add_argument("--mvp", action="store_true", help="Validate discovered MVP skill manifests")
    args = parser.parse_args()

    skill_files = [Path(p) for p in args.skill_file]
    manifest_files = [Path(p) for p in args.manifest_file]
    if args.mvp:
        manifest_files.extend(discover_mvp_skill_manifests(ROOT))

    errors: list[str] = []
    checked: list[str] = []

    for skill in skill_files:
        checked.append(str(skill))
        errors.extend([f"{skill}: {e}" for e in validate_skill_file(skill, SKILL_SCHEMA)])

    for manifest in manifest_files:
        checked.append(str(manifest))
        errors.extend([f"{manifest}: {e}" for e in validate_skill_file(manifest, MANIFEST_SCHEMA)])
        errors.extend([f"{manifest}: {e}" for e in validate_manifest_extension(manifest)])

    result = {"valid": not errors, "checked": len(checked), "files": checked, "errors": errors}
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
