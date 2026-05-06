#!/usr/bin/env python3
"""
Validate a memory packet to determine whether the workflow state is ready
to transition to the next phase.

Checks:
  1. Required memory packet fields (schema completeness)
  2. Phase status consistency (no downstream phase active before upstream completes)
  3. Quality gate blocking (no advance past a FAIL gate)
  4. Open questions (no blocking questions unresolved)
  5. Artifact readiness (next phase inputs declared as complete)

Usage:
    python validate_workflow_state.py < memory_packet.yaml
    python validate_workflow_state.py --file memory_packet.yaml
    python validate_workflow_state.py --file packet.yaml --next-phase backend

Exit codes:
    0  All checks pass — workflow may advance
    1  One or more checks fail — workflow is blocked
    2  Input error (bad file, invalid format)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Phase dependency order — mirrors skill-dependency-graph.md
# ---------------------------------------------------------------------------

# Maps phase name → phases that must be complete before it can be in_progress
_PHASE_DEPS: dict[str, list[str]] = {
    "requirements": [],
    "architecture": [],          # requirements preferred but optional
    "ai-engineering": ["architecture"],
    "backend": ["architecture"],
    "frontend": ["architecture", "backend"],
    "security": ["architecture"],
    "qa": ["backend"],
    "code-review": [],
    "release": ["qa", "security"],
    "observability": ["release"],
    "operations": ["observability"],
    "compliance": ["security", "qa"],
    "reporting": [],
}

# Valid phase status values
_VALID_STATUSES = {"pending", "in_progress", "complete", "blocked", "skipped"}

# Valid gate status values
_VALID_GATE_STATUSES = {"PASS", "PASS_WITH_WARNINGS", "FAIL", "NOT_EVALUATED", "SKIPPED"}

# Gate name → transition target phase (the phase that is blocked when gate FAILs)
_GATE_TO_TARGET_PHASE: dict[str, str] = {
    "requirements-complete": "architecture",
    "architecture-approved": "ai-engineering",  # also backend/frontend
    "ai-design-approved": "backend",
    "backend-implementation-ready": "security",
    "security-review-passed": "qa",
    "test-strategy-accepted": "release",
    "release-readiness-confirmed": "observability",
    "operations-readiness-confirmed": "operations",
}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _err(code: str, message: str, field: str | None = None) -> dict:
    e = {"code": code, "message": message}
    if field:
        e["field"] = field
    return e


def check_required_fields(packet: dict) -> list[dict]:
    """R1–R14 schema validation."""
    errors: list[dict] = []

    def require(field: str, parent: dict | None = None, path: str = "") -> bool:
        target = parent if parent is not None else packet
        keys = field.split(".")
        current = target
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                errors.append(_err("MISSING_FIELD", f"Required field missing or empty.", path + field))
                return False
            current = current[key]
        if current is None or current == "" or current == []:
            errors.append(_err("EMPTY_FIELD", f"Required field is empty.", path + field))
            return False
        return True

    require("packet_id")
    require("version")
    require("created_at")
    require("updated_at")
    require("project")
    require("project.objective")
    require("project.complexity")
    require("phase_status")
    require("current_phase")
    require("next_action")
    require("next_action.description")
    require("next_action.skill")

    # R5: complexity must be valid
    complexity = packet.get("project", {}).get("complexity", "")
    if complexity and complexity not in ("single-phase", "multi-phase", "full-sdlc"):
        errors.append(_err("INVALID_VALUE", f"project.complexity '{complexity}' is not valid.", "project.complexity"))

    # R7: phase_status values must be valid
    for phase, status in (packet.get("phase_status") or {}).items():
        if status not in _VALID_STATUSES:
            errors.append(_err("INVALID_STATUS", f"phase_status[{phase}] has invalid value '{status}'.", f"phase_status.{phase}"))

    # R8: current_phase must exist in phase_status
    current = packet.get("current_phase")
    phase_status = packet.get("phase_status") or {}
    if current and current not in phase_status:
        errors.append(_err("PHASE_MISMATCH", f"current_phase '{current}' not found in phase_status.", "current_phase"))

    # R12: gate statuses must be valid
    for entry in (packet.get("quality_gate_status") or []):
        gate_status = entry.get("status", "")
        if gate_status and gate_status not in _VALID_GATE_STATUSES:
            gate_name = entry.get("gate_name", "?")
            errors.append(_err("INVALID_GATE_STATUS", f"Gate '{gate_name}' has invalid status '{gate_status}'.", "quality_gate_status"))

    return errors


def check_phase_dependency_order(packet: dict) -> list[dict]:
    """
    No downstream phase may be in_progress or complete while a required
    upstream phase is pending or blocked.
    """
    errors: list[dict] = []
    phase_status: dict[str, str] = packet.get("phase_status") or {}

    active_statuses = {"in_progress", "complete"}

    for phase, deps in _PHASE_DEPS.items():
        phase_st = phase_status.get(phase)
        if phase_st not in active_statuses:
            continue
        for dep in deps:
            dep_st = phase_status.get(dep)
            if dep_st is None:
                continue  # dep not in this workflow — skip
            if dep_st not in ("complete", "skipped"):
                errors.append(_err(
                    "DEPENDENCY_VIOLATION",
                    f"Phase '{phase}' is '{phase_st}' but required upstream phase "
                    f"'{dep}' is '{dep_st}'. Upstream must be 'complete' first.",
                    f"phase_status.{phase}",
                ))

    return errors


def check_gate_blocking(packet: dict) -> list[dict]:
    """
    No phase may be in_progress or complete when a gate that guards its
    entry has status FAIL.
    """
    errors: list[dict] = []
    phase_status: dict[str, str] = packet.get("phase_status") or {}
    gate_statuses: dict[str, str] = {
        g["gate_name"]: g["status"]
        for g in (packet.get("quality_gate_status") or [])
        if "gate_name" in g and "status" in g
    }

    for gate_name, target_phase in _GATE_TO_TARGET_PHASE.items():
        gate_st = gate_statuses.get(gate_name)
        if gate_st != "FAIL":
            continue
        phase_st = phase_status.get(target_phase)
        if phase_st in ("in_progress", "complete"):
            errors.append(_err(
                "GATE_BLOCKING_VIOLATION",
                f"Phase '{target_phase}' is '{phase_st}' but gate "
                f"'{gate_name}' has status FAIL. The gate must pass before "
                f"this phase can proceed.",
                f"quality_gate_status[{gate_name}]",
            ))

    return errors


def check_open_questions(packet: dict, next_phase: str | None = None) -> list[dict]:
    """
    Report any open question that blocks the current or next phase.
    """
    errors: list[dict] = []
    current = packet.get("current_phase")
    targets = {current, next_phase} - {None}

    for oq in (packet.get("open_questions") or []):
        blocks = oq.get("blocks", "")
        q_id = oq.get("id", "?")
        question = oq.get("question", "")
        # Check if the blocked phase/gate matches what we care about
        if any(t and t in blocks for t in targets):
            errors.append(_err(
                "BLOCKING_OPEN_QUESTION",
                f"Open question {q_id} blocks '{blocks}' and must be resolved "
                f"before the workflow can advance. Question: {question}",
                f"open_questions[{q_id}]",
            ))

    return errors


def check_artifact_readiness(packet: dict, next_phase: str | None = None) -> list[dict]:
    """
    Verify that artifacts declared as consumed_by the next phase are present
    and have status 'complete'.
    """
    if not next_phase:
        return []

    errors: list[dict] = []
    artifacts: list[dict] = packet.get("artifacts") or []

    needed = [a for a in artifacts if next_phase in (a.get("consumed_by") or [])]
    for artifact in needed:
        if artifact.get("status") != "complete":
            name = artifact.get("name", "?")
            status = artifact.get("status", "missing")
            errors.append(_err(
                "ARTIFACT_NOT_READY",
                f"Artifact '{name}' is required by phase '{next_phase}' but "
                f"has status '{status}' (expected 'complete').",
                f"artifacts[{name}]",
            ))

    return errors


# ---------------------------------------------------------------------------
# Main validation runner
# ---------------------------------------------------------------------------

def validate(packet: dict, next_phase: str | None = None) -> dict:
    """
    Run all validation checks. Returns a result dict with:
      valid: bool
      checks: list of check results
      errors: flat list of all errors
      blocked_by: list of blocking error codes
    """
    checks = []

    def run_check(name: str, fn, *args) -> list[dict]:
        errs = fn(*args)
        checks.append({"check": name, "passed": len(errs) == 0, "errors": errs})
        return errs

    all_errors: list[dict] = []
    all_errors += run_check("required_fields", check_required_fields, packet)
    all_errors += run_check("phase_dependency_order", check_phase_dependency_order, packet)
    all_errors += run_check("gate_blocking", check_gate_blocking, packet)
    all_errors += run_check("open_questions", check_open_questions, packet, next_phase)
    all_errors += run_check("artifact_readiness", check_artifact_readiness, packet, next_phase)

    blocking_codes = list({e["code"] for e in all_errors})

    return {
        "valid": len(all_errors) == 0,
        "checks": checks,
        "errors": all_errors,
        "blocked_by": blocking_codes,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_packet(path: str | None) -> dict:
    if path:
        content = Path(path).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()

    # Try YAML first (superset of JSON), fall back to JSON
    if _YAML_AVAILABLE:
        try:
            return yaml.safe_load(content)
        except Exception:
            pass

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        print(json.dumps({"error": f"Failed to parse input: {exc}"}), file=sys.stderr)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a memory packet workflow state."
    )
    parser.add_argument("--file", "-f", metavar="PATH",
                        help="Path to memory packet file (YAML or JSON). Reads stdin if omitted.")
    parser.add_argument("--next-phase", metavar="PHASE",
                        help="Check readiness to transition into this phase.")
    args = parser.parse_args()

    raw = _load_packet(args.file)
    # Support both bare packet and wrapped {memory_packet: ...}
    packet = raw.get("memory_packet", raw) if isinstance(raw, dict) else raw

    if not isinstance(packet, dict):
        print(json.dumps({"error": "Packet must be a YAML/JSON object."}), file=sys.stderr)
        sys.exit(2)

    result = validate(packet, next_phase=args.next_phase)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()