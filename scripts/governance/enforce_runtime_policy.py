from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.governance.validators import (
    ValidationError,
    validate_autonomous_action_policy,
    EXTERNAL_SIDE_EFFECT_ACTIONS,
    validate_high_risk_approval_gate,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _emit_decision_log(output_path: Path | None, decision: dict[str, Any]) -> None:
    if output_path is None:
        print(json.dumps(decision, indent=2))
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")


def evaluate_policy(request: dict[str, Any], *, repo_root: Path) -> tuple[dict[str, Any], int]:
    skill_path = str(request.get("skill_path", "")).strip()
    requested_actions = request.get("requested_actions", [])
    if not isinstance(requested_actions, list):
        requested_actions = []
    requested_actions = [a for a in requested_actions if isinstance(a, str)]

    approval_granted = bool(request.get("approval_granted", False))
    autonomous_mode = bool(request.get("autonomous_mode", False))

    violations: list[ValidationError] = []
    side_effect_actions = sorted(set(requested_actions) & EXTERNAL_SIDE_EFFECT_ACTIONS)
    if side_effect_actions and not approval_granted:
        violations.append(
            ValidationError(
                code="approval_required_for_external_side_effect",
                message=(
                    "External side-effect actions require explicit approval: " + ", ".join(side_effect_actions)
                ),
            )
        )
    violations.extend(validate_autonomous_action_policy(requested_actions, autonomous_mode=autonomous_mode))
    violations.extend(
        validate_high_risk_approval_gate(
            skill_path=skill_path,
            requested_actions=requested_actions,
            approval_granted=approval_granted,
            high_risk_paths=None,
        )
    )

    status = "deny" if violations else "allow"
    reason = "fail_closed" if violations else "policy_checks_passed"
    decision = {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": status,
        "reason": reason,
        "skill_path": skill_path,
        "requested_actions": requested_actions,
        "approval_granted": approval_granted,
        "autonomous_mode": autonomous_mode,
        "violations": [{"code": v.code, "message": v.message} for v in violations],
        "dashboard_event": {
            "type": "governance.policy.decision",
            "status": status,
            "violation_count": len(violations),
        },
    }
    return decision, (1 if violations else 0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce fail-closed runtime governance policy checks.")
    parser.add_argument("--request", type=Path, required=True, help="JSON request payload")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--decision-log", type=Path, help="Write policy decision JSON for dashboard and audit use")
    args = parser.parse_args()

    request = _read_json(args.request)
    decision, exit_code = evaluate_policy(request, repo_root=args.repo_root)
    _emit_decision_log(args.decision_log, decision)
    if exit_code:
        print("FAIL_CLOSED: policy denied request")
    else:
        print("PASS: policy allowed request")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
