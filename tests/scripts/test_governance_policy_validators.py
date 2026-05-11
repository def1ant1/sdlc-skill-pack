from __future__ import annotations

import json

from scripts.governance.validate_high_risk_boundaries import validate_high_risk_boundaries
from scripts.governance.validate_hitl_for_actions import validate_hitl_for_actions
from scripts.governance.validate_policy_links import validate_policy_links
from scripts.governance.validators import validate_high_risk_approval_gate


def test_policy_link_validator_fails_closed_with_policy_and_remediation(tmp_path):
    skill = tmp_path / "skills" / "regulated-skill"
    skill.mkdir(parents=True)
    (skill / "manifest.v9.json").write_text("{}", encoding="utf-8")

    errors = validate_policy_links(tmp_path, {"skills/regulated-skill"})
    assert len(errors) == 1
    assert "policy=docs/architecture/governance-model.md" in errors[0]
    assert "remediation=" in errors[0]


def test_hitl_validator_blocks_external_actions_without_review_gate(tmp_path):
    skill = tmp_path / "skills" / "regulated-skill"
    skill.mkdir(parents=True)
    (skill / "manifest.v9.json").write_text(
        json.dumps({"actions": ["transfer_money"], "approval_policy": {}}), encoding="utf-8"
    )

    errors = validate_hitl_for_actions(tmp_path, {"skills/regulated-skill"})
    assert len(errors) == 1
    assert "external side-effect actions" in errors[0]
    assert "policy=docs/architecture/governance-model.md" in errors[0]


def test_boundary_validator_requires_professional_language_with_policy_reference(tmp_path):
    skill = tmp_path / "skills" / "regulated-skill"
    skill.mkdir(parents=True)
    (skill / "manifest.v9.json").write_text(json.dumps({"professional_boundary_language": ""}), encoding="utf-8")

    errors = validate_high_risk_boundaries(tmp_path, {"skills/regulated-skill"})
    assert len(errors) == 1
    assert "missing required professional boundary language" in errors[0]
    assert "policy=docs/architecture/governance-model.md" in errors[0]


def test_high_risk_write_actions_cannot_execute_without_approval():
    errors = validate_high_risk_approval_gate(
        skill_path="skills/trading-research",
        requested_actions=["transfer_money", "mutate_iam"],
        approval_granted=False,
        high_risk_paths={"skills/trading-research"},
    )
    assert len(errors) == 1
    assert errors[0].code == "approval_required_for_side_effect"
    assert "transfer_money" in errors[0].message
    assert "mutate_iam" in errors[0].message
