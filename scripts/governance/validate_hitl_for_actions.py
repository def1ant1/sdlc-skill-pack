from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.governance.validators import EXTERNAL_SIDE_EFFECT_ACTIONS, load_high_risk_skill_paths

POLICY_REFERENCE = "docs/architecture/governance-model.md"
REMEDIATION = "Set approval_policy.review_required_for_external_actions=true in each high-risk skill manifest."


def _load_manifest(skill_path: Path) -> dict[str, Any]:
    manifest_path = skill_path / "manifest.v9.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _actions(manifest: dict[str, Any]) -> set[str]:
    declared = manifest.get("actions", [])
    if not isinstance(declared, list):
        return set()
    return {a for a in declared if isinstance(a, str)}


def validate_hitl_for_actions(repo_root: Path, high_risk_paths: set[str] | None = None) -> list[str]:
    tracked_paths = high_risk_paths or load_high_risk_skill_paths(repo_root / "APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md")
    errors: list[str] = []
    for relative in sorted(tracked_paths):
        manifest = _load_manifest(repo_root / relative)
        side_effect_actions = sorted(_actions(manifest) & EXTERNAL_SIDE_EFFECT_ACTIONS)
        if not side_effect_actions:
            continue
        approval_policy = manifest.get("approval_policy", {})
        if not approval_policy.get("review_required_for_external_actions", False):
            errors.append(
                f"{relative}: external side-effect actions {side_effect_actions} require HITL approval gate. "
                f"policy={POLICY_REFERENCE} remediation={REMEDIATION}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HITL gates for high-risk external actions.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    errors = validate_hitl_for_actions(args.repo_root)
    if errors:
        print("FAIL_CLOSED: HITL gate validation failed")
        for err in errors:
            print(f" - {err}")
        return 1

    print("PASS: HITL gate coverage validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
