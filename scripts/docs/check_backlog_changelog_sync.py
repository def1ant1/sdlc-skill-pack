#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKLOG = ROOT / "APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md"
CHANGELOG = ROOT / "CHANGELOG.md"

PHASE_RE = re.compile(r"^##\s+Phase\s+(\d+)\b", re.IGNORECASE)
DONE_RE = re.compile(r"^(?:-\s*)?✅\s*Implemented", re.IGNORECASE)
NOT_RELEASED_RE = re.compile(r"not\s+released", re.IGNORECASE)


def parse_completed_phases(text: str) -> dict[str, int]:
    phases: dict[str, int] = {}
    current: str | None = None
    for i, line in enumerate(text.splitlines(), start=1):
        m = PHASE_RE.match(line.strip())
        if m:
            current = m.group(1)
            continue
        if current and DONE_RE.search(line):
            phases[current] = i
    return phases


def main() -> int:
    backlog_text = BACKLOG.read_text(encoding="utf-8")
    changelog_text = CHANGELOG.read_text(encoding="utf-8")
    completed = parse_completed_phases(backlog_text)
    failures = 0

    for phase, line in sorted(completed.items(), key=lambda x: int(x[0])):
        p = f"Phase {phase}"
        if re.search(rf"\b{re.escape(p)}\b", changelog_text, re.IGNORECASE):
            continue
        if re.search(rf"\b{re.escape(p)}\b.*{NOT_RELEASED_RE.pattern}", changelog_text, re.IGNORECASE):
            continue
        print(
            f"Missing changelog linkage for completed {p} (backlog line {line}). "
            "Add a changelog entry or an explicit 'not released' marker."
        )
        failures += 1

    if failures:
        print(f"\nBacklog/changelog sync failed with {failures} issue(s).")
        return 1
    print("Backlog/changelog sync passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
