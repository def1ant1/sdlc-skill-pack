#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
import yaml

REQ=json.loads((Path(__file__).resolve().parent.parent/'schemas'/'skill-manifest-v9.schema.json').read_text())['required']

def frontmatter(path: Path)->dict:
    t=path.read_text(encoding='utf-8')
    if not t.startswith('---'): return {}
    end=t.find('\n---',3)
    if end==-1: return {}
    return yaml.safe_load(t[3:end+1]) or {}

def validate_manifest(m:dict, path:Path)->list[str]:
    errs=[]
    for k in REQ:
        if k not in m: errs.append(f"{path}: missing {k}")
    if 'type' in m and m['type'] not in {'core','skill','agent','workflow'}: errs.append(f"{path}: invalid type")
    return errs

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.')
    args=ap.parse_args(); root=Path(args.root)
    errs=[]
    for top,typ in [('core','core'),('skills','skill'),('agents','agent')]:
        d=root/top
        if not d.exists(): continue
        for skill in d.iterdir():
            sm=skill/'SKILL.md'
            if skill.is_dir() and sm.exists():
                m=frontmatter(sm)
                if 'type' not in m: m['type']=typ
                errs.extend(validate_manifest(m,sm))
    if errs:
        print('\n'.join(errs)); return 1
    print('All skill contracts valid.'); return 0
if __name__=='__main__': raise SystemExit(main())
