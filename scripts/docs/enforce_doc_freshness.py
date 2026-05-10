#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_AGE_DAYS = 120
KEY_DOCS = [
    ROOT / "APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "docs/standards/documentation-governance.md",
]
DATE_RE = re.compile(r"last_updated\s*:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)


def get_last_updated(text: str) -> dt.date | None:
    m = DATE_RE.search(text)
    if not m:
        return None
    return dt.date.fromisoformat(m.group(1))


def main() -> int:
    today = dt.date.today()
    failures = 0
    for path in KEY_DOCS:
        if not path.exists():
            print(f"Missing key doc: {path.relative_to(ROOT)}")
            failures += 1
            continue
        text = path.read_text(encoding="utf-8")
        stamp = get_last_updated(text)
        if stamp is None:
            print(f"Missing last_updated metadata: {path.relative_to(ROOT)}")
            failures += 1
            continue
        age = (today - stamp).days
        if age > MAX_AGE_DAYS:
            print(
                f"Stale doc ({age} days): {path.relative_to(ROOT)} "
                f"last_updated={stamp.isoformat()}"
            )
            failures += 1

    if failures:
        print(f"\nDocumentation freshness check failed with {failures} issue(s).")
        return 1
    print("Documentation freshness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
