#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
DEFAULT_BUDGETS = {"L1": 2000, "L2": 8000, "L3": 16000}

def load_frontmatter(path: Path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return {}
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}
    import yaml
    return yaml.safe_load(parts[1]) or {}

errors=[]
checked=0
for p in list((ROOT/'core').glob('*/SKILL.md')) + list((ROOT/'skills').glob('*/SKILL.md')):
    fm = load_frontmatter(p)
    cl = fm.get('context_loading', {})
    default_level = cl.get('default_level', 'L2')
    levels = cl.get('levels', {})
    for level in ('L1','L2','L3'):
        max_tokens = ((levels.get(level) or {}).get('max_tokens'))
        if max_tokens is None:
            max_tokens = DEFAULT_BUDGETS[level]
        if max_tokens > DEFAULT_BUDGETS[level]:
            errors.append(f"{p}: {level} max_tokens {max_tokens} exceeds policy cap {DEFAULT_BUDGETS[level]}")
    effective_default = (levels.get(default_level) or {}).get('max_tokens', DEFAULT_BUDGETS[default_level])
    if effective_default > DEFAULT_BUDGETS[default_level]:
        errors.append(f"{p}: default_level {default_level} violates cap {DEFAULT_BUDGETS[default_level]} with {effective_default}")
    checked += 1

print(json.dumps({"valid": not errors, "checked": checked, "errors": errors}, indent=2))
sys.exit(1 if errors else 0)
