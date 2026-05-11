#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

REQUIRED_PATHS = [
    "core/", "skills/", "agents/", "shared/", "schemas/", "references/", "docs/", "scripts/", "reports/",
    "README.md", "CHANGELOG.md", "RELEASE_NOTES.md", "VERSION", "LICENSE",
]
EXCLUDED_PATTERNS = [
    ".git/*", "**/.git/*", "**/__pycache__/*", "**/.pytest_cache/*", "**/.mypy_cache/*", "**/.ruff_cache/*",
    "**/.cache/*", "**/.DS_Store", "**/.env", "**/.env.*", "**/*.pem", "**/*.key", "**/*secret*",
    "**/*token*", "**/*debug*", "**/*.log", "dist/*",
]

def _is_excluded(path: str) -> bool:
    normalized = path.replace('\\', '/')
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in EXCLUDED_PATTERNS)

def _collect_release_files() -> list[Path]:
    files: list[Path] = []
    for required in REQUIRED_PATHS:
        target = ROOT / required.rstrip('/')
        if not target.exists():
            raise SystemExit(f"Required path missing: {required}")
        if target.is_file():
            rel = target.relative_to(ROOT)
            if not _is_excluded(rel.as_posix()):
                files.append(rel)
            continue
        for path in sorted(target.rglob('*')):
            if path.is_file():
                rel = path.relative_to(ROOT)
                if not _is_excluded(rel.as_posix()):
                    files.append(rel)
    unique_files = sorted(set(files), key=lambda p: p.as_posix())
    if not unique_files:
        raise SystemExit("No files selected for release package.")
    return unique_files

def _build_archive(version: str, files: list[Path]) -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    zip_path = DIST / f"apotheon-skill-pack-v{version}.zip"
    with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as zf:
        for rel in files:
            zf.write(ROOT / rel, arcname=rel.as_posix())
    return zip_path

def _write_sha256(zip_path: Path) -> tuple[Path, str]:
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    sha_path = zip_path.with_suffix('.sha256')
    sha_path.write_text(f"{digest}  {zip_path.name}\n", encoding='utf-8')
    return sha_path, digest

def _write_manifest(version: str, zip_path: Path, digest: str, files: list[Path]) -> Path:
    manifest_path = zip_path.with_suffix('.manifest.json')
    manifest = {
        "package": zip_path.name,
        "version": version,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checksum": {"algorithm": "sha256", "value": digest},
        "file_count": len(files),
        "files": [p.as_posix() for p in files],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding='utf-8')
    return manifest_path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a release artifact for the skill pack.")
    parser.add_argument('--version', required=True)
    return parser.parse_args()

def main() -> int:
    version = parse_args().version.strip()
    files = _collect_release_files()
    zip_path = _build_archive(version, files)
    sha_path, digest = _write_sha256(zip_path)
    manifest_path = _write_manifest(version, zip_path, digest, files)
    print(f"Packaged {len(files)} files into {zip_path.relative_to(ROOT)}")
    print(f"Wrote checksum: {sha_path.relative_to(ROOT)}")
    print(f"Wrote manifest: {manifest_path.relative_to(ROOT)}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
