#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
engine_path = ROOT / "core" / "skill-graph-engine" / "engine.py"
spec = importlib.util.spec_from_file_location("skill_graph_engine", engine_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

parser = argparse.ArgumentParser(description="Planner-facing skill graph query interface")
parser.add_argument("intent", help="intent substring to match against skill use_when signals")
parser.add_argument("--required", nargs="*", default=[], help="already-available skill dependencies")
args = parser.parse_args()

engine = module.SkillGraphEngine(ROOT)
engine.build()
for candidate in engine.query_candidates(args.intent, args.required):
    print(f"{candidate['skill']} ({candidate['path']})")
    if candidate['dependencies']:
        print(f"  dependencies: {', '.join(candidate['dependencies'])}")
    if candidate['missing_dependencies']:
        print(f"  missing: {', '.join(candidate['missing_dependencies'])}")
