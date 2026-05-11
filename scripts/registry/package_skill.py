#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tarfile
from datetime import datetime, UTC
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-dir", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--dist-dir", default="dist/skills")
    args = p.parse_args()

    skill_dir = Path(args.skill_dir)
    skill = skill_dir.name
    dist = Path(args.dist_dir)
    dist.mkdir(parents=True, exist_ok=True)
    locks_dir = Path("skill_registry/locks")
    locks_dir.mkdir(parents=True, exist_ok=True)

    artifact = dist / f"{skill}-{args.version}.tar.gz"
    with tarfile.open(artifact, "w:gz") as tf:
        tf.add(skill_dir, arcname=skill)
    digest = sha256_file(artifact)
    now = datetime.now(UTC).isoformat()

    package_meta = {
        "skill": skill,
        "version": args.version,
        "artifact": str(artifact),
        "sha256": digest,
        "created_at": now,
    }
    (artifact.with_suffix(artifact.suffix + ".json")).write_text(json.dumps(package_meta, indent=2) + "\n")

    lock = {
        "schema_version": "1",
        "skill": skill,
        "version": args.version,
        "artifact": str(artifact),
        "sha256": digest,
        "resolved_at": now,
    }
    (locks_dir / f"{skill}.lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    print(json.dumps(lock))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
