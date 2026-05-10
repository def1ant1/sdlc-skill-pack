from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = [
    "finance-accounting-phase-pack",
    "sales-marketing-customer-phase-pack",
    "inventory-product-market-phase-pack",
    "hr-operations-phase-pack",
    "vendor-procurement-phase-pack",
    "legal-operations-phase-pack",
    "process-optimization-phase-pack",
]
REQUIRED_EVENTS = {
    "schemas/events/approval_requested.schema.json",
    "schemas/events/approval_decided.schema.json",
    "schemas/events/workflow_completed.schema.json",
    "schemas/events/business_policy_violation.schema.json",
}


def _manifest(skill: str) -> dict:
    return json.loads((REPO_ROOT / "skills" / skill / "manifest.v9.json").read_text())


def test_new_phase_pack_files_exist():
    for skill in SKILLS:
        root = REPO_ROOT / "skills" / skill
        assert root.is_dir()
        assert (root / "SKILL.md").is_file()
        assert (root / "manifest.v9.json").is_file()
        assert (root / "eval.spec.json").is_file()
        assert (root / "examples" / "workflow.yaml").is_file()


def test_new_phase_pack_approval_controls_and_contracts():
    for skill in SKILLS:
        manifest = _manifest(skill)
        assert manifest["human_approval_required"] is True
        controls = manifest["approval_controls"]
        assert controls["required_for_outbound_customer_communication"] is True
        assert controls["required_for_external_mutations"] is True

        canonical = manifest["canonical_schema_refs"]
        assert set(canonical["events"]) == REQUIRED_EVENTS
        for field in ("input_contract", "output_contract"):
            refs = set(manifest[field]["schema_refs"])
            assert REQUIRED_EVENTS.issubset(refs)
            assert set(canonical["entities"]).issubset(refs)
