#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

PHASE_NUMBER_RE = re.compile(r"Phase\s+(\d+)", re.IGNORECASE)


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


def is_completed_claim(backlog_path: Path, line_no: int) -> bool:
    lines = backlog_path.read_text(encoding="utf-8").splitlines()
    line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
    return "[x]" in line.lower() or "✅" in line


def phase_sort_key(phase_label: str) -> tuple[int, str]:
    m = PHASE_NUMBER_RE.search(phase_label)
    return (int(m.group(1)), phase_label) if m else (10**9, phase_label)


def build_repo_truth(root: Path, refs: list[dict], ignored: set[str]) -> dict:
    missing: list[dict] = []
    stale_claims: list[dict] = []
    existing: list[dict] = []
    phase_stats: dict[str, dict] = defaultdict(lambda: {"total": 0, "existing": 0, "missing": 0})

    for ref in refs:
        if ref["path"] in ignored:
            continue
        phase = ref["phase"]
        phase_stats[phase]["total"] += 1
        target = root / ref["path"]
        if not target.exists():
            missing.append(ref)
            phase_stats[phase]["missing"] += 1
            continue

        existing.append(ref)
        phase_stats[phase]["existing"] += 1
        backlog_file = root / ref["backlog_file"]
        if is_completed_claim(backlog_file, ref["line"]) and target.stat().st_size == 0:
            stale_claims.append(ref)

    phases = []
    for phase, stats in sorted(phase_stats.items(), key=lambda item: phase_sort_key(item[0])):
        complete = stats["total"] > 0 and stats["missing"] == 0
        phases.append({"phase": phase, **stats, "complete": complete})

    status = "pass" if not missing and not stale_claims else "fail"
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "reference_count": len(refs),
        "checked_count": len(existing) + len(missing),
        "existing_count": len(existing),
        "missing_count": len(missing),
        "stale_claim_count": len(stale_claims),
        "phase_count": len(phases),
        "phase_completion_count": sum(1 for p in phases if p["complete"]),
        "phase_stats": phases,
        "missing": missing,
        "stale_claims": stale_claims,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ignore-file", type=Path, default=Path(".backlog-truth-ignore.yaml"))
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    root = args.root
    refs = load_refs(root)
    ignored = load_ignore(root / args.ignore_file)
    truth = build_repo_truth(root, refs, ignored)

    if args.json_out:
        out_path = root / args.json_out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(truth, indent=2) + "\n", encoding="utf-8")

    if truth["status"] == "fail":
        if truth["missing"]:
            print(f"Missing required referenced paths: {truth['missing_count']}")
            for ref in truth["missing"][:200]:
                print(f"- {ref['path']} ({ref['backlog_file']}:{ref['line']}, {ref['phase']})")
        if truth["stale_claims"]:
            print(f"Stale completion claims: {truth['stale_claim_count']}")
            for ref in truth["stale_claims"][:200]:
                print(f"- {ref['path']} ({ref['backlog_file']}:{ref['line']}, {ref['phase']})")
        return 2

    print(f"Backlog truth valid ({truth['checked_count']} references checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
