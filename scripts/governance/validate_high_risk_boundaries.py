from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.governance.validators import REQUIRED_PROFESSIONAL_BOUNDARY_LANGUAGE, load_high_risk_skill_paths

POLICY_REFERENCE = "docs/architecture/governance-model.md"
REMEDIATION = (
    "Include the required professional boundary language in regulated output templates "
    "(professional_boundary_language)."
)


def _load_manifest(skill_path: Path) -> dict[str, Any]:
    manifest_path = skill_path / "manifest.v9.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def validate_high_risk_boundaries(repo_root: Path, high_risk_paths: set[str] | None = None) -> list[str]:
    tracked_paths = high_risk_paths or load_high_risk_skill_paths(repo_root / "APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md")
    errors: list[str] = []

    for relative in sorted(tracked_paths):
        manifest = _load_manifest(repo_root / relative)
        boundary = str(manifest.get("professional_boundary_language", "")).strip()
        if REQUIRED_PROFESSIONAL_BOUNDARY_LANGUAGE not in boundary:
            errors.append(
                f"{relative}: missing required professional boundary language. "
                f"policy={POLICY_REFERENCE} remediation={REMEDIATION}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate professional boundaries for high-risk skills.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    errors = validate_high_risk_boundaries(args.repo_root)
    if errors:
        print("FAIL_CLOSED: high-risk professional boundary validation failed")
        for err in errors:
            print(f" - {err}")
        return 1

    print("PASS: professional boundary language validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
