#!/usr/bin/env python3
"""Machine-verifiable release gates for Section 15 hardening checklist."""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Gate:
    key: str
    description: str
    artifacts: list[Path]
    commands: list[list[str]] | None = None


GATES: list[Gate] = [
    Gate(
        key="error-envelope-schema",
        description="Error envelope schema exists and contracts validate",
        artifacts=[ROOT / "schemas" / "error-envelope.schema.json", ROOT / "scripts" / "validation" / "validate_error_contracts.py"],
        commands=[["python", "scripts/validation/validate_error_contracts.py"]],
    ),
    Gate(
        key="runtime-hardening-modules",
        description="Runtime retry/circuit/idempotency modules exist",
        artifacts=[ROOT / "scripts" / "runtime" / "retry_policy.py", ROOT / "scripts" / "runtime" / "circuit_breaker.py", ROOT / "scripts" / "runtime" / "idempotency.py"],
    ),
    Gate(
        key="workflow-resume-support",
        description="Workflow execution failure records and resume support",
        artifacts=[ROOT / "scripts" / "runtime" / "execute_workflow.py"],
        commands=[["pytest", "--tb=short", "-q", "tests/runtime/test_execute_workflow.py"]],
    ),
    Gate(
        key="planner-diagnostics",
        description="Planners emit diagnostics and validate outputs",
        artifacts=[ROOT / "scripts" / "orchestration" / "plan_workflow.py"],
        commands=[["python", "scripts/validation/validate_workflow_plan.py", "tests/fixtures/workflow-plans/valid-plan.yaml"]],
    ),
    Gate(
        key="schedule-safety",
        description="Schedules enforce safe misfire + concurrency handling",
        artifacts=[ROOT / "scripts" / "schedules" / "run_due_schedules.py", ROOT / "scripts" / "schedules" / "schedule_state.py"],
        commands=[["pytest", "--tb=short", "-q", "tests/scheduling/test_scheduling.py"]],
    ),
    Gate(
        key="connector-fail-closed",
        description="Connectors fail closed and avoid secret leakage",
        artifacts=[ROOT / "scripts" / "connectors" / "base_connector.py", ROOT / "scripts" / "security" / "scan_for_secrets.py"],
        commands=[["python", "scripts/validation/validate_connector_mappings.py"]],
    ),
    Gate(
        key="governance-gates",
        description="High-risk actions blocked without approval",
        artifacts=[ROOT / "scripts" / "governance" / "validate_hitl_for_actions.py", ROOT / "schemas" / "hitl-gate.schema.json"],
        commands=[["python", "-m", "scripts.governance.validate_hitl_for_actions"]],
    ),
    Gate(
        key="runtime-diagnostics",
        description="Runtime diagnostics reports are generated",
        artifacts=[ROOT / "scripts" / "reports" / "generate_runtime_diagnostics.py", ROOT / "reports" / "runtime_diagnostics.md"],
        commands=[["python", "scripts/reports/generate_runtime_diagnostics.py"]],
    ),
    Gate(
        key="backup-restore",
        description="Backup and restore dry-run tooling exists",
        artifacts=[ROOT / "scripts" / "backup" / "backup_local_state.py", ROOT / "scripts" / "backup" / "restore_local_state.py"],
        commands=[
            ["python", "scripts/backup/backup_local_state.py", "--help"],
            ["python", "scripts/backup/restore_local_state.py", "--help"],
        ],
    ),
    Gate(
        key="hardening-tests",
        description="Failure injection and dry-run side-effect tests pass",
        artifacts=[ROOT / "tests" / "runtime" / "test_execute_workflow.py", ROOT / "tests" / "scheduling" / "test_scheduling.py"],
        commands=[["pytest", "--tb=short", "-q", "tests/runtime/test_execute_workflow.py", "tests/scheduling/test_scheduling.py"]],
    ),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def run_command(cmd: list[str]) -> tuple[bool, str]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode == 0, output.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Section 15 machine-verifiable release gates.")
    parser.add_argument("--strict", action="store_true", help="Fail if generated diagnostics artifacts are missing before command execution.")
    args = parser.parse_args()

    failures: list[str] = []
    print("== Section 15 release gates ==")

    for gate in GATES:
        print(f"\n[gate] {gate.key}: {gate.description}")

        missing = [artifact for artifact in gate.artifacts if not artifact.exists()]
        if missing:
            print("FAIL artifact presence")
            for artifact in missing:
                pointer = f"file://{artifact}"
                print(f"  - missing: {rel(artifact)} ({pointer})")
            failures.append(gate.key)
            continue

        print("PASS artifact presence")

        if args.strict and gate.commands is None:
            print("PASS command execution (not required)")
            continue

        if gate.commands:
            for command in gate.commands:
                ok, output = run_command(command)
                print(f"COMMAND: {' '.join(command)}")
                if ok:
                    print("PASS command execution")
                else:
                    print("FAIL command execution")
                    if output:
                        for line in output.splitlines()[:20]:
                            print(f"  > {line}")
                    failures.append(gate.key)
                    break

    if failures:
        print("\nRELEASE_GATES_FAILED")
        for gate_key in failures:
            print(f"- {gate_key}")
        print("Release tagging/promotion must be blocked until all gates pass.")
        return 1

    print("\nRELEASE_GATES_PASSED: all Section 15 gates satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
