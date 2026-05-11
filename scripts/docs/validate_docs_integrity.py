#!/usr/bin/env python3
"""Validate documentation link/path consistency and basic command sanity references."""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_RE = re.compile(r"```bash\n(.*?)```", re.DOTALL)


def iter_md_files() -> list[Path]:
    return [p for p in DOCS.rglob("*.md")]


def validate_links(md_file: Path) -> list[str]:
    errors: list[str] = []
    text = md_file.read_text(encoding="utf-8")
    for link in LINK_RE.findall(text):
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (md_file.parent / link).resolve()
        if not target.exists():
            errors.append(f"{md_file.relative_to(ROOT)}: missing link target '{link}'")
    return errors


def validate_commands(md_file: Path) -> list[str]:
    errors: list[str] = []
    text = md_file.read_text(encoding="utf-8")
    for block in CODE_RE.findall(text):
        for line in [ln.strip() for ln in block.splitlines() if ln.strip() and not ln.strip().startswith("#")]:
            parts = line.split()
            candidate = parts[-1]
            if "/" in candidate and not candidate.startswith(("http://", "https://")):
                if any(x in candidate for x in ("=", "<", ">")):
                    continue
                if candidate.startswith((".venv/", "runtime/", "reports/", "workflows/generated/")):
                    continue
                path = (ROOT / candidate).resolve()
                if not path.exists() and not candidate.startswith("<"):
                    errors.append(f"{md_file.relative_to(ROOT)}: command path not found '{candidate}'")
    return errors


def main() -> int:
    errors: list[str] = []
    for md in iter_md_files():
        errors.extend(validate_links(md))
        errors.extend(validate_commands(md))
    if errors:
        print("Documentation integrity check failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Documentation integrity check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
