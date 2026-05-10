#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

PHASE_RE = re.compile(r"^##\s+Phase\s+(\d+)\b", re.IGNORECASE)
PATH_RE = re.compile(r"(?<![\w/.-])((?:core|skills|agents|scripts|schemas|reports|references|tests)/[A-Za-z0-9_./-]+)")


def extract(root: Path) -> list[dict]:
    results=[]
    for file in sorted(root.glob("*BACKLOG*.md")):
        phase=None
        for i,line in enumerate(file.read_text(encoding='utf-8').splitlines(),start=1):
            m=PHASE_RE.match(line.strip())
            if m: phase=f"Phase {m.group(1)}"
            for pm in PATH_RE.finditer(line):
                results.append({"file":str(file.relative_to(root)),"line":i,"phase":phase,"path":pm.group(1).rstrip('.,:`')})
    return results


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path.cwd())
    ap.add_argument("--format",choices=["json","tsv"],default="json")
    args=ap.parse_args()
    rows=extract(args.root)
    if args.format=="json":
        print(json.dumps(rows,indent=2))
    else:
        print("phase\tpath\tfile\tline")
        for r in rows:
            print(f"{r['phase'] or ''}\t{r['path']}\t{r['file']}\t{r['line']}")
    return 0

if __name__=='__main__': raise SystemExit(main())
