#!/usr/bin/env python3
"""Create a basic skill scaffold."""
from pathlib import Path
import argparse, re

p = argparse.ArgumentParser()
p.add_argument('name')
p.add_argument('--root', default='.')
a = p.parse_args()
if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', a.name):
    raise SystemExit('Skill name must be kebab-case')
base = Path(a.root) / 'skills' / a.name
(base / 'references').mkdir(parents=True, exist_ok=True)
(base / 'examples').mkdir(exist_ok=True)
(base / 'assets').mkdir(exist_ok=True)
(base / 'SKILL.md').write_text(f"""---
name: {a.name}
description: Describe what this skill does and when to use it.
metadata:
  version: 0.1.0
  category: sdlc
  owner: Apotheon.ai
  maturity: draft
  dependencies: []
---

# {a.name.replace('-', ' ').title()}

## Mission

## Workflow

## Quality Gates
""", encoding='utf-8')
print(base)
