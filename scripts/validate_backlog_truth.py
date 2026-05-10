#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
import yaml


def load_refs(root: Path) -> list[dict]:
    out=subprocess.run([sys.executable,str(root/'scripts'/'extract_backlog_paths.py'),'--root',str(root)],capture_output=True,text=True,check=True)
    return json.loads(out.stdout)


def load_ignore(path: Path) -> set[str]:
    if not path.exists(): return set()
    data=yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    return set(data.get('ignore_paths',[]))


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path.cwd())
    ap.add_argument('--ignore-file',type=Path,default=Path('.backlog-truth-ignore.yaml'))
    args=ap.parse_args(); root=args.root
    rows=load_refs(root); ignore=load_ignore(root/args.ignore_file)
    missing=[]
    for r in rows:
        p=r['path']
        if p in ignore: continue
        if not (root/p).exists(): missing.append(r)
    if missing:
        print(f"Missing required referenced paths: {len(missing)}")
        for r in missing[:200]:
            print(f"- {r['path']} ({r['file']}:{r['line']}, {r['phase']})")
        return 1
    print(f"All referenced backlog paths exist ({len(rows)} references checked).")
    return 0

if __name__=='__main__': raise SystemExit(main())
