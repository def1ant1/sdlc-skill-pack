from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKLOG = (REPO_ROOT / "APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md").read_text()
PHASES = ["103", "104", "105", "107", "108", "109", "110", "111", "112"]
REQUIRED_EVENT_SCHEMAS = {
    "schemas/events/approval_requested.schema.json",
    "schemas/events/approval_decided.schema.json",
    "schemas/events/workflow_completed.schema.json",
    "schemas/events/business_policy_violation.schema.json",
}


def _skills_for_phase(phase: str) -> list[str]:
    match = re.search(rf"## Phase {phase}[^\n]*\n.*?```text\n(.*?)```", BACKLOG, re.S)
    assert match, f"Missing phase block for {phase}"
    return [Path(line.strip()).name for line in match.group(1).strip().splitlines() if line.strip()]


def _manifest(skill: str) -> dict:
    return json.loads((REPO_ROOT / "skills" / skill / "manifest.v9.json").read_text())


def test_phase_skills_have_required_files():
    for phase in PHASES:
        for skill in _skills_for_phase(phase):
            skill_dir = REPO_ROOT / "skills" / skill
            assert skill_dir.is_dir()
            assert (skill_dir / "SKILL.md").is_file()
            assert (skill_dir / "manifest.v9.json").is_file()


def test_governance_gates_enforce_human_approval_for_mutations_and_outbound_comms():
    for phase in PHASES:
        for skill in _skills_for_phase(phase):
            manifest = _manifest(skill)
            controls = manifest["approval_controls"]
            assert controls["required_for_outbound_customer_communication"] is True
            assert controls["required_for_external_mutations"] is True


def test_routing_contracts_link_to_canonical_entity_and_event_schemas():
    for phase in PHASES:
        for skill in _skills_for_phase(phase):
            manifest = _manifest(skill)
            canonical_refs = manifest["canonical_schema_refs"]
            entity_refs = set(canonical_refs["entities"])
            event_refs = set(canonical_refs["events"])

            assert entity_refs
            assert REQUIRED_EVENT_SCHEMAS.issubset(event_refs)

            for contract_field in ("input_contract", "output_contract"):
                schema_refs = set(manifest[contract_field]["schema_refs"])
                assert REQUIRED_EVENT_SCHEMAS.issubset(schema_refs)
                assert entity_refs.issubset(schema_refs)
