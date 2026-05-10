#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re

import yaml

ROOT = Path('.')
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return {}
    return yaml.safe_load(text.split('---', 2)[1]) or {}


def slug(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


manifests = sorted((ROOT / 'core').glob('*/SKILL.md')) + sorted((ROOT / 'skills').glob('*/SKILL.md'))
nodes = []
edges = []
name_index = {}

for manifest in manifests:
    fm = parse_frontmatter(manifest)
    name = fm.get('name', manifest.parent.name)
    path = str(manifest.parent)
    skill_type = 'core' if path.startswith('core/') else 'skill'
    deps = (fm.get('metadata') or {}).get('dependencies', fm.get('dependencies', [])) or []
    deps = [d for d in deps if isinstance(d, str) and d.strip()]

    node = {'name': name, 'path': path, 'type': skill_type, 'dependencies': deps}
    nodes.append(node)
    name_index[name] = node

for node in nodes:
    for dep in node['dependencies']:
        edges.append({'from': node['name'], 'to': dep, 'resolved': dep in name_index})

graph = {
    'nodes': nodes,
    'edges': edges,
    'stats': {
        'node_count': len(nodes),
        'edge_count': len(edges),
        'unresolved_dependencies': sum(1 for e in edges if not e['resolved']),
    },
}

(REPORTS / 'skill_dependency_graph.json').write_text(json.dumps(graph, indent=2) + '\n', encoding='utf-8')

mmd_lines = ['graph TD']
for node in nodes:
    mmd_lines.append(f"  {slug(node['name'])}[\"{node['name']}\"]")
for edge in edges:
    style = ' --> ' if edge['resolved'] else ' -.-> '
    mmd_lines.append(f"  {slug(edge['from'])}{style}{slug(edge['to'])}")
(REPORTS / 'skill_dependency_graph.mmd').write_text('\n'.join(mmd_lines) + '\n', encoding='utf-8')

core_nodes = sum(1 for n in nodes if n['type'] == 'core')
skill_nodes = len(nodes) - core_nodes
unresolved = [e for e in edges if not e['resolved']]

orchestration = [
    '# Orchestration Map',
    '',
    '## Artifact Outputs',
    '- `reports/skill_dependency_graph.json`',
    '- `reports/skill_dependency_graph.mmd`',
    '- `reports/orchestration_map.md`',
    '',
    '## Summary',
    f'- Total nodes: {len(nodes)} (core: {core_nodes}, skills: {skill_nodes})',
    f'- Total dependencies: {len(edges)}',
    f'- Unresolved dependencies: {len(unresolved)}',
    '',
    '## Orchestration Guidance',
    '1. Resolve unresolved dependencies before execution planning.',
    '2. Use topological ordering where graph is acyclic.',
    '3. Route to collision analysis when two skills share overlapping triggers.',
]
if unresolved:
    orchestration.extend(['', '## Unresolved Dependencies'])
    orchestration.extend([f"- `{e['from']}` -> `{e['to']}`" for e in unresolved[:50]])

(REPORTS / 'orchestration_map.md').write_text('\n'.join(orchestration) + '\n', encoding='utf-8')
print('generated reports')
