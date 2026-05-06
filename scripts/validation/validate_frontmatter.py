#!/usr/bin/env python3
"""Validate basic skill YAML frontmatter."""
from pathlib import Path
import re, sys, json
try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
errors = []
name_re = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
for skill in list((ROOT/'skills').glob('*/SKILL.md')) + list((ROOT/'core').glob('*/SKILL.md')):
    text = skill.read_text(encoding='utf-8')
    if not text.startswith('---'):
        errors.append(f'{skill}: missing opening frontmatter delimiter')
        continue
    parts = text.split('---', 2)
    if len(parts) < 3:
        errors.append(f'{skill}: missing closing frontmatter delimiter')
        continue
    fm = parts[1]
    if '<' in fm or '>' in fm:
        errors.append(f'{skill}: frontmatter contains forbidden angle bracket')
    if yaml:
        data = yaml.safe_load(fm) or {}
        if 'name' not in data or 'description' not in data:
            errors.append(f'{skill}: name and description required')
        elif not name_re.match(str(data['name'])):
            errors.append(f'{skill}: invalid skill name {data['name']}')
        elif len(str(data['description'])) > 1024:
            errors.append(f'{skill}: description exceeds 1024 characters')
print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
sys.exit(1 if errors else 0)
