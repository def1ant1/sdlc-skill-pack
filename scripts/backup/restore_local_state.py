#!/usr/bin/env python3
"""Restore local runtime backup with dry-run preview and validation."""
from __future__ import annotations

import argparse
import hashlib
import tarfile
from pathlib import Path

SECRET_MARKERS = (".env", "secret", "secrets", "token", "key", "credential")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def looks_secret(path: str) -> bool:
    p = path.lower()
    return any(marker in p for marker in SECRET_MARKERS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    parser.add_argument("--target", default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-encrypted-secrets", action="store_true")
    parser.add_argument("--approval-ticket")
    args = parser.parse_args()

    if args.include_encrypted_secrets and not args.approval_ticket:
        raise SystemExit("--approval-ticket is required when including encrypted secrets")

    target = Path(args.target).resolve()
    archive = Path(args.archive).resolve()

    restored = 0
    skipped = 0
    with tarfile.open(archive, "r:gz") as tf:
        members = [m for m in tf.getmembers() if m.isfile()]
        print("Restore preview:")
        for m in members:
            if looks_secret(m.name) and not args.include_encrypted_secrets:
                print(f"SKIP_SECRET {m.name}")
                skipped += 1
                continue
            dest = target / m.name
            action = "OVERWRITE" if dest.exists() else "CREATE"
            print(f"{action} {m.name} ({m.size} bytes)")
            if not args.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                src = tf.extractfile(m)
                if src is None:
                    raise SystemExit(f"unable to extract {m.name}")
                data = src.read()
                dest.write_bytes(data)
                extracted_hash = hashlib.sha256(data).hexdigest()
                if file_sha256(dest) != extracted_hash:
                    raise SystemExit(f"checksum validation failed after restore for {m.name}")
            restored += 1

    print(f"restored={restored}")
    print(f"skipped={skipped}")
    print("mode=dry-run" if args.dry_run else "mode=live")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
