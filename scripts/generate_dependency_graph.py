#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT=Path('.')
REPORTS=ROOT/'reports'; REPORTS.mkdir(exist_ok=True)

def parse_fm(p:Path):
    t=p.read_text(encoding='utf-8')
    if not t.startswith('---'): return {}
    fm=t.split('---',2)[1]
    import yaml
    return yaml.safe_load(fm) or {}

nodes=[]; edges=[]
for p in list((ROOT/'core').glob('*/SKILL.md'))+list((ROOT/'skills').glob('*/SKILL.md')):
    fm=parse_fm(p)
    name=fm.get('name',p.parent.name)
    deps=(fm.get('metadata') or {}).get('dependencies',[]) or fm.get('dependencies',[])
    nodes.append({"name":name,"path":str(p.parent),"type":"core" if 'core/' in str(p) else 'skill'})
    for d in deps:
        edges.append({"from":name,"to":d})

graph={"nodes":nodes,"edges":edges,"stats":{"node_count":len(nodes),"edge_count":len(edges)}}
(REPORTS/'skill_dependency_graph.json').write_text(json.dumps(graph,indent=2)+"\n")

lines=["graph TD"]
for e in edges:
    lines.append(f"  {re.sub(r'[^A-Za-z0-9_]','_',e['from'])} --> {re.sub(r'[^A-Za-z0-9_]','_',e['to'])}")
(REPORTS/'skill_dependency_graph.mmd').write_text("\n".join(lines)+"\n")

(REPORTS/'orchestration_map.md').write_text(f"""# Orchestration Map\n\nGenerated dependency artifacts:\n- `reports/skill_dependency_graph.json`\n- `reports/skill_dependency_graph.mmd`\n\n## Summary\n- Nodes: {len(nodes)}\n- Edges: {len(edges)}\n\n## Notes\nUse this map to enforce deterministic ordering and to detect unresolved dependencies during planning.\n""")
print('generated reports')
