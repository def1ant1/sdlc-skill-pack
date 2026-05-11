from scripts.governance.validators import (
    REQUIRED_PROFESSIONAL_BOUNDARY_LANGUAGE,
    load_high_risk_skill_paths,
    validate_autonomous_action_policy,
    validate_high_risk_approval_gate,
    validate_skill_output,
)


def test_output_missing_required_governance_fails_closed() -> None:
    payload = {
        "sections": {"observed_data": "facts"},
    }
    errors = validate_skill_output(payload)
    codes = {e.code for e in errors}
    assert "missing_professional_boundary_language" in codes
    assert "missing_traceability_fields" in codes
    assert "missing_output_sections" in codes


def test_output_with_required_sections_and_traceability_passes() -> None:
    payload = {
        "professional_boundary_language": REQUIRED_PROFESSIONAL_BOUNDARY_LANGUAGE,
        "sections": {
            "observed_data": "raw inputs",
            "derived_analysis": "computed metrics",
            "inference": "interpreted signals",
            "recommendation": "next-best action",
        },
        "assumptions_log": ["FX rates assumed constant intraday"],
        "evidence_lineage": [{"source": "ledger.csv", "retrieved_at": "2026-05-11"}],
        "confidence": 0.81,
        "risk_score": 0.33,
        "compliance_boundary_checks": ["no autonomous payout initiated"],
        "audit_events": [{"event": "governance.validated"}],
    }
    assert validate_skill_output(payload) == []


def test_prohibited_autonomous_actions_blocked() -> None:
    errors = validate_autonomous_action_policy(
        ["place_trade", "analyze_positions"],
        autonomous_mode=True,
    )
    assert len(errors) == 1
    assert errors[0].code == "prohibited_autonomous_actions"


def test_high_risk_paths_with_external_side_effects_require_approval() -> None:
    high_risk = load_high_risk_skill_paths()
    assert "skills/trading-research" in high_risk

    errors = validate_high_risk_approval_gate(
        skill_path="skills/trading-research",
        requested_actions=["place_trade"],
        approval_granted=False,
        high_risk_paths=high_risk,
    )
    assert len(errors) == 1
    assert errors[0].code == "approval_required_for_side_effect"


def test_non_side_effect_action_does_not_require_approval() -> None:
    errors = validate_high_risk_approval_gate(
        skill_path="skills/trading-research",
        requested_actions=["analyze_positions"],
        approval_granted=False,
        high_risk_paths={"skills/trading-research"},
    )
    assert errors == []
