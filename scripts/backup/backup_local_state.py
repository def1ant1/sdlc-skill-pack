#!/usr/bin/env python3
"""Create local state backups with manifest + checksums.

Coverage:
- runtime runs/artifacts/reports
- schedule runs
- qdrant data
- local app volumes
- PostgreSQL dumps (when configured)
- config snapshots (excluding known secrets)
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SECRET_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "private_key",
    "client_secret",
    "access_key",
}


@dataclass
class BackupTarget:
    name: str
    source: Path
    mode: str = "copy"  # copy|pg_dump


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_secret_path(path: Path) -> bool:
    lowered = str(path).lower()
    return any(k in lowered for k in SECRET_KEYS)


def safe_copy_tree(src: Path, dst: Path, *, include_secrets: bool) -> dict[str, Any]:
    copied = 0
    skipped: list[str] = []
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        out = dst / rel
        if p.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue
        if not include_secrets and is_secret_path(p):
            skipped.append(str(rel))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        copied += 1
    return {"files_copied": copied, "files_skipped": skipped}


def pg_dump(target_dir: Path, name: str, dsn_env: str = "DATABASE_URL") -> Path:
    dsn = os.getenv(dsn_env)
    if not dsn:
        raise RuntimeError(f"{dsn_env} not set; cannot run pg_dump")
    out = target_dir / f"{name}.sql"
    subprocess.run(["pg_dump", dsn, "-f", str(out)], check=True)
    return out


def build_targets(root: Path) -> list[BackupTarget]:
    return [
        BackupTarget("runtime_runs", root / "runs"),
        BackupTarget("runtime_artifacts", root / "artifacts"),
        BackupTarget("runtime_reports", root / "reports"),
        BackupTarget("schedule_runs", root / "schedules" / "runs"),
        BackupTarget("qdrant_data", root / "qdrant"),
        BackupTarget("local_app_volumes", root / "volumes"),
        BackupTarget("config_snapshot", root / "config"),
        BackupTarget("postgres_dump", root / "postgres", mode="pg_dump"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="backups")
    parser.add_argument("--name", default=None)
    parser.add_argument(
        "--allow-secrets",
        action="store_true",
        help="Requires --encrypted-secrets and approval acknowledgment.",
    )
    parser.add_argument("--encrypted-secrets", action="store_true")
    parser.add_argument("--approval-ticket", default="")
    args = parser.parse_args()

    if args.allow_secrets and (not args.encrypted_secrets or not args.approval_ticket.strip()):
        raise SystemExit(
            "Refusing secret inclusion: provide both --encrypted-secrets and --approval-ticket."
        )

    root = Path(args.root).resolve()
    output_root = Path(args.output).resolve()
    stamp = args.name or dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_dir = output_root / f"local-state-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "created_at_utc": dt.datetime.utcnow().isoformat() + "Z",
        "root": str(root),
        "policy": {
            "secrets_allowed": bool(args.allow_secrets),
            "encrypted_secrets": bool(args.encrypted_secrets),
            "approval_ticket": args.approval_ticket,
        },
        "entries": [],
    }

    for t in build_targets(root):
        if t.mode == "pg_dump":
            try:
                dump_file = pg_dump(backup_dir, t.name)
                manifest["entries"].append(
                    {
                        "name": t.name,
                        "mode": "pg_dump",
                        "path": str(dump_file.relative_to(backup_dir)),
                    }
                )
            except Exception as exc:
                manifest["entries"].append({"name": t.name, "status": "skipped", "reason": str(exc)})
            continue

        if not t.source.exists():
            manifest["entries"].append({"name": t.name, "status": "missing", "source": str(t.source)})
            continue

        target_dir = backup_dir / t.name
        target_dir.mkdir(parents=True, exist_ok=True)
        stats = safe_copy_tree(t.source, target_dir, include_secrets=args.allow_secrets)
        manifest["entries"].append(
            {
                "name": t.name,
                "mode": "copy",
                "source": str(t.source),
                "path": str(target_dir.relative_to(backup_dir)),
                **stats,
            }
        )

    checksums: dict[str, str] = {}
    for f in backup_dir.rglob("*"):
        if f.is_file() and f.name not in {"manifest.json", "checksums.sha256"}:
            checksums[str(f.relative_to(backup_dir))] = sha256_file(f)

    manifest_path = backup_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    checksum_path = backup_dir / "checksums.sha256"
    checksum_path.write_text("\n".join(f"{h}  {p}" for p, h in sorted(checksums.items())) + "\n", encoding="utf-8")

    archive_path = output_root / f"local-state-{stamp}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(backup_dir, arcname=backup_dir.name)

    print(json.dumps({"backup_dir": str(backup_dir), "archive": str(archive_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
