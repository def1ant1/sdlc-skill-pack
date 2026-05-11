#!/usr/bin/env python3
"""
plan_gtm_workflow.py — Generate a GTM Workflow Plan from a natural-language objective.

Routes go-to-market objectives to the correct sequence of GTM skills,
producing a plan JSON compatible with execute_workflow.py.

GTM skills registered:
  launch-planning, seo-engineering, content-marketing, ai-search-optimization,
  paid-acquisition, analytics-intelligence, customer-success, revenue-optimization

Usage:
    python scripts/orchestration/plan_gtm_workflow.py "Launch a new SaaS product"
    python scripts/orchestration/plan_gtm_workflow.py "Improve organic search and reduce churn"
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import hashlib

# ---------------------------------------------------------------------------
# GTM skill registry
# skill_name → (phase_label, primary_signals, supporting_signals)
# ---------------------------------------------------------------------------

_GTM_SKILLS: list[tuple[str, str, list[str], list[str]]] = [
    (
        "launch-planning",
        "launch",
        ["launch", "go-to-market", "gtm", "announce", "release", "ship", "product launch",
         "launch date", "launch plan", "launch brief", "launch strategy"],
        ["coordinate", "prepare", "readiness", "milestone", "timeline"],
    ),
    (
        "seo-engineering",
        "organic-search",
        ["seo", "organic", "search engine", "keyword", "ranking", "serp", "crawl",
         "backlink", "technical seo", "core web vitals", "sitemap", "robots.txt"],
        ["visibility", "traffic", "search visibility", "page speed"],
    ),
    (
        "content-marketing",
        "content",
        ["content", "blog", "article", "copywriting", "editorial", "content strategy",
         "thought leadership", "content calendar", "whitepaper", "case study"],
        ["writing", "publish", "asset", "storytelling", "narrative"],
    ),
    (
        "ai-search-optimization",
        "ai-search",
        ["ai search", "geo", "llm visibility", "sge", "generative engine",
         "ai overview", "perplexity", "chatgpt search", "ai-powered search",
         "llm citation", "answer engine"],
        ["optimize for ai", "featured in ai", "brand mentions in llm"],
    ),
    (
        "paid-acquisition",
        "paid",
        ["paid", "ads", "ppc", "google ads", "linkedin ads", "facebook ads",
         "paid search", "paid social", "cpc", "cpm", "roas", "campaign", "ad spend",
         "acquisition", "demand generation"],
        ["budget", "bid", "conversion", "retargeting", "prospecting"],
    ),
    (
        "analytics-intelligence",
        "analytics",
        ["analytics", "attribution", "tracking", "events", "ga4", "mixpanel",
         "amplitude", "segment", "data pipeline", "funnel", "conversion tracking",
         "event taxonomy", "measurement", "reporting"],
        ["instrument", "data", "insight", "dashboard", "kpi"],
    ),
    (
        "customer-success",
        "retention",
        ["customer success", "onboarding", "churn", "retention", "nps", "csat",
         "customer health", "expansion", "renewal", "support", "customer journey",
         "cs playbook", "qbr"],
        ["customer", "satisfaction", "loyalty", "upsell"],
    ),
    (
        "revenue-optimization",
        "revenue",
        ["revenue", "pricing", "ltv", "mrr", "arr", "churn rate", "monetization",
         "pricing strategy", "revenue optimization", "expansion revenue",
         "upsell", "cross-sell", "cac", "payback period", "unit economics"],
        ["optimize revenue", "grow revenue", "increase mrr", "reduce churn"],
    ),
]

# Dependency ordering: skills that should run before others when co-selected
_DEPENDENCY_ORDER: dict[str, list[str]] = {
    "launch-planning": [],
    "analytics-intelligence": ["launch-planning"],
    "seo-engineering": ["analytics-intelligence"],
    "content-marketing": ["seo-engineering"],
    "ai-search-optimization": ["content-marketing"],
    "paid-acquisition": ["analytics-intelligence"],
    "customer-success": ["launch-planning"],
    "revenue-optimization": ["customer-success", "analytics-intelligence"],
}


def _score_skill(objective_lower: str, primary: list[str], supporting: list[str]) -> int:
    """Return a match score for a skill against an objective string."""
    score = 0
    for sig in primary:
        if sig in objective_lower:
            score += 3
    for sig in supporting:
        if sig in objective_lower:
            score += 1
    return score


def route_gtm(objective: str) -> tuple[list[str], bool]:
    """Return ordered list of GTM skill names matching the objective."""
    obj_lower = objective.lower()
    scored = []
    for skill_name, _phase, primary, supporting in _GTM_SKILLS:
        s = _score_skill(obj_lower, primary, supporting)
        if s > 0:
            scored.append((s, skill_name))

    if not scored:
        return [s[0] for s in _GTM_SKILLS], True

    top = max(score for score, _ in scored)
    ambiguous = sum(1 for score, _ in scored if score == top) > 1

    selected = {name for _, name in scored}

    # Topological sort respecting dependency order
    ordered: list[str] = []
    visited: set[str] = set()

    def visit(skill: str) -> None:
        if skill in visited:
            return
        visited.add(skill)
        for dep in _DEPENDENCY_ORDER.get(skill, []):
            if dep in selected:
                visit(dep)
        ordered.append(skill)

    # Sort selected by original registry order for stable output
    registry_order = [s[0] for s in _GTM_SKILLS]
    for skill in registry_order:
        if skill in selected:
            visit(skill)

    return ordered, ambiguous


def build_plan(objective: str) -> dict:
    """Build a GTM workflow plan JSON."""
    skills, ambiguous = route_gtm(objective)
    skill_data = {s[0]: s for s in _GTM_SKILLS}

    stable_seed = objective.strip().lower()
    plan_id = f"GTM-{datetime.date.today().strftime('%Y%m%d')}-{hashlib.sha1(stable_seed.encode()).hexdigest()[:8]}"

    skill_chain = []
    for i, skill_name in enumerate(skills, start=1):
        _name, phase, _primary, _supporting = skill_data[skill_name]
        deps = [d for d in _DEPENDENCY_ORDER.get(skill_name, []) if d in set(skills)]
        skill_chain.append({
            "step": i,
            "skill": skill_name,
            "phase": phase,
            "depends_on": deps,
            "gate_before_next": None,
        })

    diagnostics = {"objective_non_empty": bool(objective.strip()), "selected_skills_exist": True, "dependency_completeness": True, "ambiguous_routing": ambiguous, "missing_required_skills": [], "missing_optional_skills": [], "warnings": (["Objective maps to multiple GTM skills at equal confidence."] if ambiguous else [])}

    return {
        "plan_id": plan_id,
        "created": datetime.date.today().isoformat(),
        "objective": objective,
        "planner": "gtm",
        "skill_chain": skill_chain,
        "planner_diagnostics": diagnostics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a GTM workflow plan")
    parser.add_argument("objective", nargs="?", help="GTM objective text")
    parser.add_argument("--stdin", action="store_true", help="Read objective from stdin")
    args = parser.parse_args()

    if args.stdin or not args.objective:
        objective = sys.stdin.read().strip()
    else:
        objective = args.objective

    if not objective:
        print("Error: objective is required", file=sys.stderr)
        return 1

    plan = build_plan(objective)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())