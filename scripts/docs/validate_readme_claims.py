#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

README = Path("README.md")
REQUIRED_REFERENCES = [
    "reports/release_readiness.md",
    "reports/release_readiness.json",
    "reports/skill_inventory.md",
    "reports/hitl_coverage_report.md",
    "reports/test_summary.md",
    "reports/business_skill_coverage.md",
]
BLOCKED_PATTERNS = [
    re.compile(r"\b\d+\s+of\s+\d+\s+skills\b", re.IGNORECASE),
    re.compile(r"\b\d+\+\s+passing\s+tests\b", re.IGNORECASE),
    re.compile(r"\b\d+\s+test files\b", re.IGNORECASE),
    re.compile(r"\b\d+-skill\b", re.IGNORECASE),
]


def main() -> int:
    text = README.read_text(encoding="utf-8")
    missing = [p for p in REQUIRED_REFERENCES if p not in text]
    if missing:
        print("README is missing required generated-report references:")
        for m in missing:
            print(f"- {m}")
        return 1

    violations = []
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(text):
            violations.append(pattern.pattern)
    if violations:
        print("README includes hard-coded numeric claims; source those via generated reports:")
        for v in violations:
            print(f"- {v}")
        return 1

    print("README numeric-claim guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
