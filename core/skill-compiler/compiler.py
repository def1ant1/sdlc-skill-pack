"""Skill compiler runtime scaffold."""
from __future__ import annotations

import json
import importlib.util
from dataclasses import asdict
from pathlib import Path

_BINDINGS_PATH = Path(__file__).with_name("schema_bindings.py")
_spec = importlib.util.spec_from_file_location("schema_bindings", _BINDINGS_PATH)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)
CompiledSkill = _module.CompiledSkill


def compile_skill(skill_name: str, version: str = "0.1.0") -> dict:
    artifact = CompiledSkill(
        skill_name=skill_name,
        compiler_version=version,
        activity_stub=f"activities/{skill_name}_activity.py",
        eval_stub=f"tests/test_{skill_name}_eval.py",
        package_metadata={"name": skill_name, "version": version},
    )
    return asdict(artifact)


def write_compiled_skill(output_dir: Path, compiled: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{compiled['skill_name']}.compiled.json"
    out.write_text(json.dumps(compiled, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
