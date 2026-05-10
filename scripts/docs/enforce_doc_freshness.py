#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_AGE_DAYS = 120
DATE_RE = re.compile(r"last_updated\s*:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)


def key_docs() -> list[Path]:
    candidates = [
        ROOT / "APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md",
        ROOT / "CHANGELOG.md",
        ROOT / "ROADMAP.md",
        ROOT / "docs/standards/documentation-governance.md",
    ]
    return [p for p in candidates if p.exists()]


def get_last_updated(text: str) -> dt.date | None:
    m = DATE_RE.search(text)
    return dt.date.fromisoformat(m.group(1)) if m else None


def main() -> int:
    today = dt.date.today()
    failures = 0

    for path in key_docs():
        text = path.read_text(encoding="utf-8")
        stamp = get_last_updated(text)
        rel = path.relative_to(ROOT)
        if stamp is None:
            print(f"Missing last_updated metadata: {rel}")
            failures += 1
            continue

        age = (today - stamp).days
        if age > MAX_AGE_DAYS:
            print(f"Stale doc ({age} days): {rel} last_updated={stamp.isoformat()}")
            failures += 1

    if failures:
        print(f"\nDocumentation freshness check failed with {failures} issue(s).")
        return 1

    print("Documentation freshness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
