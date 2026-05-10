#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import itertools
import yaml

ROOT = Path('.')
OUT = ROOT / 'reports' / 'routing_collision_report.md'


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return {}
    return yaml.safe_load(text.split('---', 2)[1]) or {}


manifests = sorted((ROOT / 'core').glob('*/SKILL.md')) + sorted((ROOT / 'skills').glob('*/SKILL.md'))
skills = []
for manifest in manifests:
    fm = parse_frontmatter(manifest)
    skills.append(
        {
            'name': fm.get('name', manifest.parent.name),
            'path': str(manifest.parent),
            'use_when': [x.strip().lower() for x in (fm.get('use_when') or []) if isinstance(x, str)],
            'do_not_use_when': [x.strip().lower() for x in (fm.get('do_not_use_when') or []) if isinstance(x, str)],
            'domain': (fm.get('metadata') or {}).get('category', 'unknown'),
            'deps': (fm.get('metadata') or {}).get('dependencies', []),
        }
    )

collisions = []
for a, b in itertools.combinations(skills, 2):
    overlap = sorted(set(a['use_when']) & set(b['use_when']))
    if overlap:
        collisions.append((a['name'], b['name'], overlap[:3]))

# cycle detection
adj = {s['name']: [d for d in (s['deps'] or []) if isinstance(d, str)] for s in skills}
visited, active = set(), set()
cycles = []


def dfs(node: str, trail: list[str]) -> None:
    if node in active:
        if node in trail:
            i = trail.index(node)
            cycles.append(trail[i:] + [node])
        return
    if node in visited:
        return
    visited.add(node)
    active.add(node)
    for nxt in adj.get(node, []):
        if nxt in adj:
            dfs(nxt, trail + [nxt])
    active.remove(node)


for node in adj:
    dfs(node, [node])

unknown_domains = [s for s in skills if s['domain'] == 'unknown']
ambiguous_rules = [s for s in skills if not s['do_not_use_when']]

lines = [
    '# Routing Collision Report',
    '',
    '## Summary',
    f"- Skills scanned: {len(skills)}",
    f"- Trigger overlaps: {len(collisions)}",
    f"- Dependency cycles: {len(cycles)}",
    f"- Unknown domain ownership: {len(unknown_domains)}",
    f"- Missing exclusion rules: {len(ambiguous_rules)}",
    '',
    '## Trigger Overlap',
]
if collisions:
    lines.extend([f"- `{a}` vs `{b}` overlap on: {', '.join(keys)}" for a, b, keys in collisions[:150]])
else:
    lines.append('- None detected.')

lines.extend(['', '## Dependency Cycles'])
if cycles:
    lines.extend([f"- {' -> '.join(c)}" for c in cycles[:50]])
else:
    lines.append('- None detected.')

lines.extend(['', '## Ambiguity Signals'])
if unknown_domains:
    lines.extend([f"- `{s['name']}` has `metadata.category: unknown`." for s in unknown_domains[:100]])
if ambiguous_rules:
    lines.extend([f"- `{s['name']}` missing `do_not_use_when` guidance." for s in ambiguous_rules[:100]])
if not unknown_domains and not ambiguous_rules:
    lines.append('- None detected.')

lines.extend([
    '',
    '## Remediation Recommendations',
    '1. Strengthen `use_when` with unique trigger language per domain.',
    '2. Add negative routing constraints in `do_not_use_when` for neighboring skills.',
    '3. Resolve dependency cycles by introducing orchestrator nodes or splitting responsibilities.',
    '4. Assign explicit `metadata.category` ownership for all unknown domains.',
])

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'wrote {OUT}')
