#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]

ALLOWLIST_PREFIXES = [
    'core/',
    'skills/',
    'agents/',
    'shared/',
    'schemas/',
    'references/',
    'docs/',
    'scripts/',
    'reports/',
]
ALLOWLIST_FILES = {'README.md', 'CHANGELOG.md', 'LICENSE'}
DENYLIST_PATTERNS = [
    '.git/*',
    '**/.git/*',
    '**/__pycache__/*',
    '**/.pytest_cache/*',
    '**/.mypy_cache/*',
    '**/.ruff_cache/*',
    '**/.cache/*',
    '**/.env',
    '**/.env.*',
    '**/*.pem',
    '**/*.key',
    '**/*secret*',
    '**/*token*',
    '**/*debug*',
    '**/*.log',
]
REQUIRED_ENTRIES = set(ALLOWLIST_FILES) | set(ALLOWLIST_PREFIXES)


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _in_allowlist(path: str) -> bool:
    return path in ALLOWLIST_FILES or any(path.startswith(prefix) for prefix in ALLOWLIST_PREFIXES)


def validate_package(zip_path: Path) -> list[str]:
    errors: list[str] = []
    with ZipFile(zip_path, 'r') as zf:
        names = sorted(n for n in zf.namelist() if not n.endswith('/'))

    if not names:
        return [f'{zip_path}: archive is empty']

    present_prefixes = {prefix: False for prefix in ALLOWLIST_PREFIXES}
    present_files = {fname: False for fname in ALLOWLIST_FILES}

    for name in names:
        if _matches_any(name, DENYLIST_PATTERNS):
            errors.append(f'Denylisted entry present: {name}')
        if not _in_allowlist(name):
            errors.append(f'Entry outside allowlist: {name}')

        for prefix in ALLOWLIST_PREFIXES:
            if name.startswith(prefix):
                present_prefixes[prefix] = True
        if name in ALLOWLIST_FILES:
            present_files[name] = True

    for prefix, present in present_prefixes.items():
        if not present:
            errors.append(f'Required prefix missing from archive: {prefix}')

    for fname, present in present_files.items():
        if not present:
            errors.append(f'Required file missing from archive: {fname}')

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Validate release package allowlist/denylist.')
    parser.add_argument('--zip-path', type=Path, required=True, help='Path to release zip archive.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    zip_path = args.zip_path
    if not zip_path.is_absolute():
        zip_path = ROOT / zip_path

    if not zip_path.exists():
        print(f'Archive not found: {zip_path}')
        return 1

    errors = validate_package(zip_path)
    if errors:
        print('Release package validation failed:')
        for err in errors:
            print(f' - {err}')
        return 1

    print(f'Release package validation passed: {zip_path.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
