#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import yaml, json
REQ=json.loads((Path(__file__).resolve().parent.parent/'schemas'/'skill-manifest-v9.schema.json').read_text())['required']
DEFAULTS={k: ([] if k.endswith('s') or k in {'dependencies','activation_triggers','required_context','optional_context','telemetry_events','eval_metrics','integration_targets','data_contracts','failure_modes','fallbacks'} else None) for k in REQ}
DEFAULTS.update({'version':'9.0.0','maturity':'draft','name':'','type':'skill','domain':None,'subdomain':None})

def process(path:Path,dry:bool=False):
    t=path.read_text(encoding='utf-8')
    if not t.startswith('---'): return False
    end=t.find('\n---',3)
    if end==-1:return False
    fm=yaml.safe_load(t[3:end+1]) or {}
    for k,v in DEFAULTS.items(): fm.setdefault(k,v)
    new='---\n'+yaml.safe_dump(fm,sort_keys=False).strip()+'\n---'+t[end+4:]
    if not dry: path.write_text(new,encoding='utf-8')
    return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); ap.add_argument('--dry-run',action='store_true'); a=ap.parse_args()
    c=0
    for p in (a.root).glob('**/SKILL.md'):
        if any(seg in {'core','skills','agents'} for seg in p.parts):
            c += 1 if process(p,a.dry_run) else 0
    print(f'Processed {c} files')
if __name__=='__main__': main()
