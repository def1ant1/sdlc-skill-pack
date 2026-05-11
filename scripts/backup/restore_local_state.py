#!/usr/bin/env python3
"""Restore local state backups with integrity verification and dry-run support."""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(backup_dir: Path) -> list[str]:
    errors: list[str] = []
    checksums = backup_dir / "checksums.sha256"
    if not checksums.exists():
        return ["checksums.sha256 missing"]
    for line in checksums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        file_path = backup_dir / rel
        if not file_path.exists():
            errors.append(f"missing file: {rel}")
            continue
        actual = sha256_file(file_path)
        if actual != expected:
            errors.append(f"checksum mismatch: {rel}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("backup", help="Path to backup dir or .tar.gz archive")
    parser.add_argument("--target-root", default=".")
    parser.add_argument("--dry-run", action="store_true", help="Preview restore actions only")
    args = parser.parse_args()

    backup = Path(args.backup).resolve()
    target_root = Path(args.target_root).resolve()

    temp_dir_obj = None
    if backup.is_file() and backup.suffixes[-2:] == [".tar", ".gz"]:
        temp_dir_obj = tempfile.TemporaryDirectory()
        with tarfile.open(backup, "r:gz") as tar:
            tar.extractall(temp_dir_obj.name)
        dirs = [p for p in Path(temp_dir_obj.name).iterdir() if p.is_dir()]
        if not dirs:
            raise SystemExit("Archive did not contain backup directory")
        backup_dir = dirs[0]
    else:
        backup_dir = backup

    errors = verify(backup_dir)
    if errors:
        raise SystemExit("Integrity check failed:\n- " + "\n- ".join(errors))

    manifest_path = backup_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    planned = []
    for entry in manifest.get("entries", []):
        rel = entry.get("path")
        if not rel:
            continue
        src = backup_dir / rel
        dst = target_root / rel
        planned.append((src, dst))

    if args.dry_run:
        print("DRY RUN: planned restore actions")
        for src, dst in planned:
            print(f"- restore {src} -> {dst}")
        return 0

    for src, dst in planned:
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            for p in src.rglob("*"):
                rel = p.relative_to(src)
                out = dst / rel
                if p.is_dir():
                    out.mkdir(parents=True, exist_ok=True)
                else:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(p.read_bytes())
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())

    print("Restore completed")
    if temp_dir_obj:
        temp_dir_obj.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
