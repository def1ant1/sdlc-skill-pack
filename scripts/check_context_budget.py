#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import yaml

DEFAULT_BUDGETS = {"L1": 2000, "L2": 8000, "L3": 16000}


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def check_skill(path: Path) -> list[str]:
    errors: list[str] = []
    fm = load_frontmatter(path)
    cl = fm.get("context_loading") or {}
    default_level = cl.get("default_level", "L2")

    if default_level not in DEFAULT_BUDGETS:
        errors.append(f"{path}: invalid default_level '{default_level}'")
        default_level = "L2"

    levels = cl.get("levels") or {}
    for level, cap in DEFAULT_BUDGETS.items():
        level_cfg = levels.get(level) or {}
        max_tokens = level_cfg.get("max_tokens", cap)
        if not isinstance(max_tokens, int):
            errors.append(f"{path}: {level} max_tokens must be integer")
            continue
        if max_tokens > cap:
            errors.append(f"{path}: {level} max_tokens {max_tokens} exceeds cap {cap}")

    effective_default = (levels.get(default_level) or {}).get("max_tokens", DEFAULT_BUDGETS[default_level])
    if isinstance(effective_default, int) and effective_default > DEFAULT_BUDGETS[default_level]:
        errors.append(
            f"{path}: default_level {default_level} uses {effective_default}, exceeds cap {DEFAULT_BUDGETS[default_level]}"
        )

    for field in ("use_when", "do_not_use_when"):
        value = fm.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{path}: missing or empty {field}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate context loading budgets in skill manifests")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root)
    manifests = sorted((root / "core").glob("*/SKILL.md")) + sorted((root / "skills").glob("*/SKILL.md"))

    errors: list[str] = []
    for manifest in manifests:
        errors.extend(check_skill(manifest))

    print(json.dumps({"valid": not errors, "checked": len(manifests), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
