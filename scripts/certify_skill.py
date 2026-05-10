#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "skill-manifest-v9.schema.json"


def _python_type_for_json_type(type_name: str):
    return {
        "string": str,
        "number": (int, float),
        "integer": int,
        "object": dict,
        "array": list,
        "boolean": bool,
        "null": type(None),
    }.get(type_name)


def validate_manifest_schema(manifest: dict) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    reasons: list[str] = []

    required = schema.get("required", [])
    missing_required = [key for key in required if key not in manifest]
    if missing_required:
        reasons.append("invalid_manifest:missing_required=" + ",".join(missing_required))

    properties = schema.get("properties", {})
    for key, rules in properties.items():
        if key not in manifest:
            continue

        value = manifest[key]

        allowed_types = rules.get("type")
        if allowed_types is not None:
            types = allowed_types if isinstance(allowed_types, list) else [allowed_types]
            if not any(
                isinstance(value, _python_type_for_json_type(t))
                and not (t == "boolean" and isinstance(value, bool) is False)
                for t in types
            ):
                reasons.append(f"invalid_manifest:type_mismatch:{key}")

        allowed_enum = rules.get("enum")
        if allowed_enum is not None and value not in allowed_enum:
            reasons.append(f"invalid_manifest:enum_violation:{key}")

    return reasons


def certify(skill_dir: Path, eval_passed: bool, security_passed: bool, context_passed: bool,
            telemetry_passed: bool, unresolved_routing_collisions: int,
            production_mutation_requested: bool, approval_status: str,
            approval_actor: str | None, policy_id: str | None, policy_version: str | None) -> dict:
    reasons: list[str] = []
    manifest_path = skill_dir / "manifest.v9.json"

    if not manifest_path.exists():
        reasons.append("missing_manifest")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            reasons.append(f"invalid_manifest_json:{exc.msg}")
        else:
            reasons.extend(validate_manifest_schema(manifest))

    if not eval_passed:
        reasons.append("eval_failed")
    if not security_passed:
        reasons.append("security_check_failed")
    if not context_passed:
        reasons.append("context_check_failed")
    if not telemetry_passed:
        reasons.append("telemetry_check_failed")
    if unresolved_routing_collisions > 0:
        reasons.append("unresolved_routing_collisions")

    certification_status = "certified" if not reasons else "rejected"
    governance_status = "not_required"

    if production_mutation_requested:
        governance_missing = []
        if approval_status != "approved":
            governance_missing.append("approval_status")
        if not approval_actor:
            governance_missing.append("approval_actor")
        if not policy_id:
            governance_missing.append("policy_id")
        if not policy_version:
            governance_missing.append("policy_version")
        if governance_missing:
            governance_status = "approval_required"
            reasons.append("governance_gate_blocked:" + ",".join(governance_missing))
            certification_status = "rejected"
        else:
            governance_status = "approved_for_mutation"

    return {
        "skill": skill_dir.name,
        "certification_status": certification_status,
        "governance_status": governance_status,
        "reasons": reasons,
        "manifest_present": manifest_path.exists(),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Certify a skill for marketplace publication.")
    p.add_argument("skill_dir", type=Path)
    p.add_argument("--eval-passed", action="store_true")
    p.add_argument("--security-passed", action="store_true")
    p.add_argument("--context-passed", action="store_true")
    p.add_argument("--telemetry-passed", action="store_true")
    p.add_argument("--unresolved-routing-collisions", type=int, default=0)
    p.add_argument("--production-mutation-requested", action="store_true")
    p.add_argument("--approval-status", default="pending")
    p.add_argument("--approval-actor")
    p.add_argument("--policy-id")
    p.add_argument("--policy-version")
    args = p.parse_args()

    result = certify(
        skill_dir=args.skill_dir,
        eval_passed=args.eval_passed,
        security_passed=args.security_passed,
        context_passed=args.context_passed,
        telemetry_passed=args.telemetry_passed,
        unresolved_routing_collisions=args.unresolved_routing_collisions,
        production_mutation_requested=args.production_mutation_requested,
        approval_status=args.approval_status,
        approval_actor=args.approval_actor,
        policy_id=args.policy_id,
        policy_version=args.policy_version,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["certification_status"] == "certified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
