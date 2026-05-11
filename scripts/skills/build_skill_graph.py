#!/usr/bin/env python3
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

engine = module.SkillGraphEngine(ROOT)
engine.build()
engine.write_reports(ROOT / "reports")
print("Generated reports/skill_graph.{json,md,mmd}")
