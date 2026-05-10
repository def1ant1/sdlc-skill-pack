#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import yaml

def fm(path:Path):
    t=path.read_text(encoding='utf-8')
    if not t.startswith('---'): return {}
    e=t.find('\n---',3)
    if e==-1:return {}
    return yaml.safe_load(t[3:e+1]) or {}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path.cwd()); a=ap.parse_args(); rows=[]
    for typ in ['core','skills','agents']:
        d=a.root/typ
        if not d.exists(): continue
        for child in sorted(d.iterdir(), key=lambda p:p.name):
            sk=child/'SKILL.md'
            if child.is_dir() and sk.exists():
                m=fm(sk); rows.append({'category':typ,'id':child.name,'name':m.get('name',child.name),'version':m.get('version'),'owner':m.get('owner'),'maturity':m.get('maturity'),'hitl_gates': len(m.get('hitl_gates') or [])})
    (a.root/'reports').mkdir(exist_ok=True)
    (a.root/'reports'/'skill_inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (a.root/'reports'/'skill_inventory.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['category','id','name','version','owner','maturity','hitl_gates']); w.writeheader(); w.writerows(rows)
    md=['# Skill Inventory','',f'Total: {len(rows)}','', '| category | id | name | version | owner | maturity | hitl_gates |','|---|---|---|---|---|---|---|']
    md += [f"| {r['category']} | {r['id']} | {r['name']} | {r['version'] or ''} | {r['owner'] or ''} | {r['maturity'] or ''} | {r['hitl_gates']} |" for r in rows]
    (a.root/'reports'/'skill_inventory.md').write_text('\n'.join(md)+'\n')
    print(f'Generated inventory for {len(rows)} items')
if __name__=='__main__': main()
