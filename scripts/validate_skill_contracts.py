#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "skill-manifest-v9.schema.json"
REQUIRED = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["required"]
VALID_TYPES = {"core", "skill", "agent", "workflow"}


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3:end + 1]) or {}


def validate_manifest(manifest: dict, path: Path, expected_type: str) -> list[str]:
    errors: list[str] = []
    manifest_type = manifest.get("type", expected_type)
    for key in REQUIRED:
        if key not in manifest:
            errors.append(f"{path}: missing {key}")
    if manifest_type not in VALID_TYPES:
        errors.append(f"{path}: invalid type '{manifest_type}'")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)

    errors: list[str] = []
    for top, expected in (("core", "core"), ("skills", "skill"), ("agents", "agent")):
        directory = root / top
        if not directory.exists():
            continue
        for entry in sorted(directory.iterdir(), key=lambda p: p.name):
            skill_doc = entry / "SKILL.md"
            if entry.is_dir() and skill_doc.exists():
                manifest = parse_frontmatter(skill_doc)
                errors.extend(validate_manifest(manifest, skill_doc, expected))

    if errors:
        print("\n".join(errors))
        return 1

    print("All skill contracts valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
