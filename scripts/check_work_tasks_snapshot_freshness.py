#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "V9_OPEN_WORK_TASKS.md"
SOURCE = ROOT / "reports" / "release_readiness.md"


def main() -> int:
    if not SNAPSHOT.exists() or not SOURCE.exists():
        print("Required files missing for freshness check.")
        return 2
    if SNAPSHOT.stat().st_mtime < SOURCE.stat().st_mtime:
        print("V9_OPEN_WORK_TASKS.md is older than reports/release_readiness.md. Regenerate snapshot.")
        return 2
    print("Work task snapshot freshness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
