#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

REQUIRED_TOP_LEVEL_FIELDS = ("datasets", "metrics", "acceptance_gates")


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3 : end + 1]) or {}


def _is_non_empty_list(value: object) -> bool:
    return isinstance(value, list) and len(value) > 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    skills_dir = root / "skills"
    errors: list[str] = []

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.exists():
            continue

        frontmatter = load_frontmatter(skill_file)
        priority = str(frontmatter.get("priority") or frontmatter.get("metadata", {}).get("priority") or "").upper()
        if priority not in {"P0", "P1"}:
            continue

        spec_path = skill_dir / "eval.spec.json"
        if not spec_path.exists():
            errors.append(f"{skill_dir}: missing eval.spec.json for {priority} skill")
            continue

        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{spec_path}: invalid JSON ({exc})")
            continue

        spec_priority = str(spec.get("priority", "")).upper()
        if spec_priority != priority:
            errors.append(
                f"{spec_path}: priority mismatch skill={priority} eval={spec_priority or 'MISSING'}"
            )

        for field in REQUIRED_TOP_LEVEL_FIELDS:
            if not _is_non_empty_list(spec.get(field)):
                errors.append(
                    f"{spec_path}: {field} must be a non-empty list for {priority} skill eval completeness"
                )

    if errors:
        print("\n".join(errors))
        return 1

    print("All required P0/P1 skill eval specs are present and complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
