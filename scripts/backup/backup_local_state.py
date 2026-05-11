#!/usr/bin/env python3
"""Create deterministic local runtime backup with manifest/checksums."""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_INCLUDE = [
    "runtime",
    "reports",
    "schedules",
    "local_apps",
    ".env.example",
]
SECRET_MARKERS = (".env", "secret", "secrets", "token", "key", "credential")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def looks_secret(path: Path) -> bool:
    p = str(path).lower()
    return any(marker in p for marker in SECRET_MARKERS)


def collect_files(root: Path, include_encrypted_secrets: bool) -> list[Path]:
    files: list[Path] = []
    for rel in DEFAULT_INCLUDE:
        target = root / rel
        if not target.exists():
            continue
        if target.is_file():
            rel_path = target.relative_to(root)
            if looks_secret(rel_path) and not include_encrypted_secrets:
                continue
            files.append(rel_path)
            continue
        for child in target.rglob("*"):
            if child.is_file():
                rel_path = child.relative_to(root)
                if looks_secret(rel_path) and not include_encrypted_secrets:
                    continue
                files.append(rel_path)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/backups")
    parser.add_argument("--include-encrypted-secrets", action="store_true")
    parser.add_argument("--approval-ticket", help="Required with --include-encrypted-secrets")
    args = parser.parse_args()

    if args.include_encrypted_secrets and not args.approval_ticket:
        raise SystemExit("--approval-ticket is required when including encrypted secrets")

    root = Path.cwd()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"local-state-backup-{stamp}"
    archive = out_dir / f"{name}.tar.gz"
    manifest = out_dir / f"{name}.manifest.json"
    checksums = out_dir / f"{name}.sha256"

    files = collect_files(root, args.include_encrypted_secrets)
    manifest_data = {
        "created_at_utc": stamp,
        "root": str(root),
        "include_encrypted_secrets": args.include_encrypted_secrets,
        "approval_ticket": args.approval_ticket,
        "files": [],
    }

    with tarfile.open(archive, "w:gz") as tf, checksums.open("w", encoding="utf-8") as chk:
        for rel in files:
            abs_path = root / rel
            sha = file_sha256(abs_path)
            size = abs_path.stat().st_size
            tf.add(abs_path, arcname=str(rel))
            manifest_data["files"].append({"path": str(rel), "size": size, "sha256": sha})
            chk.write(f"{sha}  {rel}\n")

    manifest.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    print(f"archive={archive}")
    print(f"manifest={manifest}")
    print(f"checksums={checksums}")
    print(f"files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
