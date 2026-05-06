#!/usr/bin/env python3
"""Generate a simple SDLC workflow plan from a requested outcome."""
import argparse
import json

KEYWORDS = {
    "requirements-engineering": ["requirement", "prd", "scope", "acceptance"],
    "system-architecture": ["architecture", "design", "api", "database", "system"],
    "ai-engineering": ["ai", "agent", "rag", "model", "prompt"],
    "devsecops": ["security", "secure", "ci", "cd", "deploy", "secret"],
    "qa-automation": ["test", "qa", "coverage", "validation"],
    "release-management": ["release", "version", "changelog", "rollout"],
}

def plan(text: str) -> dict:
    lowered = text.lower()
    skills = [skill for skill, words in KEYWORDS.items() if any(w in lowered for w in words)]
    if not skills:
        skills = ["requirements-engineering", "system-architecture"]
    return {
        "objective": text,
        "required_skills": skills,
        "quality_gates": ["requirements_traceability", "security_review", "test_strategy"],
        "next_action": f"Start with {skills[0]}",
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("objective")
    args = parser.parse_args()
    print(json.dumps(plan(args.objective), indent=2))
