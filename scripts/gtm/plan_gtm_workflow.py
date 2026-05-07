#!/usr/bin/env python3
"""
GTM Workflow Planner

Classifies a go-to-market objective and produces a structured GTM workflow plan.

Usage:
    python plan_gtm_workflow.py "launch our AI document processing SaaS to SMB market"
    python plan_gtm_workflow.py --stdin < objective.txt
    echo "optimize SEO and set up paid acquisition" | python plan_gtm_workflow.py --stdin
"""

from __future__ import annotations

import json
import sys
import argparse
from datetime import date
from typing import Optional

# ---------------------------------------------------------------------------
# GTM Phase definitions
# ---------------------------------------------------------------------------

GTM_PHASES = [
    "launch-planning",
    "seo-engineering",
    "content-marketing",
    "ai-search-optimization",
    "paid-acquisition",
    "analytics-intelligence",
    "customer-success",
    "revenue-optimization",
]

# Each rule: (phase, primary_skill, primary_signals, supporting_signals, negative_signals)
_GTM_CLASSIFICATION_RULES: list[tuple[str, str, list[str], list[str], list[str]]] = [
    (
        "launch-planning",
        "launch-planning",
        ["launch", "go live", "ship to market", "go-to-market", "gtm", "release to market", "product launch"],
        ["positioning", "icp", "messaging", "value proposition", "competitive", "market entry"],
        ["internal", "dev only", "infrastructure only"],
    ),
    (
        "seo-engineering",
        "seo-engineering",
        ["seo", "search ranking", "organic traffic", "search engine", "backlinks", "technical seo", "serp"],
        ["keyword", "domain authority", "sitemap", "crawl", "indexing", "meta tags"],
        ["paid only", "no website", "api only"],
    ),
    (
        "ai-search-optimization",
        "ai-search-optimization",
        ["ai search", "llm discovery", "llms.txt", "answer engine", "chatgpt visibility", "ai-powered search"],
        ["semantic search", "vector search", "ai discoverability", "capability manifest", "ai traffic"],
        ["traditional seo only", "no content"],
    ),
    (
        "content-marketing",
        "content-marketing",
        ["content", "blog", "article", "newsletter", "editorial calendar", "content strategy"],
        ["thought leadership", "case study", "whitepaper", "video", "podcast", "copywriting"],
        ["no content budget", "product-led only"],
    ),
    (
        "paid-acquisition",
        "paid-acquisition",
        ["paid ads", "google ads", "meta ads", "ppc", "acquisition", "paid campaign", "advertising budget"],
        ["cac", "roas", "cpm", "cpc", "retargeting", "linkedin ads", "tiktok ads", "paid social"],
        ["organic only", "no ad budget", "bootstrapped with zero marketing spend"],
    ),
    (
        "analytics-intelligence",
        "analytics-intelligence",
        ["analytics", "dashboard", "metrics", "funnel", "attribution", "conversion rate", "tracking"],
        ["ga4", "mixpanel", "amplitude", "segment", "data pipeline", "reporting", "kpis"],
        ["no measurement needed"],
    ),
    (
        "customer-success",
        "customer-success",
        ["customer success", "onboarding", "churn", "nps", "retention", "csat", "customer health"],
        ["support", "cs team", "helpdesk", "user adoption", "activation", "time-to-value"],
        ["b2c mass market", "self-serve only with no cs"],
    ),
    (
        "revenue-optimization",
        "revenue-optimization",
        ["revenue", "pricing", "upsell", "expansion", "arr", "mrr", "ltv", "monetization"],
        ["net revenue retention", "nrr", "expansion revenue", "pricing strategy", "packaging"],
        ["non-commercial", "open source only", "free tier only"],
    ),
]

# Phase dependency graph
_GTM_DEPS: dict[str, list[str]] = {
    "launch-planning": [],
    "seo-engineering": ["launch-planning"],
    "content-marketing": ["launch-planning"],
    "ai-search-optimization": ["seo-engineering"],
    "paid-acquisition": ["launch-planning", "content-marketing"],
    "analytics-intelligence": ["launch-planning"],
    "customer-success": ["launch-planning"],
    "revenue-optimization": ["analytics-intelligence", "customer-success"],
}

