#!/usr/bin/env python3
"""
Route an ordered skill chain from a set of detected SDLC phases.

Accepts a JSON array of skill names on stdin or via --skills flag, outputs a
JSON workflow chain with dependency-ordered steps and parallel execution hints.

Usage:
    echo '["backend-engineering","devsecops","qa-automation"]' | python route_skill_chain.py
    python route_skill_chain.py --skills backend-engineering devsecops qa-automation
    python route_skill_chain.py --full-sdlc
"""
import argparse
import json
import sys
from collections import deque

# ---------------------------------------------------------------------------
# Skill registry
# All 13 domain skills with dependency metadata.
# Mirrors core/orchestration/references/skill-dependency-graph.md.
# ---------------------------------------------------------------------------

SKILLS = {
    "requirements-engineering": {
        "phase": "requirements",
        "depends_on": [],
        "parallel_with": [],
        "standalone": True,
        "gate_before_next": "requirements-complete",
    },
    "system-architecture": {
        "phase": "architecture",
        "depends_on": [],  # requirements preferred but not required
        "parallel_with": [],
        "standalone": True,
        "gate_before_next": "architecture-approved",
    },
    "ai-engineering": {
        "phase": "ai-engineering",
        "depends_on": ["system-architecture"],
        "parallel_with": [],
        "standalone": False,
        "gate_before_next": "ai-design-approved",
    },
    "backend-engineering": {
        "phase": "backend",
        "depends_on": ["system-architecture"],
        "parallel_with": ["ai-engineering"],
        "standalone": False,
        "gate_before_next": "backend-implementation-ready",
    },
    "frontend-engineering": {
        "phase": "frontend",
        "depends_on": ["system-architecture", "backend-engineering"],
        "parallel_with": ["ai-engineering"],
        "standalone": False,
        "gate_before_next": None,
    },
    "devsecops": {
        "phase": "security",
        # Minimum dependency is system-architecture; backend preferred.
        # For routing purposes we treat system-architecture as the hard dep.
        "depends_on": ["system-architecture"],
        "parallel_with": ["qa-automation"],
        "standalone": False,
        "gate_before_next": "security-review-passed",
    },
    "qa-automation": {
        "phase": "qa",
        # Requires at least one implementation artifact.
        "depends_on": ["backend-engineering"],
        "parallel_with": ["devsecops", "code-review"],
        "standalone": False,
        "gate_before_next": "test-strategy-accepted",
    },
    "code-review": {
        "phase": "code-review",
        "depends_on": [],
        "parallel_with": ["devsecops", "qa-automation"],
        "standalone": True,
        "gate_before_next": None,
    },
    "release-management": {
        "phase": "release",
        "depends_on": ["qa-automation", "devsecops"],
        "parallel_with": ["compliance-governance"],
        "standalone": False,
        "gate_before_next": "release-readiness-confirmed",
    },
    "observability": {
        "phase": "observability",
        "depends_on": ["release-management"],
        "parallel_with": [],
        "standalone": False,
        "gate_before_next": "operations-readiness-confirmed",
    },
    "sre-incident-response": {
        "phase": "operations",
        "depends_on": ["observability"],
        "parallel_with": [],
        "standalone": True,  # can triage active incidents immediately
        "gate_before_next": None,
    },
    "compliance-governance": {
        "phase": "compliance",
        "depends_on": ["devsecops", "qa-automation"],
        "parallel_with": ["release-management"],
        "standalone": False,
        "gate_before_next": None,
    },
    "executive-reporting": {
        "phase": "reporting",
        "depends_on": [],
        "parallel_with": [],
        "standalone": True,
        "gate_before_next": None,
    },
}

FULL_SDLC_SKILLS = [
    "requirements-engineering",
    "system-architecture",
    "ai-engineering",
    "backend-engineering",
    "frontend-engineering",
    "devsecops",
    "qa-automation",
    "code-review",
    "release-management",
    "observability",
    "sre-incident-response",
    "compliance-governance",
    "executive-reporting",
]


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def validate_skills(skill_names: list[str]) -> tuple[list[str], list[str]]:
    """Split skill names into known and unknown."""
    known = [s for s in skill_names if s in SKILLS]
    unknown = [s for s in skill_names if s not in SKILLS]
    return known, unknown


def resolve_dependencies(requested: list[str]) -> list[str]:
    """
    Expand the requested skill set by adding any dependencies that are not
    already present. Uses breadth-first expansion so direct dependencies of
    the requested skills are always included.
    """
    expanded = set(requested)
    queue = deque(requested)
    while queue:
        skill = queue.popleft()
        for dep in SKILLS[skill]["depends_on"]:
            if dep not in expanded:
                expanded.add(dep)
                queue.append(dep)
    return list(expanded)


