#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

REQUIRED_CATEGORIES = {"runtime", "business"}


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3 : end + 1]) or {}


def validate_event_payload(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    events = payload if isinstance(payload, list) else [payload]

    errors: list[str] = []
    for idx, event in enumerate(events):
        category = str(event.get("event_category", "")).lower()
        if category in REQUIRED_CATEGORIES and not str(event.get("correlation_id", "")).strip():
            errors.append(f"event[{idx}] missing correlation_id for category '{category}'")

    if errors:
        print("\n".join(errors))
        return 1

    print("Telemetry events valid: correlation_id present for runtime/business events.")
    return 0


def validate_skill_telemetry(root: Path) -> int:
    errors: list[str] = []
    for skill_dir in sorted((root / "skills").iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.exists():
            continue
        fm = load_frontmatter(skill_file)
        priority = str(fm.get("priority") or (fm.get("metadata") or {}).get("priority") or "").upper()
        if priority not in {"P0", "P1"}:
            continue

        manifest_file = skill_dir / str((fm.get("metadata") or {}).get("manifest") or "")
        has_contract = bool(fm.get("telemetry_contract"))
        has_manifest_events = False
        if manifest_file.is_file():
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                has_manifest_events = bool(manifest.get("telemetry_events"))
            except json.JSONDecodeError:
                errors.append(f"{manifest_file}: invalid manifest JSON")

        if not has_contract and not has_manifest_events:
            errors.append(
                f"{skill_dir}: missing telemetry declaration for {priority} skill "
                f"(telemetry_contract or manifest telemetry_events required)"
            )

    if errors:
        print("\n".join(errors))
        return 1

    print("All required P0/P1 skill telemetry declarations are present.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", help="Path to JSON file containing telemetry events")
    parser.add_argument("--root", default=".", help="Repository root for skill telemetry validation")
    args = parser.parse_args()

    if args.input:
        return validate_event_payload(Path(args.input))
    return validate_skill_telemetry(Path(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
