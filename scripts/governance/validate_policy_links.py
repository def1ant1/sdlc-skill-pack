from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.governance.validators import load_high_risk_skill_paths

POLICY_REFERENCE = "docs/architecture/governance-model.md"
REMEDIATION = (
    "Add governance_docs links in each high-risk skill manifest with at least one "
    "path under docs/ and rerun validation."
)


def _load_manifest(skill_path: Path) -> dict[str, Any]:
    manifest_path = skill_path / "manifest.v9.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def validate_policy_links(repo_root: Path, high_risk_paths: set[str] | None = None) -> list[str]:
    tracked_paths = high_risk_paths or load_high_risk_skill_paths(repo_root / "APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md")
    errors: list[str] = []

    for relative in sorted(tracked_paths):
        skill_dir = repo_root / relative
        manifest = _load_manifest(skill_dir)
        governance_docs = manifest.get("governance_docs", [])
        linked_docs = [d for d in governance_docs if isinstance(d, str) and d.startswith("docs/")]
        if not linked_docs:
            errors.append(
                f"{relative}: missing governance_docs link. policy={POLICY_REFERENCE} remediation={REMEDIATION}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate governance doc linkage for high-risk skills.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    errors = validate_policy_links(args.repo_root)
    if errors:
        print("FAIL_CLOSED: governance policy link validation failed")
        for err in errors:
            print(f" - {err}")
        return 1

    print("PASS: governance policy links validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
