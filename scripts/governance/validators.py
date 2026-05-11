from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

REQUIRED_PROFESSIONAL_BOUNDARY_LANGUAGE = (
    "This output is decision support only. Review with a qualified professional before acting."
)

PROHIBITED_AUTONOMOUS_ACTIONS = {
    "place_trade",
    "transfer_money",
    "execute_tax_filing",
    "create_or_dissolve_entity",
    "submit_hr_decision",
    "send_customer_communication",
    "submit_legal_filing",
    "final_legal_advice",
    "mutate_security_policy",
}

EXTERNAL_SIDE_EFFECT_ACTIONS = {
    "place_trade",
    "transfer_money",
    "execute_tax_filing",
    "create_or_dissolve_entity",
    "submit_hr_decision",
    "send_customer_communication",
    "submit_legal_filing",
    "mutate_security_policy",
    "mutate_secrets",
    "mutate_iam",
    "mutate_encryption",
    "mutate_access_controls",
    "execute_payment",
}

REQUIRED_TRACEABILITY_FIELDS = {
    "assumptions_log",
    "evidence_lineage",
    "confidence",
    "risk_score",
    "compliance_boundary_checks",
    "audit_events",
}

REQUIRED_OUTPUT_SECTIONS = {
    "observed_data",
    "derived_analysis",
    "inference",
    "recommendation",
}


@dataclass
class ValidationError:
    code: str
    message: str


def validate_skill_output(output: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []

    language = str(output.get("professional_boundary_language", "")).strip()
    if REQUIRED_PROFESSIONAL_BOUNDARY_LANGUAGE not in language:
        errors.append(
            ValidationError(
                code="missing_professional_boundary_language",
                message="Output must include required professional-boundary language.",
            )
        )

    sections = output.get("sections", {})
    missing_sections = sorted(section for section in REQUIRED_OUTPUT_SECTIONS if not sections.get(section))
    if missing_sections:
        errors.append(
            ValidationError(
                code="missing_output_sections",
                message=f"Missing required output sections: {', '.join(missing_sections)}",
            )
        )

    errors.extend(validate_traceability(output))
    return errors


def validate_traceability(output: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    missing = sorted(field for field in REQUIRED_TRACEABILITY_FIELDS if not output.get(field))
    if missing:
        errors.append(
            ValidationError(
                code="missing_traceability_fields",
                message=f"Missing traceability fields: {', '.join(missing)}",
            )
        )
    return errors


def validate_autonomous_action_policy(actions: list[str], *, autonomous_mode: bool) -> list[ValidationError]:
    if not autonomous_mode:
        return []

    violations = sorted(set(actions) & PROHIBITED_AUTONOMOUS_ACTIONS)
    if violations:
        return [
            ValidationError(
                code="prohibited_autonomous_actions",
                message=f"Autonomous mode cannot execute actions: {', '.join(violations)}",
            )
        ]
    return []


def load_high_risk_skill_paths(backlog_path: Path | None = None) -> set[str]:
    path = backlog_path or Path("APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md")
    text = path.read_text(encoding="utf-8")
    return {m.group(0).rstrip("/") for m in re.finditer(r"skills/[a-z0-9-]+/", text)}


def validate_high_risk_approval_gate(
    skill_path: str,
    requested_actions: list[str],
    approval_granted: bool,
    high_risk_paths: set[str] | None = None,
) -> list[ValidationError]:
    tracked = high_risk_paths or load_high_risk_skill_paths()
    normalized = skill_path.rstrip("/")
    if normalized not in tracked:
        return []

    side_effect_actions = sorted(set(requested_actions) & EXTERNAL_SIDE_EFFECT_ACTIONS)
    if side_effect_actions and not approval_granted:
        return [
            ValidationError(
                code="approval_required_for_side_effect",
                message=(
                    "High-risk domain skill requires approval for external side effects: "
                    + ", ".join(side_effect_actions)
                ),
            )
        ]
    return []
