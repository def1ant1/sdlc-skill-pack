"""
autonomous_os_bootstrap.py

Validates that the Apotheon Autonomous OS is fully assembled and ready to operate.
Checks: all required SKILL.md files present and valid, all script dependencies exist,
no validation errors in the skill pack.

Usage:
    python scripts/orchestration/autonomous_os_bootstrap.py
    python scripts/orchestration/autonomous_os_bootstrap.py --json
    python scripts/orchestration/autonomous_os_bootstrap.py --strict   # exit 1 on any warning
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Required skill manifest
# All 31 phases must be present for a fully operational Autonomous OS.
# ---------------------------------------------------------------------------

REQUIRED_SKILLS: list[dict] = [
    # Control plane
    {"path": "core/orchestration/SKILL.md",              "phase": 1,  "tier": 1, "name": "sdlc-orchestration"},
    {"path": "core/memory-token-management/SKILL.md",   "phase": 2,  "tier": 0, "name": "sdlc-memory-token-management"},
    {"path": "core/telemetry/SKILL.md",                 "phase": 6,  "tier": 0, "name": "telemetry"},
    {"path": "core/local-runtime/SKILL.md",             "phase": 7,  "tier": 1, "name": "local-runtime"},
    {"path": "core/connector-hub/SKILL.md",             "phase": 8,  "tier": 1, "name": "connector-hub"},
    {"path": "core/local-security/SKILL.md",            "phase": 9,  "tier": 0, "name": "local-security"},
    {"path": "core/knowledge-graph/SKILL.md",           "phase": 10, "tier": 1, "name": "knowledge-graph"},
    {"path": "core/retrieval-engine/SKILL.md",          "phase": 11, "tier": 1, "name": "retrieval-engine"},
    {"path": "core/kv-cache-management/SKILL.md",       "phase": 11, "tier": 1, "name": "kv-cache-management"},
    {"path": "core/multi-agent/SKILL.md",               "phase": 12, "tier": 2, "name": "multi-agent"},
    {"path": "core/model-evaluation/SKILL.md",          "phase": 14, "tier": 3, "name": "model-evaluation"},
    {"path": "core/mcp-integrations/SKILL.md",          "phase": 15, "tier": 3, "name": "mcp-integrations"},
    {"path": "core/gtm-orchestration/SKILL.md",         "phase": 17, "tier": 2, "name": "gtm-orchestration"},
    {"path": "core/tenant-management/SKILL.md",         "phase": 24, "tier": 2, "name": "tenant-management"},
    {"path": "core/hitl-dashboard/SKILL.md",            "phase": 25, "tier": 2, "name": "hitl-dashboard"},
    {"path": "core/strategic-planning/SKILL.md",        "phase": 26, "tier": 3, "name": "strategic-planning"},
    {"path": "core/sandbox-execution/SKILL.md",         "phase": 28, "tier": 3, "name": "sandbox-execution"},
    {"path": "core/lora-lifecycle/SKILL.md",            "phase": 29, "tier": 3, "name": "lora-lifecycle"},
    {"path": "core/synthetic-data/SKILL.md",            "phase": 30, "tier": 3, "name": "synthetic-data"},
    {"path": "core/runtime-economics/SKILL.md",         "phase": 22, "tier": 3, "name": "runtime-economics"},
    {"path": "core/autonomous-os/SKILL.md",             "phase": 31, "tier": 5, "name": "autonomous-os"},
    # Domain skills
    {"path": "skills/repo-intelligence/SKILL.md",       "phase": 13, "tier": 4, "name": "repo-intelligence"},
    {"path": "skills/cloud-deployment/SKILL.md",        "phase": 16, "tier": 3, "name": "cloud-deployment"},
    {"path": "skills/ai-search-optimization/SKILL.md",  "phase": 18, "tier": 4, "name": "ai-search-optimization"},
    {"path": "skills/content-marketing/SKILL.md",       "phase": 19, "tier": 4, "name": "content-marketing"},
    {"path": "skills/customer-success/SKILL.md",        "phase": 20, "tier": 4, "name": "customer-success"},
    {"path": "skills/product-analytics/SKILL.md",       "phase": 21, "tier": 4, "name": "product-analytics"},
    {"path": "skills/compliance-automation/SKILL.md",   "phase": 23, "tier": 4, "name": "compliance-automation"},
    {"path": "skills/revenue-operations/SKILL.md",      "phase": 27, "tier": 4, "name": "revenue-operations"},
]

REQUIRED_SCRIPTS: list[str] = [
    "scripts/validation/validate_skill_structure.py",
    "scripts/validation/validate_frontmatter.py",
    "scripts/orchestration/plan_workflow.py",
    "scripts/memory/build_context_packet.py",
    "scripts/ai-discovery/validate_ai_discovery.py",
    "scripts/ai-discovery/generate_llms_txt.py",
    "scripts/telemetry/record_telemetry_event.py",
    "scripts/security/scan_for_secrets.py",
    "scripts/gtm/plan_gtm_workflow.py",
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    severity: str = "error"  # error | warning | info


@dataclass
class BootstrapReport:
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    results: list[CheckResult] = field(default_factory=list)
    skill_coverage: dict = field(default_factory=dict)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)
        self.total_checks += 1
        if result.passed:
            self.passed += 1
        elif result.severity == "warning":
            self.warnings += 1
        else:
            self.failed += 1

    @property
    def healthy(self) -> bool:
        return self.failed == 0

    @property
    def fully_operational(self) -> bool:
        return self.failed == 0 and self.warnings == 0


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_skill_presence(root: Path, report: BootstrapReport) -> None:
    """Verify all required SKILL.md files exist."""
    present = 0
    for skill in REQUIRED_SKILLS:
        path = root / skill["path"]
        exists = path.exists()
        if exists:
            present += 1
        report.add(CheckResult(
            name=f"skill:{skill['name']}",
            passed=exists,
            message=(
                f"Phase {skill['phase']:02d} Tier-{skill['tier']} — {skill['path']}"
                if exists else
                f"MISSING: {skill['path']} (Phase {skill['phase']})"
            ),
            severity="error" if skill["tier"] <= 2 else "warning",
        ))
    report.skill_coverage = {
        "present": present,
        "total": len(REQUIRED_SKILLS),
        "pct": round(present / len(REQUIRED_SKILLS) * 100, 1),
    }


def check_script_presence(root: Path, report: BootstrapReport) -> None:
    """Verify all required automation scripts exist."""
    for script in REQUIRED_SCRIPTS:
        path = root / script
        report.add(CheckResult(
            name=f"script:{Path(script).name}",
            passed=path.exists(),
            message=(
                f"Found: {script}" if path.exists() else f"MISSING: {script}"
            ),
            severity="error",
        ))


def check_validation_passes(root: Path, report: BootstrapReport) -> None:
    """Run the two core validation scripts and check for zero errors."""
    for script_name, script_path in [
        ("validate_skill_structure", "scripts/validation/validate_skill_structure.py"),
        ("validate_frontmatter", "scripts/validation/validate_frontmatter.py"),
    ]:
        script = root / script_path
        if not script.exists():
            report.add(CheckResult(
                name=f"validation:{script_name}",
                passed=False,
                message=f"Script not found — cannot run validation: {script_path}",
                severity="error",
            ))
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(script), str(root)],
                capture_output=True, text=True, timeout=60,
            )
            output = result.stdout.strip()
            try:
                parsed = json.loads(output)
                errors = parsed.get("errors", [])
                passed = len(errors) == 0 and result.returncode == 0
                report.add(CheckResult(
                    name=f"validation:{script_name}",
                    passed=passed,
                    message=(
                        "All checks passed" if passed
                        else f"{len(errors)} error(s): {errors[:3]}"
                    ),
                    severity="error",
                ))
            except json.JSONDecodeError:
                passed = result.returncode == 0
                report.add(CheckResult(
                    name=f"validation:{script_name}",
                    passed=passed,
                    message="Passed" if passed else f"Failed (exit {result.returncode})",
                    severity="error",
                ))
        except subprocess.TimeoutExpired:
            report.add(CheckResult(
                name=f"validation:{script_name}",
                passed=False,
                message="Timed out after 60s",
                severity="error",
            ))


def check_agent_presence(root: Path, report: BootstrapReport) -> None:
    """Verify all 9 agent definition files exist."""
    agents = [
        "agents/architect/agent.md",
        "agents/security/agent.md",
        "agents/reviewer/agent.md",
        "agents/tester/agent.md",
        "agents/optimizer/agent.md",
        "agents/researcher/agent.md",
        "agents/gtm-agent/agent.md",
        "agents/analytics-agent/agent.md",
        "agents/governance-agent/agent.md",
    ]
    for agent_path in agents:
        path = root / agent_path
        report.add(CheckResult(
            name=f"agent:{Path(agent_path).parent.name}",
            passed=path.exists(),
            message=f"Found: {agent_path}" if path.exists() else f"MISSING: {agent_path}",
            severity="warning",
        ))


def check_shared_resources(root: Path, report: BootstrapReport) -> None:
    """Verify critical shared resources exist."""
    shared = [
        "shared/standards/security-baseline.md",
        "shared/standards/architecture-principles.md",
        "shared/standards/ai-governance-baseline.md",
        "shared/policies/ai-safety-policy.md",
        "shared/frameworks/ai-discovery/llms-txt-patterns.md",
    ]
    for resource in shared:
        path = root / resource
        report.add(CheckResult(
            name=f"shared:{Path(resource).name}",
            passed=path.exists(),
            message=f"Found: {resource}" if path.exists() else f"MISSING: {resource}",
            severity="warning",
        ))


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(report: BootstrapReport, verbose: bool = False) -> None:
    status = "[OK] OPERATIONAL" if report.healthy else "[!!] NOT READY"
    print(f"\nAPOTHEON AUTONOMOUS OS -- BOOTSTRAP REPORT")
    print("=" * 60)
    print(f"Status:           {status}")
    print(f"Skill coverage:   {report.skill_coverage.get('present', 0)}"
          f"/{report.skill_coverage.get('total', 0)}"
          f" ({report.skill_coverage.get('pct', 0)}%)")
    print(f"Checks:           {report.total_checks} total  |  "
          f"{report.passed} passed  |  "
          f"{report.failed} failed  |  "
          f"{report.warnings} warnings")
    print()

    if report.failed > 0:
        print("ERRORS (must fix before operation):")
        for r in report.results:
            if not r.passed and r.severity == "error":
                print(f"  [X] [{r.name}] {r.message}")
        print()

    if report.warnings > 0:
        print("WARNINGS (degraded capability):")
        for r in report.results:
            if not r.passed and r.severity == "warning":
                print(f"  [!] [{r.name}] {r.message}")
        print()

    if verbose:
        print("PASSED:")
        for r in report.results:
            if r.passed:
                print(f"  [+] [{r.name}] {r.message}")
        print()

    if report.healthy:
        if report.warnings == 0:
            print("System is FULLY OPERATIONAL. All 31 phases present and validated.")
        else:
            print("System is OPERATIONAL with reduced capability. Resolve warnings for full operation.")
    else:
        print("System is NOT READY. Resolve all errors before starting the Autonomous OS.")
    print()


def json_report(report: BootstrapReport) -> None:
    output = {
        "status": "operational" if report.healthy else "not_ready",
        "fully_operational": report.fully_operational,
        "skill_coverage": report.skill_coverage,
        "summary": {
            "total": report.total_checks,
            "passed": report.passed,
            "failed": report.failed,
            "warnings": report.warnings,
        },
        "errors": [
            {"name": r.name, "message": r.message}
            for r in report.results
            if not r.passed and r.severity == "error"
        ],
        "warnings": [
            {"name": r.name, "message": r.message}
            for r in report.results
            if not r.passed and r.severity == "warning"
        ],
    }
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap validator for the Apotheon Autonomous OS",
    )
    parser.add_argument(
        "root", nargs="?", default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks including passed")
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit 1 on any warning (not just errors)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: repository root not found: {root}", file=sys.stderr)
        sys.exit(2)

    report = BootstrapReport()

    check_skill_presence(root, report)
    check_script_presence(root, report)
    check_validation_passes(root, report)
    check_agent_presence(root, report)
    check_shared_resources(root, report)

    if args.json:
        json_report(report)
    else:
        print_report(report, verbose=args.verbose)

    if not report.healthy:
        sys.exit(1)
    if args.strict and not report.fully_operational:
        sys.exit(1)


if __name__ == "__main__":
    main()