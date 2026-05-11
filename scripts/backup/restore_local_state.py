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


def safe_extract_archive(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            member_path = destination / member.name
            resolved = member_path.resolve()
            if member_path.is_absolute() or not str(resolved).startswith(str(destination.resolve())):
                raise SystemExit(f"Unsafe archive member path blocked: {member.name}")
        tar.extractall(destination, members=members)

    dirs = [p for p in destination.iterdir() if p.is_dir()]
    if not dirs:
        raise SystemExit("Archive did not contain backup directory")
    return dirs[0]


def resolve_destination(entry: dict, backup_root: Path, target_root: Path) -> tuple[Path, Path] | None:
    rel = entry.get("path")
    if not rel:
        return None

    src = backup_root / rel
    source_path = entry.get("source")
    manifest_root = entry.get("manifest_root")

    if source_path and manifest_root:
        try:
            source_rel = Path(source_path).resolve().relative_to(Path(manifest_root).resolve())
            return src, target_root / source_rel
        except Exception:
            pass

    if source_path:
        source_name = Path(source_path).name
        return src, target_root / source_name

    return src, target_root / rel


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
        backup_dir = safe_extract_archive(backup, Path(temp_dir_obj.name))
    else:
        backup_dir = backup

    errors = verify(backup_dir)
    if errors:
        raise SystemExit("Integrity check failed:\n- " + "\n- ".join(errors))

    manifest_path = backup_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    planned = []
    manifest_root = manifest.get("root")
    for entry in manifest.get("entries", []):
        entry["manifest_root"] = manifest_root
        mapped = resolve_destination(entry, backup_dir, target_root)
        if mapped:
            planned.append(mapped)

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
