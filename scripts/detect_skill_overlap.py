#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re

ROOT=Path('.')
OUT=ROOT/'reports/routing_collision_report.md'

def parse_fm(p:Path):
    t=p.read_text(encoding='utf-8')
    if not t.startswith('---'): return {}
    import yaml
    return yaml.safe_load(t.split('---',2)[1]) or {}

skills=[]
for p in list((ROOT/'core').glob('*/SKILL.md'))+list((ROOT/'skills').glob('*/SKILL.md')):
    fm=parse_fm(p)
    skills.append({"name":fm.get('name',p.parent.name),"path":str(p.parent),"use_when":fm.get('use_when',[]),"domain":(fm.get('metadata') or {}).get('category','unknown'),"deps":(fm.get('metadata') or {}).get('dependencies',[])})

collisions=[]
for i,a in enumerate(skills):
    ta={x.strip().lower() for x in a['use_when'] if isinstance(x,str)}
    for b in skills[i+1:]:
        tb={x.strip().lower() for x in b['use_when'] if isinstance(x,str)}
        inter=ta & tb
        if inter:
            collisions.append((a['name'],b['name'],sorted(inter)[:2]))

# cycle detection
adj={s['name']:s['deps'] for s in skills}
seen=set(); stack=set(); cycles=[]

def dfs(n,path):
    if n in stack:
        i=path.index(n); cycles.append(path[i:]+[n]); return
    if n in seen: return
    seen.add(n); stack.add(n)
    for m in adj.get(n,[]) or []: dfs(m,path+[m])
    stack.remove(n)
for n in adj: dfs(n,[n])

OUT.write_text('# Routing Collision Report\n\n'
+f'- Skills scanned: {len(skills)}\n'
+f'- Trigger collisions: {len(collisions)}\n'
+f'- Dependency cycles: {len(cycles)}\n\n'
+'## Trigger Collisions\n'
+('\n'.join([f"- `{a}` vs `{b}` overlap on {k}" for a,b,k in collisions[:100]]) or '- None detected\n')
+'\n## Duplicate Capabilities\n- Heuristic: trigger collisions approximate duplicate capabilities.\n'
+'\n## Dependency Cycles\n'
+('\n'.join([f"- {' -> '.join(c)}" for c in cycles[:20]]) or '- None detected\n')
+'\n## Ambiguous Domain Ownership\n- Skills with `metadata.category: unknown` require explicit ownership review.\n')
print('wrote',OUT)
