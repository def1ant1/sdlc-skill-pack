#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml


def load_refs(root: Path) -> list[dict]:
    out = subprocess.run(
        [sys.executable, str(root / "scripts" / "extract_backlog_paths.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


def load_ignore(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return set(data.get("ignore_paths", []))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ignore-file", type=Path, default=Path(".backlog-truth-ignore.yaml"))
    args = parser.parse_args()

    root = args.root
    refs = load_refs(root)
    ignored = load_ignore(root / args.ignore_file)

    missing: list[dict] = []
    for ref in refs:
        if ref["path"] in ignored:
            continue
        if not (root / ref["path"]).exists():
            missing.append(ref)

    if missing:
        print(f"Missing required referenced paths: {len(missing)}")
        for ref in missing[:200]:
            print(
                f"- {ref['path']} ({ref['backlog_file']}:{ref['line']}, {ref['phase']})"
            )
        return 2

    print(f"All referenced backlog paths exist ({len(refs)} references checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