def topological_sort(skills: list[str]) -> list[str]:
    """
    Return skills in dependency order using Kahn's algorithm.
    Only considers edges between skills in the provided set.
    Raises ValueError if a cycle is detected (not possible with current graph,
    but guarded for future changes).
    """
    skill_set = set(skills)
    # Build in-degree map restricted to the current skill set
    in_degree: dict[str, int] = {s: 0 for s in skills}
    dependents: dict[str, list[str]] = {s: [] for s in skills}

    for skill in skills:
        for dep in SKILLS[skill]["depends_on"]:
            if dep in skill_set:
                in_degree[skill] += 1
                dependents[dep].append(skill)

    # Start with skills that have no in-set dependencies
    # Stable sort by FULL_SDLC_SKILLS order for deterministic output
    def sdlc_order(s: str) -> int:
        try:
            return FULL_SDLC_SKILLS.index(s)
        except ValueError:
            return len(FULL_SDLC_SKILLS)

    ready = sorted([s for s in skills if in_degree[s] == 0], key=sdlc_order)
    result = []

    while ready:
        skill = ready.pop(0)
        result.append(skill)
        for dependent in sorted(dependents[skill], key=sdlc_order):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                ready.append(dependent)
                ready.sort(key=sdlc_order)

    if len(result) != len(skills):
        cyclic = [s for s in skills if s not in result]
        raise ValueError(f"Dependency cycle detected among: {cyclic}")

    return result


def compute_parallel_groups(ordered: list[str]) -> list[list[str]]:
    """
    Group skills into parallel execution steps.
    Skills in the same group have no mutual dependencies within the set.
    """
    skill_set = set(ordered)
    groups: list[list[str]] = []
    assigned: set[str] = set()

    for skill in ordered:
        if skill in assigned:
            continue
        # Find all skills that can run in parallel with this one
        # (within the ordered list, not yet assigned, mutually independent)
        group = [skill]
        for candidate in ordered:
            if candidate in assigned or candidate == skill:
                continue
            # candidate can join group if:
            # 1. it has no dependency on any skill in the group
            # 2. no skill in the group depends on it
            # 3. the dependency graph explicitly lists them as parallel_with
            can_parallel = True
            for member in group:
                member_deps = set(SKILLS[member]["depends_on"])
                candidate_deps = set(SKILLS[candidate]["depends_on"])
                if member in candidate_deps or candidate in member_deps:
                    can_parallel = False
                    break
                # Require explicit parallel_with declaration for safety (symmetric: either side)
                if (candidate not in SKILLS[member]["parallel_with"]
                        and member not in SKILLS[candidate]["parallel_with"]):
                    can_parallel = False
                    break
            if can_parallel:
                group.append(candidate)

        groups.append(group)
        assigned.update(group)

    return groups


def build_chain(requested: list[str], expand_deps: bool = True) -> dict:
    """
    Build a routed skill chain from a list of requested skill names.

    Returns a dict with:
      - skill_chain: ordered steps with metadata
      - parallel_groups: grouped execution steps
      - unknown_skills: any unrecognised skill names
      - dependency_additions: skills added to satisfy dependencies
    """
    known, unknown = validate_skills(requested)

    if expand_deps:
        expanded = resolve_dependencies(known)
        additions = [s for s in expanded if s not in known]
    else:
        expanded = known
        additions = []

    ordered = topological_sort(expanded)
    groups = compute_parallel_groups(ordered)

    # Build step list
    steps = []
    for i, skill in enumerate(ordered, start=1):
        meta = SKILLS[skill]
        # Only emit gate_before_next if the next skill in chain exists
        is_last = (i == len(ordered))
        gate = meta["gate_before_next"] if not is_last else None

        steps.append({
            "step": i,
            "skill": skill,
            "phase": meta["phase"],
            "depends_on": [d for d in meta["depends_on"] if d in set(expanded)],
            "gate_before_next": gate,
        })

    # Build parallel group steps
    group_steps = []
    for gi, group in enumerate(groups, start=1):
        group_steps.append({
            "group": gi,
            "parallel": len(group) > 1,
            "skills": group,
        })

    complexity = _infer_complexity(known)

    return {
        "complexity": complexity,
        "skill_chain": steps,
        "execution_groups": group_steps,
        "dependency_additions": additions,
        "unknown_skills": unknown,
    }


def _infer_complexity(ordered: list[str]) -> str:
    n = len(ordered)
    if n <= 1:
        return "single-phase"
    if n <= 4:
        return "multi-phase"
    return "full-sdlc"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Route an ordered skill chain from detected SDLC phases."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--skills",
        nargs="+",
        metavar="SKILL",
        help="Space-separated skill names to route.",
    )
    group.add_argument(
        "--full-sdlc",
        action="store_true",
        help="Route all skills in the full SDLC order.",
    )
    parser.add_argument(
        "--no-expand",
        action="store_true",
        help="Do not automatically add missing dependency skills.",
    )
    args = parser.parse_args()

    if args.full_sdlc:
        requested = list(FULL_SDLC_SKILLS)
    elif args.skills:
        requested = args.skills
    else:
        try:
            requested = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError) as exc:
            print(json.dumps({"error": f"Invalid JSON input: {exc}"}), file=sys.stderr)
            sys.exit(1)

    if not isinstance(requested, list):
        print(json.dumps({"error": "Input must be a JSON array of skill names."}), file=sys.stderr)
        sys.exit(1)

    try:
        result = build_chain(requested, expand_deps=not args.no_expand)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    if result["unknown_skills"]:
        result["warnings"] = [
            f"Unknown skill ignored: '{s}'" for s in result["unknown_skills"]
        ]

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()