# Explicit parallel pairs
_PARALLEL_WITH: dict[str, list[str]] = {
    "seo-engineering": ["content-marketing"],
    "content-marketing": ["seo-engineering"],
    "paid-acquisition": ["analytics-intelligence", "ai-search-optimization"],
    "analytics-intelligence": ["paid-acquisition"],
    "ai-search-optimization": ["paid-acquisition"],
}

# Channel recommendations by phase
_CHANNEL_HINTS: dict[str, list[str]] = {
    "launch-planning": ["product-hunt", "pr", "email-list"],
    "seo-engineering": ["organic-search", "backlink-outreach"],
    "content-marketing": ["blog", "newsletter", "social-media"],
    "ai-search-optimization": ["ai-directories", "llms-txt", "capability-manifest"],
    "paid-acquisition": ["google-ads", "linkedin-ads", "meta-ads"],
    "analytics-intelligence": ["ga4", "mixpanel"],
    "customer-success": ["intercom", "zendesk", "customer-portal"],
    "revenue-optimization": ["pricing-page", "upsell-flows", "expansion-outreach"],
}


def classify_gtm_intent(text: str) -> list[dict]:
    """
    Classify a GTM objective into a list of detected phases with confidence.

    Returns a list of dicts sorted by confidence (high first), each with:
      - phase: str
      - primary_skill: str
      - confidence: "high" | "medium" | "low"
      - rationale: str
      - matched_signals: list[str]
    """
    normalized = f" {text.lower()} "
    results = []

    for phase, primary_skill, primary_sigs, supporting_sigs, negative_sigs in _GTM_CLASSIFICATION_RULES:
        # Check negative signals — skip if any match
        neg_hits = [s for s in negative_sigs if s in normalized]
        if neg_hits:
            continue

        primary_hits = [s for s in primary_sigs if s in normalized]
        supporting_hits = [s for s in supporting_sigs if s in normalized]

        if primary_hits:
            confidence = "high" if len(primary_hits) >= 2 else "medium" if supporting_hits else "medium"
        elif supporting_hits:
            confidence = "low"
        else:
            continue

        rationale_parts = []
        if primary_hits:
            rationale_parts.append(f"primary signals: {', '.join(primary_hits[:3])}")
        if supporting_hits:
            rationale_parts.append(f"supporting: {', '.join(supporting_hits[:2])}")

        results.append({
            "phase": phase,
            "primary_skill": primary_skill,
            "confidence": confidence,
            "rationale": "; ".join(rationale_parts),
            "matched_signals": primary_hits + supporting_hits,
        })

    # Sort: high → medium → low
    order = {"high": 0, "medium": 1, "low": 2}
    results.sort(key=lambda r: order[r["confidence"]])
    return results


def _resolve_dependencies(phases: list[str]) -> list[str]:
    """Expand phase list to include all transitive dependencies."""
    visited: set[str] = set()
    queue = list(phases)
    while queue:
        p = queue.pop(0)
        if p in visited:
            continue
        visited.add(p)
        for dep in _GTM_DEPS.get(p, []):
            if dep not in visited:
                queue.append(dep)
    # Return in canonical GTM_PHASES order
    return [p for p in GTM_PHASES if p in visited]


def _compute_complexity(phases: list[str]) -> str:
    if len(phases) == 1:
        return "single-phase"
    if len(phases) >= len(GTM_PHASES):
        return "full-gtm"
    return "multi-phase"


