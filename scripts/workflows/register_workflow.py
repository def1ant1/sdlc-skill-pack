#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

DEFAULT_REGISTRY = Path('workflows/library/registry.yaml')

def load_registry(path: Path) -> dict:
    if not path.exists():
        return {"workflows": []}
    return yaml.safe_load(path.read_text()) or {"workflows": []}

def main() -> int:
    ap=argparse.ArgumentParser(description='Register workflow fixture into local library registry.')
    ap.add_argument('workflow', type=Path)
    ap.add_argument('--registry', type=Path, default=DEFAULT_REGISTRY)
    a=ap.parse_args()
    payload=json.loads(a.workflow.read_text())
    reg=load_registry(a.registry)
    reg.setdefault('workflows',[])
    rel=str(a.workflow.as_posix())
    entry={"id":payload['fixture_id'],"file":rel,"expected_artifacts":payload.get('expected_artifacts',[]),"failure_fixtures":payload.get('failure_fixtures',[])}
    reg['workflows']=[w for w in reg['workflows'] if w.get('id')!=entry['id']]
    reg['workflows'].append(entry)
    a.registry.parent.mkdir(parents=True,exist_ok=True)
    a.registry.write_text(yaml.safe_dump(reg, sort_keys=False))
    print(json.dumps({"registered":entry['id'],"registry":str(a.registry)}, indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
