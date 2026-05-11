#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

DEFAULT_REGISTRY = Path('workflows/library/registry.yaml')

def main() -> int:
    ap=argparse.ArgumentParser(description='List workflows in local library registry.')
    ap.add_argument('--registry', type=Path, default=DEFAULT_REGISTRY)
    ap.add_argument('--json', action='store_true')
    a=ap.parse_args()
    payload=yaml.safe_load(a.registry.read_text()) if a.registry.exists() else {"workflows": []}
    workflows=payload.get('workflows',[])
    if a.json:
        print(json.dumps(workflows, indent=2))
    else:
        for w in workflows:
            print(f"{w.get('id')}\t{w.get('file')}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
