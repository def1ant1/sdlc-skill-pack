#!/usr/bin/env python3
from pathlib import Path
import json, sys
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
summary = {"directories": 0, "files": 0}
for p in root.rglob('*'):
    if p.is_dir(): summary["directories"] += 1
    else: summary["files"] += 1
print(json.dumps(summary, indent=2))
