#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

PHASE_RE = re.compile(r"^##\s+Phase\s+([0-9]+)\b", re.IGNORECASE)
PATH_RE = re.compile(
    r"(?<![\w/.-])((?:core|skills|agents|scripts|schemas|reports|references|tests)/[A-Za-z0-9_./-]+)"
)


def extract_rows(root: Path) -> list[dict]:
    rows: list[dict] = []
    for file in sorted(root.glob("*BACKLOG*.md")):
        phase = "Unscoped"
        for line_no, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
            phase_match = PHASE_RE.match(line.strip())
            if phase_match:
                phase = f"Phase {phase_match.group(1)}"
            for path_match in PATH_RE.finditer(line):
                rows.append(
                    {
                        "backlog_file": str(file.relative_to(root)),
                        "line": line_no,
                        "phase": phase,
                        "path": path_match.group(1).rstrip(".,:`)"),
                    }
                )
    return rows


def group_rows(rows: list[dict]) -> dict:
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["phase"]][row["backlog_file"]].append(
            {"path": row["path"], "line": row["line"]}
        )
    return {
        phase: {bf: entries for bf, entries in sorted(files.items())}
        for phase, files in sorted(grouped.items())
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=["json", "tsv"], default="json")
    parser.add_argument("--grouped", action="store_true")
    args = parser.parse_args()

    rows = extract_rows(args.root)
    payload = group_rows(rows) if args.grouped else rows
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print("phase\tpath\tbacklog_file\tline")
        for row in rows:
            print(
                f"{row['phase']}\t{row['path']}\t{row['backlog_file']}\t{row['line']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
