#!/usr/bin/env python3
"""
Generate a structured SDLC Workflow Plan from a natural-language objective.

Pipeline:
  1. Classify intent → detect SDLC phases and confidence levels
  2. Route skill chain → topological order with dependency expansion
  3. Assemble workflow plan → full JSON matching workflow-plan-template schema

Usage:
    python plan_workflow.py "Build a secure AI document processing API"
    python plan_workflow.py --objective "Add user auth to existing service" --no-expand
    echo "Design and deploy a payment microservice" | python plan_workflow.py --stdin
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import route_skill_chain from the same package directory
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
from route_skill_chain import build_chain, SKILLS  # noqa: E402


# ---------------------------------------------------------------------------
# Intent classification
# Maps keyword signals to SDLC phases.
# Mirrors core/orchestration/references/intent-classification.md.
# ---------------------------------------------------------------------------

# Each entry: (phase_key, skill_name, primary_signals, supporting_signals, negative_signals)
_CLASSIFICATION_RULES: list[tuple[str, str, list[str], list[str], list[str]]] = [
    (
        "requirements",
        "requirements-engineering",
        ["requirement", "prd", "user stor", "acceptance criteria", "scope", "feature spec",
         "product brief", "epic", "use case", "traceability", "stakeholder", "backlog item",
         "functional requirement", "non-functional requirement"],
        ["define what", "capture needs", "clarify scope", "write stories", "document requirements"],
        ["implement", "code the", "deploy", "write tests", "review pr"],
    ),
    (
        "architecture",
        "system-architecture",
        ["architecture", "adr", "system design", "service boundary", "data model",
         "integration pattern", "component", "non-functional", "scalability", "reliability",
         "technology choice", "tech stack", "monolith", "microservice", "event-driven",
         "design decision", "tradeoff"],
        ["how should we structure", "what pattern", "design the system", "quality attribute"],
        ["implement the code", "write the function", "fix this bug"],
    ),
    (
        "ai-engineering",
        "ai-engineering",
        ["llm", " ai ", "ai-", "agent", "rag", "embedding", "vector", "prompt", "model selection",
         "fine-tun", "inference", "evaluation", "eval", "ai safety", "hallucination",
         "retrieval", "tool use", "claude", "gpt", "openai", "generative", "anthropic",
         "langchain", "semantic kernel"],
        ["ai-powered", "ai-enabled", "intelligent", "nlp", "chatbot", "recommendation",
         "classification model", "ai pipeline"],
        ["no ai", "traditional algorithm", "rules-based only"],
    ),
    (
        "backend",
        "backend-engineering",
        ["api", "rest", "graphql", "grpc", "service", "backend", "database", "schema",
         "endpoint", "controller", "repository", "orm", "authentication", "authorization",
         "server", "microservice", "message broker", "queue", "implementation plan",
         "business logic", "crud"],
        ["build the service", "implement the api", "write the backend", "data access layer"],
        ["frontend only", "ui only", "no backend"],
    ),
    (
        "frontend",
        "frontend-engineering",
        ["frontend", " ui ", "react", "vue", "angular", "component", "page", "accessibility",
         "responsive", "design system", "css", "state management", "client-side", "web app",
         "user interface", "ux"],
        ["build the ui", "implement the page", "make it accessible", "design the component"],
        ["backend only", "no ui", "api only"],
    ),
    (
        "security",
        "devsecops",
        ["security", "threat model", "owasp", "vulnerability", "cve", "secrets management",
         "jwt", "oauth", "rbac", "supply chain", "sast", "dast", "penetration test",
         "hardening", "encryption", "tls", "zero trust", "ci security", "devsecops",
         "secure", "auth"],
        ["is this secure", "security review", "check for vulnerabilities", "compliance scan"],
        ["no security concerns", "internal tool only", "prototype only"],
    ),
    (
        "qa",
        "qa-automation",
        ["test", "qa", "coverage", "unit test", "integration test", "end-to-end", "regression",
         "test strategy", "test plan", "automation", "pytest", "jest", "playwright",
         "cypress", "performance test", "load test", "ai eval", "evaluation harness"],
        ["write tests for", "validate the behavior", "ensure correctness", "test coverage"],
        ["no tests needed", "prototype only", "skip testing"],
    ),
    (
        "code-review",
        "code-review",
        ["review", " pr ", "pull request", "code quality", "refactor", "maintainability",
         "readability", "technical debt", "smell", "lint", "static analysis",
         "review this code", "review this implementation", "feedback on this code"],
        ["is this code good", "what can be improved", "clean up this code"],
        ["implement new feature", "write from scratch"],
    ),
    (
        "release",
        "release-management",
        ["release", "deploy", "deployment", "ci/cd", "pipeline", "rollout", "rollback",
         "version", "semver", "changelog", "feature flag", "canary", "blue-green",
         "gitops", "helm", "kubernetes", "release checklist", "release readiness"],
        ["ship it", "go to production", "release plan", "deployment strategy", "release notes"],
        ["local only", "not deploying", "development only"],
    ),
    (
        "observability",
        "observability",
        ["observability", "logging", "metrics", "traces", "slo", "sla", "dashboard",
         "alert", "monitoring", "datadog", "prometheus", "grafana", "opentelemetry",
         "distributed tracing", "error rate", "latency"],
        ["how do we know it works", "visibility into", "operational readiness", "detect issues"],
        ["no production deployment", "prototype only"],
    ),
    (
        "operations",
        "sre-incident-response",
        ["incident", "outage", "postmortem", "on-call", "runbook", "mitigation", "triage",
         "sre", "reliability", "downtime", "degradation", "pagerduty", "blameless",
         "root cause", "remediation", "incident report"],
        ["something is broken", "investigate this failure", "create a postmortem"],
        ["pre-production", "planning phase", "no incidents yet"],
    ),
    (
        "compliance",
        "compliance-governance",
        ["compliance", "audit", "governance", "soc 2", "gdpr", "hipaa", "pci",
         "iso 27001", "policy", "control", "evidence", "risk register",
         "data classification", "ai act", "regulatory", "traceability matrix"],
        ["are we compliant", "audit evidence", "policy mapping", "governance review"],
        ["ignore compliance", "prototype only, no compliance"],
    ),
    (
        "reporting",
        "executive-reporting",
        ["status report", "executive summary", "leadership update", "delivery health",
         "roadmap status", "risk summary", "stakeholder brief", "board report",
         "program update", "okr status"],
        ["summarize for leadership", "delivery status", "report out on this project"],
        ["technical deep dive", "implementation details"],
    ),
]

# Phase dependency order for sorting and gap-filling
_PHASE_ORDER = [
    "requirements", "architecture", "ai-engineering", "backend", "frontend",
    "security", "qa", "code-review", "release", "observability", "operations",
    "compliance", "reporting",
]


def classify_intent(text: str) -> list[dict]:
    """
    Return a list of detected phase entries ordered by phase sequence.
    Each entry: {phase, skill, confidence, rationale}.
    """
    lowered = f" {text.lower()} "
    detected: list[dict] = []

    for phase, skill, primary, supporting, negative in _CLASSIFICATION_RULES:
        primary_hits = [s for s in primary if s in lowered]
        supporting_hits = [s for s in supporting if s in lowered]
        negative_hits = [s for s in negative if s in lowered]

        # Negative signals dominate only when there are no primary hits
        if negative_hits and not primary_hits:
            continue

        if len(primary_hits) >= 2:
            confidence = "high"
        elif len(primary_hits) == 1:
            confidence = "high" if not negative_hits else "medium"
        elif supporting_hits:
            confidence = "medium" if not negative_hits else "low"
        else:
            continue

        rationale = (
            f"Matched primary signals: {primary_hits[:3]}"
            if primary_hits
            else f"Matched supporting signals: {supporting_hits[:2]}"
        )
        detected.append(
            {"phase": phase, "skill": skill, "confidence": confidence, "rationale": rationale}
        )

    # Sort by canonical phase order
    order_map = {p: i for i, p in enumerate(_PHASE_ORDER)}
    detected.sort(key=lambda d: order_map.get(d["phase"], 99))
    return detected


def _infer_complexity(skill_count: int) -> str:
    if skill_count <= 1:
        return "single-phase"
    if skill_count <= 4:
        return "multi-phase"
    return "full-sdlc"


def _select_quality_gates(ordered_skills: list[str]) -> list[dict]:
    """Collect gate_before_next entries from the ordered chain."""
    gates = []
    for i, skill in enumerate(ordered_skills[:-1]):
        gate_name = SKILLS[skill].get("gate_before_next")
        if gate_name:
            next_skill = ordered_skills[i + 1]
            next_phase = SKILLS[next_skill]["phase"]
            gates.append({
                "gate_name": gate_name,
                "transition": f"{SKILLS[skill]['phase']} → {next_phase}",
                "fail_action": "block",
            })
    return gates


def _estimate_token_budget(complexity: str, skill_count: int) -> dict:
    """Produce a rough token budget estimate."""
    if complexity == "single-phase":
        total = 12_000
        alloc = dict(planning=600, source_context=2400, reasoning=3600, output=4800, buffer=600)
    elif complexity == "multi-phase":
        total = 8_000 * skill_count
        alloc = dict(
            planning=int(total * 0.08),
            source_context=int(total * 0.25),
            reasoning=int(total * 0.30),
            output=int(total * 0.30),
            buffer=int(total * 0.07),
        )
    else:  # full-sdlc
        total = max(60_000, 10_000 * skill_count)
        alloc = dict(
            planning=int(total * 0.10),
            source_context=int(total * 0.20),
            reasoning=int(total * 0.30),
            output=int(total * 0.30),
            buffer=int(total * 0.10),
        )
    return {"total_estimated": total, "allocation": alloc, "compression_trigger": "75%"}


def _build_plan_id() -> str:
    today = datetime.date.today().strftime("%Y%m%d")
    return f"WP-{today}-001"


def _memory_strategy(detected_phases: list[dict]) -> dict:
    phases = [d["phase"] for d in detected_phases]
    compress_after = [f"Intermediate reasoning from {p} phase" for p in phases]
    return {
        "preserve": [
            "user objective",
            "accepted decisions and ADRs",
            "all quality gate statuses",
            "open questions and constraints",
            "artifact names and locations",
            "remediation tasks from failed gates",
        ],
        "compress_after": compress_after + [
            "raw conversation turns after each phase completion",
            "superseded design drafts",
        ],
    }


def plan(objective: str, expand_deps: bool = True) -> dict:
    """
    Produce a full workflow plan dict for the given objective string.
    Raises ValueError if no phases are detected.
    """
    detected = classify_intent(objective)

    if not detected:
        # Fall back to requirements + architecture as a safe default
        detected = [
            {
                "phase": "requirements",
                "skill": "requirements-engineering",
                "confidence": "low",
                "rationale": "No specific signals detected; defaulting to requirements phase.",
            }
        ]

    requested_skills = [d["skill"] for d in detected]
    chain = build_chain(requested_skills, expand_deps=expand_deps)

    ordered_skills = [s["skill"] for s in chain["skill_chain"]]
    complexity = chain["complexity"]

    # Annotate detected_phases with any dependency additions
    added_skills = set(chain["dependency_additions"])
    all_detected = list(detected)
    for skill in chain["dependency_additions"]:
        phase = SKILLS[skill]["phase"]
        all_detected.append({
            "phase": phase,
            "skill": skill,
            "confidence": "high",
            "rationale": f"Added automatically to satisfy dependency for requested skills.",
        })
    order_map = {p: i for i, p in enumerate(_PHASE_ORDER)}
    all_detected.sort(key=lambda d: order_map.get(d["phase"], 99))

    quality_gates = _select_quality_gates(ordered_skills)
    token_budget = _estimate_token_budget(complexity, len(ordered_skills))
    memory_strategy = _memory_strategy(all_detected)

    next_skill = ordered_skills[0] if ordered_skills else "requirements-engineering"

    diagnostics = {
        "objective_non_empty": bool(objective.strip()),
        "selected_skills_exist": len(chain["unknown_skills"]) == 0,
        "dependency_completeness": True,
        "ambiguous_routing": len(detected) > 1 and all(d["confidence"] == detected[0]["confidence"] for d in detected),
        "missing_required_skills": sorted(chain["unknown_skills"]),
        "missing_optional_skills": [],
        "warnings": [],
    }

    return {
        "plan_id": _build_plan_id(),
        "created": datetime.date.today().isoformat(),
        "objective": objective,
        "complexity": complexity,
        "classification_confidence": detected[0]["confidence"] if detected else "low",
        "detected_phases": all_detected,
        "skill_chain": chain["skill_chain"],
        "execution_groups": chain["execution_groups"],
        "quality_gates": quality_gates,
        "memory_strategy": memory_strategy,
        "token_budget": token_budget,
        "dependency_additions": chain["dependency_additions"],
        "unknown_skills": chain["unknown_skills"],
        "planner_diagnostics": diagnostics,
        "next_action": {
            "description": f"Load {next_skill} skill and begin phase execution.",
            "skill": next_skill,
            "input_needed": None,
            "gate_to_pass": "N/A",
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a structured SDLC Workflow Plan from a natural-language objective."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("objective", nargs="?", help="Objective string.")
    source.add_argument("--stdin", action="store_true", help="Read objective from stdin.")
    parser.add_argument("--no-expand", action="store_true",
                        help="Do not auto-add dependency skills.")
    args = parser.parse_args()

    if args.stdin:
        objective = sys.stdin.read().strip()
    elif args.objective:
        objective = args.objective
    else:
        parser.error("Provide an objective as a positional argument or use --stdin.")

    if not objective:
        parser.error("Objective must not be empty.")

    try:
        result = plan(objective, expand_deps=not args.no_expand)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()