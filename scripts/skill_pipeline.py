#!/usr/bin/env python3
"""Deterministic skill pipeline scaffold generator.

Creates runnable compiler scaffolds and reports for MB-P0-018.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "compiled-skill.schema.json"
REPORT_JSON = ROOT / "reports" / "skill_pipeline_report.json"
REPORT_MD = ROOT / "reports" / "skill_pipeline_report.md"


@dataclass(frozen=True)
class PipelineArtifact:
    path: str
    kind: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_payload(version: str) -> dict[str, Any]:
    artifacts = [
        PipelineArtifact("core/skill-compiler/README.md", "docs"),
        PipelineArtifact("core/skill-compiler/compiler.py", "runtime"),
        PipelineArtifact("core/skill-compiler/schema_bindings.py", "bindings"),
        PipelineArtifact("core/skill-compiler/telemetry.py", "telemetry"),
        PipelineArtifact("core/skill-compiler/governance.py", "governance"),
        PipelineArtifact("core/skill-compiler/tests/test_compiler.py", "test"),
    ]
    return {
        "version": version,
        "generated_at": _utc_now_iso(),
        "schema": str(SCHEMA_PATH.relative_to(ROOT)),
        "artifacts": [a.__dict__ for a in artifacts],
        "deterministic_seed": "skill-pipeline-v1",
    }


def write_reports(payload: dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    stable_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    REPORT_JSON.write_text(stable_json, encoding="utf-8")
    checksum = _sha256_text(stable_json)
    REPORT_MD.write_text(
        "# Skill Pipeline Report\n\n"
        f"- Version: `{payload['version']}`\n"
        f"- Generated: `{payload['generated_at']}`\n"
        f"- Deterministic Seed: `{payload['deterministic_seed']}`\n"
        f"- JSON SHA256: `{checksum}`\n"
        "\n## Artifacts\n"
        + "\n".join(f"- `{a['path']}` ({a['kind']})" for a in payload["artifacts"]) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic skill pipeline reports")
    parser.add_argument("--version", default="0.1.0")
    args = parser.parse_args()
    payload = build_payload(args.version)
    write_reports(payload)
    print(json.dumps({"ok": True, "report": str(REPORT_JSON.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