def _build_skill_chain(ordered_phases: list[str]) -> list[dict]:
    """Build ordered skill chain steps with inputs, outputs, and parallel annotations."""
    chain = []
    gate_map = {
        "launch-planning": "launch-plan-approved",
        "seo-engineering": "seo-baseline-complete",
        "content-marketing": "content-strategy-approved",
        "ai-search-optimization": "ai-discovery-validated",
        "paid-acquisition": "campaign-brief-approved",
        "analytics-intelligence": "analytics-baseline-set",
        "customer-success": "onboarding-flow-live",
        "revenue-optimization": "revenue-model-approved",
    }
    outputs_map = {
        "launch-planning": ["positioning-doc", "icp-definition", "messaging-framework", "launch-brief"],
        "seo-engineering": ["technical-seo-report", "keyword-map", "sitemap"],
        "content-marketing": ["content-calendar", "launch-blog-post", "social-copy"],
        "ai-search-optimization": ["llms-txt", "capability-manifest", "semantic-audit-report"],
        "paid-acquisition": ["campaign-briefs", "ad-creative-set", "landing-pages"],
        "analytics-intelligence": ["analytics-dashboard", "tracking-plan", "kpi-baseline"],
        "customer-success": ["onboarding-flow", "cs-runbook", "nps-baseline"],
        "revenue-optimization": ["pricing-model", "expansion-playbook", "revenue-dashboard"],
    }
    for phase in ordered_phases:
        deps = _GTM_DEPS.get(phase, [])
        parallel = [p for p in _PARALLEL_WITH.get(phase, []) if p in ordered_phases]
        chain.append({
            "step": len(chain) + 1,
            "phase": phase,
            "skill": phase,
            "inputs_from": deps,
            "outputs": outputs_map.get(phase, []),
            "parallel_with": parallel,
            "gate": gate_map.get(phase),
            "channels": _CHANNEL_HINTS.get(phase, []),
        })
    return chain


def plan_gtm(objective: str, expand_deps: bool = True) -> dict:
    """
    Produce a full GTM workflow plan for the given objective.

    Returns a dict with: plan_id, objective, complexity, detected_phases,
    skill_chain, channel_recommendations, next_action.
    """
    detected = classify_gtm_intent(objective)

    if not detected:
        today = date.today().strftime("%Y%m%d")
        return {
            "plan_id": f"GTM-{today}-UNKNOWN",
            "objective": objective,
            "complexity": "unknown",
            "detected_phases": [],
            "skill_chain": [],
            "channel_recommendations": [],
            "next_action": (
                "Intent could not be classified. Please clarify: are you planning a product "
                "launch, building marketing infrastructure, optimizing for AI search, or "
                "improving revenue/retention?"
            ),
        }

    requested_phases = [d["phase"] for d in detected]
    ordered_phases = _resolve_dependencies(requested_phases) if expand_deps else [
        p for p in GTM_PHASES if p in requested_phases
    ]
    complexity = _compute_complexity(ordered_phases)
    skill_chain = _build_skill_chain(ordered_phases)

    # Aggregate channel recommendations
    channels: set[str] = set()
    for phase in ordered_phases:
        channels.update(_CHANNEL_HINTS.get(phase, []))

    today = date.today().strftime("%Y%m%d")
    plan_id = f"GTM-{today}-001"

    first_step = skill_chain[0] if skill_chain else {}
    next_action = (
        f"Load {first_step.get('skill', 'launch-planning')} skill and begin "
        f"{first_step.get('outputs', ['planning'])[0] if first_step.get('outputs') else 'planning'}."
    )

    return {
        "plan_id": plan_id,
        "objective": objective,
        "complexity": complexity,
        "detected_phases": detected,
        "ordered_phases": ordered_phases,
        "skill_chain": skill_chain,
        "channel_recommendations": sorted(channels),
        "next_action": next_action,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify a GTM objective and produce a workflow plan.")
    parser.add_argument("objective", nargs="?", help="GTM objective string")
    parser.add_argument("--stdin", action="store_true", help="Read objective from stdin")
    parser.add_argument("--no-expand", action="store_true", help="Do not expand dependencies")
    args = parser.parse_args()

    if args.stdin:
        objective = sys.stdin.read().strip()
    elif args.objective:
        objective = args.objective
    else:
        parser.print_help()
        sys.exit(1)

    result = plan_gtm(objective, expand_deps=not args.no_expand)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()