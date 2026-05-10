#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Gate:
    name: str
    phase: str
    command: list[str]


GATES: tuple[Gate, ...] = (
    Gate("Doc uniqueness", "contracts", ["python", "scripts/docs/validate_doc_uniqueness.py"]),
    Gate("Backlog/changelog sync", "contracts", ["python", "scripts/docs/check_backlog_changelog_sync.py"]),
    Gate("Documentation freshness", "contracts", ["python", "scripts/docs/enforce_doc_freshness.py"]),
    Gate("README claims", "contracts", ["python", "scripts/docs/validate_readme_claims.py"]),
    Gate("Backlog truth", "contracts", ["python", "scripts/validate_backlog_truth.py"]),
    Gate("Skill contracts", "contracts", ["python", "scripts/validate_skill_contracts.py"]),
    Gate("Context budget", "contracts", ["python", "scripts/check_context_budget.py"]),
    Gate("Skill inventory", "contracts", ["python", "scripts/generate_skill_inventory.py"]),
    Gate("Dependency graph", "contracts", ["python", "scripts/generate_dependency_graph.py"]),
    Gate("Skill overlap", "contracts", ["python", "scripts/detect_skill_overlap.py"]),
    Gate("Skill evals", "contracts", ["python", "scripts/validate_skill_evals.py"]),
    Gate("Telemetry events", "contracts", ["python", "scripts/validate_telemetry_events.py"]),
    Gate(
        "Work task snapshot freshness",
        "contracts",
        ["python", "scripts/check_work_tasks_snapshot_freshness.py"],
    ),
    Gate("HITL coverage", "contracts", ["python", "scripts/validate_hitl_coverage.py"]),
    Gate("Skill maturity", "contracts", ["python", "scripts/grade_skill_maturity.py"]),
    Gate("Release reports", "release", ["python", "scripts/generate_release_reports.py"]),
    Gate("Release artifacts", "release", ["python", "scripts/validate_release_artifacts.py"]),
    Gate("Release HITL coverage", "release", ["python", "scripts/validate_hitl_coverage.py"]),
    Gate("Release skill maturity", "release", ["python", "scripts/grade_skill_maturity.py"]),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pre-merge quality gates.")
    parser.add_argument(
        "--phase",
        action="append",
        choices=sorted({gate.phase for gate in GATES}),
        help="Phase(s) to execute. Omit to run all phases.",
    )
    return parser.parse_args()


def dedupe_lines(text: str) -> list[str]:
    seen: set[str] = set()
    lines: list[str] = []
    for line in text.splitlines():
        normalized = line.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        lines.append(line)
    return lines


def run_gate(gate: Gate) -> tuple[bool, list[str]]:
    result = subprocess.run(gate.command, capture_output=True, text=True)
    if result.returncode == 0:
        return True, []

    merged_output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    return False, dedupe_lines(merged_output)


def main() -> int:
    args = parse_args()
    selected_phases = set(args.phase) if args.phase else {gate.phase for gate in GATES}
    selected_gates = [gate for gate in GATES if gate.phase in selected_phases]

    if not selected_gates:
        print("No gates matched the requested phase selection.")
        return 2

    failures: dict[str, list[tuple[Gate, list[str]]]] = {}

    for gate in selected_gates:
        command_text = " ".join(gate.command)
        print(f"\n[{gate.phase}] {gate.name}\n$ {command_text}")
        passed, output = run_gate(gate)
        if passed:
            print("✔ PASS")
            continue
        print("✖ FAIL")
        failures.setdefault(gate.phase, []).append((gate, output))

    if not failures:
        print("\nAll pre-merge gates passed.")
        return 0

    print("\nPre-merge gate failures by phase:")
    for phase, phase_failures in failures.items():
        print(f"\n== {phase} ==")
        for gate, output in phase_failures:
            print(f"- {gate.name}")
            if output:
                for line in output:
                    print(f"    {line}")

    total_failed = sum(len(items) for items in failures.values())
    print(f"\nPre-merge checks failed: {total_failed} gate(s) failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
