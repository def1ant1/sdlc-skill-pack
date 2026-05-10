#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def lines(path: Path) -> list[str]:
    return path.read_text(encoding='utf-8').splitlines()


def fail(msg: str) -> None:
    print(msg)


def find_line(path: Path, pattern: str) -> tuple[int, str] | None:
    for i, line in enumerate(lines(path), start=1):
        if re.search(pattern, line):
            return i, line
    return None


def current_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    failures: list[str] = []

    readme = ROOT / 'README.md'
    expected_readme = f"**Current Version:** `{version}`"
    rm = find_line(readme, re.escape(expected_readme))
    if not rm:
        hint = find_line(readme, r"Current Version")
        if hint:
            failures.append(f"README version mismatch: {readme}:{hint[0]} has '{hint[1]}' expected '{expected_readme}'")
        else:
            failures.append(f"README version missing: expected line '{expected_readme}' in {readme}:1")

    changelog = ROOT / 'CHANGELOG.md'
    cm = find_line(changelog, rf"^## \[{re.escape(version)}\]")
    if not cm:
        failures.append(f"Changelog entry missing: expected heading '## [{version}]' in {changelog}:1")

    notes = ROOT / 'RELEASE_NOTES.md'
    nm = find_line(notes, rf"^## v{re.escape(version)}\b")
    if not nm:
        failures.append(f"Release notes missing: expected heading '## v{version}' in {notes}:1")

    sha = current_sha()
    reports = sorted((ROOT / 'reports').glob('*'))
    sha_present = []
    for p in reports:
        if p.is_file() and sha in p.read_text(encoding='utf-8', errors='ignore'):
            sha_present.append(p)
    if not sha_present:
        failures.append(f"Report traceability mismatch: commit SHA {sha} not found in any reports/* file. Run scripts/generate_release_reports.py.")

    if failures:
        for f in failures:
            fail(f"ERROR: {f}")
        return 1

    print(f"PASS: release artifacts validated for version {version} and commit {sha}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
