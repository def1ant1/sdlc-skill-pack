#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

REQUIRED = json.loads(
    (Path(__file__).resolve().parent.parent / "schemas" / "skill-manifest-v9.schema.json").read_text(encoding="utf-8")
)["required"]

LIST_KEYS = {
    "dependencies", "activation_triggers", "required_context", "optional_context",
    "telemetry_events", "eval_metrics", "integration_targets", "data_contracts",
    "failure_modes", "fallbacks",
}

DEFAULTS = {key: ([] if key in LIST_KEYS else None) for key in REQUIRED}
DEFAULTS.update({"version": "9.0.0", "maturity": "draft", "name": "", "type": "skill"})


def migrate_file(path: Path, dry_run: bool = False) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end == -1:
        return False
    manifest = yaml.safe_load(text[3:end + 1]) or {}
    for key, value in DEFAULTS.items():
        manifest.setdefault(key, value)

    new_text = "---\n" + yaml.safe_dump(manifest, sort_keys=False).strip() + "\n---" + text[end + 4:]
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    count = 0
    for top in ("core", "skills", "agents"):
        base = args.root / top
        if not base.exists():
            continue
        for skill_dir in sorted(base.iterdir(), key=lambda p: p.name):
            skill_file = skill_dir / "SKILL.md"
            if skill_dir.is_dir() and skill_file.exists() and migrate_file(skill_file, args.dry_run):
                count += 1

    print(f"Processed {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
