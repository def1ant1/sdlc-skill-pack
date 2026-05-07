#!/usr/bin/env python3
"""
route_business_task.py — Route a business task to the appropriate domain skill.

Classifies an incoming business task description and outputs the domain skill,
urgency, required approval level, and recommended workflow.

Usage:
    python scripts/business/route_business_task.py --task "Process invoice from Acme Corp for $5,200"
    echo "Schedule Q3 reforecast review" | python scripts/business/route_business_task.py --stdin

Output: JSON routing decision.
"""

import json
import re
import sys


# Routing rules: list of (pattern, domain, skill, urgency, approval_level)
ROUTING_RULES = [
    # Finance — accounting
    (r"invoice|expense|receipt|reconcil|payment|accounts payable|accounts receivable",
     "finance", "accounting-automation", "routine", "level-1-or-auto"),
    # Finance — budget
    (r"budget|reforecast|forecast|variance|spend|headcount plan|annual plan",
     "finance", "budget-planning", "routine", "level-2"),
    # Finance — revenue
    (r"revenue|ARR|MRR|churn|subscription|pricing|contract value",
     "finance", "revenue-operations", "routine", "level-2"),
    # Legal — contracts
    (r"contract|agreement|NDA|terms|legal|clause|governing law|indemnif",
     "legal", "legal-ops", "urgent", "level-2"),
    # Legal — policy
    (r"policy|regulation|compliance|GDPR|EU AI Act|regulatory",
     "legal", "legal-ops", "routine", "level-2"),
    # HR — hiring
    (r"hire|requisition|job description|JD|headcount|recruit|candidate",
     "hr", "workforce-management", "routine", "level-3"),
    # HR — employee
    (r"onboard|offboard|performance|review|promotion|termination|compensation|salary",
     "hr", "workforce-management", "urgent", "level-3"),
    # Procurement — vendor
    (r"vendor|supplier|RFP|purchase order|PO|procurement|quote|proposal",
     "procurement", "vendor-procurement", "routine", "level-2"),
    # Meetings
    (r"meeting|transcript|action item|minutes|agenda|standup|retrospective",
     "meetings", "meeting-intelligence", "routine", "level-0"),
    # Customer
    (r"customer|account|renewal|health score|churn risk|NPS|onboard",
     "customer", "customer-success", "urgent", "level-1"),
    # GTM
    (r"marketing|campaign|content|lead|pipeline|GTM|sales|SEO",
     "gtm", "gtm-orchestration", "routine", "level-1"),
    # Strategic planning / OKR
    (r"OKR|objective|key result|strategic|roadmap|planning|strategy",
     "strategy", "strategic-planning", "routine", "level-2"),
    # Executive reporting
    (r"board report|investor update|weekly review|executive summary|dashboard",
     "reporting", "executive-reporting", "routine", "level-2"),
    # Decision
    (r"decision|decide|options|trade-off|evaluation|criteria",
     "intelligence", "decision-intelligence", "routine", "level-1"),
]

URGENCY_OVERRIDE_PATTERNS = [
    (r"urgent|ASAP|immediately|critical|emergency|today|now", "critical"),
    (r"by (tomorrow|end of day|EOD|COB)", "urgent"),
    (r"this week|soon|upcoming", "urgent"),
]


def classify_task(task_text: str) -> dict:
    """Classify a business task and produce a routing decision."""
    task_lower = task_text.lower()

    # Find matching routing rule
    matched = None
    for pattern, domain, skill, urgency, approval in ROUTING_RULES:
        if re.search(pattern, task_lower, re.IGNORECASE):
            matched = {
                "domain": domain,
                "skill": skill,
                "urgency": urgency,
                "approval_level": approval,
                "pattern_matched": pattern,
            }
            break

    if not matched:
        matched = {
            "domain": "unknown",
            "skill": "business-orchestration",
            "urgency": "routine",
            "approval_level": "level-1",
            "pattern_matched": None,
        }

    # Check urgency overrides
    for pattern, override_urgency in URGENCY_OVERRIDE_PATTERNS:
        if re.search(pattern, task_text, re.IGNORECASE):
            matched["urgency"] = override_urgency
            break

    # Build workflow recommendation
    workflow = build_workflow(matched["domain"], matched["skill"], matched["urgency"])

    return {
        "task": task_text,
        "routing": matched,
        "workflow": workflow,
        "confidence": "high" if matched.get("pattern_matched") else "low",
    }


def build_workflow(domain: str, skill: str, urgency: str) -> dict:
    """Build a recommended workflow for the routed task."""
    steps = [
        {"step": 1, "action": "Intake and classify", "skill": "business-orchestration"},
        {"step": 2, "action": "Execute domain task", "skill": skill},
    ]

    if urgency in ("urgent", "critical"):
        steps.insert(0, {"step": 0, "action": "Escalate notification", "skill": "hitl-dashboard"})

    steps.append({"step": len(steps) + 1, "action": "Audit log", "skill": "telemetry"})

    return {
        "type": "business-task",
        "domain": domain,
        "urgency": urgency,
        "steps": steps,
        "estimated_duration": {
            "routine": "< 1 hour (automated)",
            "urgent": "< 30 minutes (prioritized)",
            "critical": "immediate (paged)",
        }.get(urgency, "unknown"),
    }


def main() -> int:
    args = sys.argv[1:]
    task_text = None
    read_stdin = False

    i = 0
    while i < len(args):
        if args[i] == "--task" and i + 1 < len(args):
            task_text = args[i + 1]
            i += 2
        elif args[i] == "--stdin":
            read_stdin = True
            i += 1
        else:
            i += 1

    if read_stdin or not task_text:
        task_text = sys.stdin.read().strip()

    if not task_text:
        print("ERROR: No task text provided. Use --task '...' or pipe via --stdin", file=sys.stderr)
        return 1

    result = classify_task(task_text)
    print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())