"""
Apotheon Chat UI — primary operator interface.

Layout:
  Sidebar  | Chat (center) | Artifact Panel (collapsible right)

Chat drives all interaction: planning, HITL approvals, workflow monitoring.
The right panel renders artifacts: plan details, live progress, HITL approval
forms, reports, and past conversation/workflow history.

Flow:
  idle → conversational_response → draft_artifact (optional) → reviewing (optional)
  → executing (optional) → hitl_pending (optional) → done
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from workspace_state import (
    load_workspace_state,
    register_conversation,
    resume_session_from_workspace,
    save_workspace_state,
    snapshot_turn_state,
    append_audit_event,
)
from workspace_views import render_workspace_actions
from visible_cognition_panel import render_visible_cognition_panel

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

OLLAMA_URL    = os.environ.get("OLLAMA_URL",          "http://ollama:11434")
OLLAMA_MODEL  = os.environ.get("OLLAMA_MODEL",        "qwen3:4b")
API_URL_ENV   = os.environ.get("APOTHEON_API_URL",    "http://runtime:8000")
JWT_ENV       = os.environ.get("APOTHEON_JWT_TOKEN",  "")

ROOT          = Path(__file__).resolve().parents[2]
REPORTS_DIR   = ROOT / "reports"
CONV_DIR      = REPORTS_DIR / "conversations"
WORKSPACE_STATE_FILE = REPORTS_DIR / "workspace" / "workspace-state.json"
CONVERSATION_INTENT_SCHEMA_PATH = ROOT / "schemas" / "conversation-intent.schema.json"
INTENT_ROUTER_SCRIPT = ROOT / "scripts" / "orchestration" / "route_conversation_intent.py"

# ─────────────────────────────────────────────────────────────────────────────
# Skill catalog
# ─────────────────────────────────────────────────────────────────────────────

ALL_SKILLS: dict[str, dict] = {
    # ── Business / Strategy ──────────────────────────────────────────────────
    "business-orchestration":       {"domain": "business",       "description": "Coordinate cross-functional business workflows and decisions"},
    "requirements-engineering":     {"domain": "business",       "description": "Capture, validate, and prioritize business and technical requirements"},
    "governance":                   {"domain": "business",       "description": "Policy enforcement, approval routing, and decision governance"},
    "audit-trail":                  {"domain": "business",       "description": "Immutable record of all workflow events and human approvals"},
    "executive-reporting":          {"domain": "business",       "description": "Generate executive-level KPI dashboards and board reports"},
    "risk-assessment":              {"domain": "business",       "description": "Identify, quantify, and build mitigation plans for operational and strategic risks"},
    "business-continuity-planning": {"domain": "business",       "description": "Design and test continuity plans for critical operations"},
    "business-process-optimization":{"domain": "business",       "description": "Identify and eliminate inefficiencies in business processes"},
    "execution-risk-analysis":      {"domain": "business",       "description": "Assess execution risk before committing to a plan or contract"},
    "system-architecture":          {"domain": "business",       "description": "Design system architecture, integration patterns, and technical standards"},
    "backend-engineering":          {"domain": "business",       "description": "Implement and review backend services, APIs, and data models"},
    "qa-automation":                {"domain": "business",       "description": "Design and execute automated test suites and quality gates"},
    "release-management":           {"domain": "business",       "description": "Coordinate software releases, change management, and rollback plans"},
    "hr-operations-phase-pack":     {"domain": "business",       "description": "Handle hiring, onboarding, offboarding, and HR policy workflows"},
    "hr-policy-guidance-support":   {"domain": "business",       "description": "Provide HR policy guidance and compliance for employment decisions"},
    # ── Finance ──────────────────────────────────────────────────────────────
    "billing-runtime":              {"domain": "finance",        "description": "Manage invoicing, payment processing, and billing cycles"},
    "business-policy-engine":       {"domain": "finance",        "description": "Enforce spending limits, approval thresholds, and financial policies"},
    "budget-planning":              {"domain": "finance",        "description": "Create and baseline operational and project budgets"},
    "budget-monitoring":            {"domain": "finance",        "description": "Track actuals vs. budget and surface variances in real time"},
    "budget-variance-analysis":     {"domain": "finance",        "description": "Analyse budget variances and recommend corrective actions"},
    "cash-flow-forecasting":        {"domain": "finance",        "description": "Model cash inflows and outflows and flag liquidity risks"},
    "cash-management":              {"domain": "finance",        "description": "Optimise working capital, payment timing, and treasury positions"},
    "accounts-payable-automation":  {"domain": "finance",        "description": "Process vendor invoices, 3-way matching, and payment runs"},
    "accounts-receivable-automation":{"domain": "finance",       "description": "Manage customer billing, collections, and AR aging workflows"},
    "accounting-automation":        {"domain": "finance",        "description": "Automate journal entries, reconciliations, and month-end close"},
    "accounting-operations":        {"domain": "finance",        "description": "Manage chart of accounts, cost centres, and GL operations"},
    "expense-policy-compliance":    {"domain": "finance",        "description": "Enforce employee expense policies and flag non-compliant claims"},
    "financial-reporting":          {"domain": "finance",        "description": "Produce P&L statements, balance sheets, and management accounts"},
    "audit-log-review":             {"domain": "finance",        "description": "Review financial audit logs for anomalies and control gaps"},
    "audit-trail-analysis":         {"domain": "finance",        "description": "Analyse transaction audit trails for compliance and fraud signals"},
    # ── Legal & Compliance ────────────────────────────────────────────────────
    "compliance-runtime":           {"domain": "legal",          "description": "Continuous compliance monitoring against regulatory frameworks"},
    "compliance-automation":        {"domain": "legal",          "description": "Automate recurring compliance checks and evidence collection"},
    "compliance-governance":        {"domain": "legal",          "description": "Govern compliance programmes, controls, and remediation tracks"},
    "compliance-posture-reporting": {"domain": "legal",          "description": "Report on compliance posture across frameworks (SOC 2, GDPR, HIPAA)"},
    "data-contract-management":     {"domain": "legal",          "description": "Draft, version, and enforce data-sharing and processing agreements"},
    "legal-intake-triage-support":  {"domain": "legal",          "description": "Triage and route incoming legal requests to the right resource"},
    "legal-obligation-management":  {"domain": "legal",          "description": "Track and manage legal obligations from contracts and regulations"},
    "legal-ops":                    {"domain": "legal",          "description": "Streamline legal operations: matter management, spend, and workflows"},
    "legal-hold-management":        {"domain": "legal",          "description": "Identify, notify, and manage legal holds for litigation or audit"},
    "vendor-obligation-tracking":   {"domain": "legal",          "description": "Monitor vendor contractual obligations, milestones, and renewals"},
    "vendor-negotiation-support":   {"domain": "legal",          "description": "Prepare negotiation briefs, redlines, and contract terms analysis"},
    "listing-compliance-validation":{"domain": "legal",          "description": "Validate product listings for regulatory and marketplace compliance"},
    "iam-policy-analysis":          {"domain": "legal",          "description": "Analyse identity and access management policies for compliance gaps"},
    "policy-engine":                {"domain": "legal",          "description": "Author, version, and enforce organisational policies"},
    # ── Customer ──────────────────────────────────────────────────────────────
    "meeting-intelligence":         {"domain": "customer",       "description": "Capture, summarise, and extract action items from meetings and calls"},
    "churn-risk-detection":         {"domain": "customer",       "description": "Identify at-risk customers and recommend retention interventions"},
    "customer-success":             {"domain": "customer",       "description": "Run customer success playbooks: health checks, QBRs, expansions"},
    "customer-health-scoring":      {"domain": "customer",       "description": "Compute and monitor customer health scores and leading indicators"},
    "customer-journey-mapping":     {"domain": "customer",       "description": "Map customer journeys and identify friction and drop-off points"},
    "crm-integration":              {"domain": "customer",       "description": "Sync and enrich CRM data across platforms (Salesforce, HubSpot)"},
    "account-expansion-intelligence":{"domain": "customer",      "description": "Identify upsell and cross-sell opportunities within existing accounts"},
    # ── Go-to-Market ──────────────────────────────────────────────────────────
    "campaign-optimization":        {"domain": "gtm",            "description": "Optimise marketing campaign targeting, spend, and creative performance"},
    "content-marketing":            {"domain": "gtm",            "description": "Plan, produce, and distribute content across marketing channels"},
    "brand-sentiment-analysis":     {"domain": "gtm",            "description": "Monitor and analyse brand sentiment across channels and media"},
    "market-data-ingestion":        {"domain": "gtm",            "description": "Ingest and structure market data for competitive and pricing intelligence"},
    "gtm-orchestration":            {"domain": "gtm",            "description": "Orchestrate end-to-end go-to-market launch sequences"},
    # ── Inventory & Supply Chain ──────────────────────────────────────────────
    "master-data-management":       {"domain": "inventory",      "description": "Maintain canonical product, supplier, customer, and location records"},
    "inventory-forecasting":        {"domain": "inventory",      "description": "Predict demand and optimise inventory levels to reduce stockouts and overstock"},
    "procurement-kpi-optimization": {"domain": "inventory",      "description": "Track and improve procurement KPIs: lead time, cost, quality, reliability"},
    "vendor-network-analysis":      {"domain": "inventory",      "description": "Analyse vendor network for concentration risk, performance, and alternatives"},
    "logistics-management":         {"domain": "inventory",      "description": "Coordinate inbound/outbound logistics, freight, and 3PL partners"},
    "carrier-selection-support":    {"domain": "inventory",      "description": "Evaluate and select carriers based on cost, SLA, and reliability data"},
    "ecommerce-fulfillment":        {"domain": "inventory",      "description": "Orchestrate order fulfilment workflows across warehouses and channels"},
    "multi-channel-inventory-sync": {"domain": "inventory",      "description": "Synchronise inventory across sales channels and fulfilment nodes"},
    "bulk-purchase-negotiation":    {"domain": "inventory",      "description": "Prepare data and strategy for bulk purchase price negotiations"},
    # ── Data & Security ───────────────────────────────────────────────────────
    "data-security-management":     {"domain": "data-security",  "description": "Manage data security controls, policies, and incident response"},
    "access-control-review":        {"domain": "data-security",  "description": "Audit and enforce least-privilege access controls across systems"},
    "devsecops":                    {"domain": "data-security",  "description": "Integrate security into CI/CD pipelines and deployment workflows"},
    "sandbox-execution":            {"domain": "data-security",  "description": "Run sensitive or untrusted workloads in isolated sandbox environments"},
}

DOMAIN_LABELS: dict[str, str] = {
    "business":      "Business & Strategy",
    "finance":       "Finance & Accounting",
    "customer":      "Customer Success",
    "gtm":           "Go-to-Market",
    "inventory":     "Inventory & Supply Chain",
    "legal":         "Legal & Compliance",
    "data-security": "Data & Security",
}

DOMAIN_DESCRIPTIONS: dict[str, str] = {
    "business":      "Strategy, planning, OKRs, org design, risk, engineering, HR, and cross-functional orchestration",
    "finance":       "Budgeting, P&L, cash flow, AP/AR, accounting automation, financial reporting, and expense governance",
    "customer":      "CRM, churn prevention, customer health, journey mapping, success playbooks, and account expansion",
    "gtm":           "Product launches, marketing campaigns, brand, content, market intelligence, and sales GTM execution",
    "inventory":     "Stock management, demand forecasting, procurement, vendor management, logistics, and fulfilment",
    "legal":         "Contract review, regulatory compliance, legal ops, obligation tracking, policy, and GDPR/HIPAA/SOC2",
    "data-security": "Security controls, access management, DevSecOps, sandbox execution, and data protection",
}

STATUS_COLORS = {
    "done": "green", "completed": "green",
    "queued": "blue", "running": "orange",
    "failed": "red", "dry_run_saved": "gray",
    "cancelled": "gray", "paused_for_hitl": "orange",
    "dry_run": "gray", "pending": "orange",
    "approved": "green", "rejected": "red",
}

COMPLEXITY_LABELS = {
    "simple":     "Simple (1-3 skills)",
    "moderate":   "Moderate (4-7 skills)",
    "complex":    "Complex (8-15 skills)",
    "enterprise": "Enterprise (15+ skills, multi-phase)",
}

STEP_ICONS = {
    "pending": "⏳", "running": "⚙️", "completed": "✅",
    "failed": "❌", "error": "❌", "dry_run": "🔵",
    "pending_hitl": "🔒", "hitl_required": "🔒",
}

MODE_OPTIONS = ["Chat", "Plan", "Workflow Builder", "Operator", "Research", "Governance"]
MODE_TO_INTENT = {
    "Plan": "draft_plan",
    "Workflow Builder": "create_workflow",
    "Operator": "run_workflow",
    "Research": "ask_clarifying_question",
    "Governance": "request_approval",
}

# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _http(url: str, method: str = "GET", data: Any = None,
          token: str = "", timeout: int = 10) -> tuple[int, Any]:
    body = json.dumps(data).encode() if data is not None else None
    headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read())
        except Exception:
            detail = {"error": exc.reason}
        return exc.code, detail
    except Exception as exc:
        return 0, {"error": str(exc)}

# ─────────────────────────────────────────────────────────────────────────────
# Ollama helpers
# ─────────────────────────────────────────────────────────────────────────────

def _strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _extract_json(text: str) -> dict | None:
    text = _strip_think(text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def ollama_status(url: str) -> tuple[bool, bool]:
    code, resp = _http(f"{url}/api/tags", timeout=3)
    if code != 200:
        return False, False
    models = [m.get("name", "") for m in resp.get("models", [])]
    base = OLLAMA_MODEL.split(":")[0]
    ready = any(OLLAMA_MODEL in m or m.startswith(base) for m in models)
    return True, ready


def _ollama_call(url: str, system: str, messages: list[dict],
                 as_json: bool = False, max_tokens: int = 600,
                 temperature: float = 0.4) -> str:
    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "system": system,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    if as_json:
        payload["format"] = "json"
    code, resp = _http(f"{url}/api/chat", method="POST", data=payload, timeout=120)
    if code == 200:
        return _strip_think(resp.get("message", {}).get("content", "")).strip()
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# Runtime API helpers
# ─────────────────────────────────────────────────────────────────────────────

def backend_up(api_url: str) -> bool:
    code, _ = _http(f"{api_url}/health", timeout=3)
    return code == 200


def submit_to_backend(plan: dict, dry_run: bool, api_url: str, token: str) -> dict:
    code, resp = _http(
        f"{api_url}/v1/workflows", method="POST",
        data={"plan": plan, "mode": "local", "dry_run": dry_run},
        token=token, timeout=15,
    )
    return resp if code in (200, 202) else {"error": f"HTTP {code}: {resp}"}


def get_workflow(api_url: str, token: str, run_id: str) -> dict | None:
    code, resp = _http(f"{api_url}/v1/workflows/{run_id}", token=token, timeout=5)
    return resp if code == 200 else None


def list_workflows(api_url: str, token: str, limit: int = 15) -> list[dict]:
    code, resp = _http(f"{api_url}/v1/workflows?limit={limit}", token=token, timeout=5)
    return resp if (code == 200 and isinstance(resp, list)) else []


def get_approvals(api_url: str, token: str) -> list[dict]:
    code, resp = _http(f"{api_url}/v1/approvals", token=token, timeout=5)
    return resp if (code == 200 and isinstance(resp, list)) else []


def decide_approval(api_url: str, token: str, approval_id: str,
                    decision: str, reason: str = "") -> dict:
    code, resp = _http(
        f"{api_url}/v1/approvals/{approval_id}/decide", method="POST",
        data={"decision": decision, "reason": reason},
        token=token, timeout=10,
    )
    return resp if code == 200 else {"error": f"HTTP {code}: {resp}"}


def load_saved_conversations() -> list[dict]:
    """Load conversation summaries from reports/conversations/."""
    if not CONV_DIR.exists():
        return []
    items = []
    for f in sorted(CONV_DIR.glob("*.json"), reverse=True)[:20]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            items.append({
                "file": f.name,
                "saved_at": data.get("saved_at", ""),
                "plan_id": data.get("plan_id", ""),
                "title": (data.get("plan") or {}).get("workflow_title", f.stem),
                "message_count": len(data.get("messages", [])),
                "data": data,
            })
        except Exception:
            pass
    return items


def load_plan_files() -> list[dict]:
    """Load plan JSON files from reports/."""
    if not REPORTS_DIR.exists():
        return []
    items = []
    for f in sorted(REPORTS_DIR.glob("plan-*.json"), reverse=True)[:10]:
        try:
            plan = json.loads(f.read_text(encoding="utf-8"))
            items.append({
                "file": f.name,
                "id": plan.get("id", f.stem),
                "title": plan.get("workflow_title", f.stem),
                "complexity": plan.get("complexity", ""),
                "domains": plan.get("domains", []),
                "plan": plan,
            })
        except Exception:
            pass
    return items

# ─────────────────────────────────────────────────────────────────────────────
# Skill catalog helpers
# ─────────────────────────────────────────────────────────────────────────────

def _catalog_text() -> str:
    lines = []
    for name, info in ALL_SKILLS.items():
        lines.append(f"  {name} [{info['domain']}]: {info['description']}")
    return "\n".join(lines)


def _domain_context() -> str:
    return "\n".join(
        f"  {k}: {DOMAIN_DESCRIPTIONS[k]}" for k in DOMAIN_LABELS
    )

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Analyze request
# ─────────────────────────────────────────────────────────────────────────────

ANALYSIS_SYSTEM = """You are Apotheon's multi-domain workflow analyzer.

Your job: deeply understand a business request and determine EVERYTHING needed to fulfill it — \
across ALL relevant domains, not just the most obvious one.

Available domains:
{domains}

Available skills (name [domain]: description):
{skills}

Analyze the request and return a JSON object with this exact structure:
{{
  "workflow_title": "concise descriptive title for this workflow",
  "understanding": "1-2 sentences explaining what the user actually needs and why it is complex",
  "domains": ["domain1", "domain2"],
  "complexity": "simple|moderate|complex|enterprise",
  "skills_preview": ["skill1", "skill2", "skill3"],
  "assumptions": [
    "Assumption 1 used to move forward safely"
  ],
  "open_questions": [
    "Known uncertainty that may affect optimization"
  ],
  "questions": []
}}

Rules for questions:
- Ask questions only when missing information would materially change the next safe action.
- Prefer drafting with explicit assumptions when you can proceed safely.
- Ask at most ONE clarifying question at a time unless the user explicitly requests full intake.
- Questions must surface information needed to select the right skills and sequencing.
- Each question should uncover a different dimension: scope, constraints, stakeholders, \
timeline, data/systems, risk tolerance, approvals, etc.
- Questions must be specific to this request — not generic boilerplate.
- Do NOT ask about things that are obvious from the request.

Rules for skills_preview:
- Include ALL skills likely needed, across ALL domains.
- Think holistically: a vendor contract needs legal review, finance/AP setup, \
procurement/logistics setup, compliance checks, AND audit trail.
- This list will be refined after the user answers the questions.
"""


def analyze_request(ollama_url: str, request: str) -> dict | None:
    system = ANALYSIS_SYSTEM.format(
        domains=_domain_context(),
        skills=_catalog_text(),
    )
    raw = _ollama_call(
        ollama_url, system,
        [{"role": "user", "content": request}],
        as_json=True, max_tokens=1000, temperature=0.2,
    )
    result = _extract_json(raw)
    if result:
        result.setdefault("assumptions", [])
        result.setdefault("open_questions", [])
        result.setdefault("questions", [])
        if not isinstance(result.get("questions"), list):
            result["questions"] = []
        if not isinstance(result.get("assumptions"), list):
            result["assumptions"] = []
        if not isinstance(result.get("open_questions"), list):
            result["open_questions"] = []
        return result
    return None


def _fallback_analysis(request: str, routed_intent: str | None = None) -> dict:
    normalized_intent = (routed_intent or "").strip()
    workflow_intents = {"create_workflow", "run_workflow", "draft_plan", "create_task", "create_schedule"}
    asks_for_plan = normalized_intent in workflow_intents

    concise_understanding = (
        "User wants a structured business workflow response grounded in cross-functional execution."
        if asks_for_plan
        else "User likely needs a direct conversational answer rather than workflow intake."
    )
    initial_artifact = (
        "Drafted an initial multi-domain execution outline with safe defaults and governance checkpoints."
        if asks_for_plan
        else "Drafted a direct answer path with no workflow planning steps."
    )
    assumptions = [
        "The request can proceed with standard organizational controls unless the user states hard constraints."
    ]
    questions = (
        ["Do you have one non-negotiable constraint (budget, compliance, or timeline) that should drive sequencing?"]
        if asks_for_plan
        else []
    )
    open_questions = questions.copy()

    return {
        "workflow_title": "Workflow Plan" if asks_for_plan else "Direct Response",
        "understanding": concise_understanding,
        "initial_artifact": initial_artifact,
        "domains": ["business", "legal", "finance"] if asks_for_plan else ["business"],
        "complexity": "moderate" if asks_for_plan else "simple",
        "skills_preview": (
            ["business-orchestration", "governance", "compliance-runtime", "accounts-payable-automation", "audit-trail"]
            if asks_for_plan
            else []
        ),
        "assumptions": assumptions,
        "open_questions": open_questions,
        "questions": questions,
    }

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Synthesize plan
# ─────────────────────────────────────────────────────────────────────────────

SYNTHESIS_SYSTEM = """You are Apotheon's multi-domain workflow architect.

You have collected full context from the user. Now build a comprehensive, \
multi-domain workflow execution plan.

Available skills (name [domain]: description):
{skills}

Initial analysis:
{analysis}

User's answers to clarifying questions:
{answers}

Return a JSON object with this exact structure:
{{
  "workflow_title": "final concise title",
  "domains": ["domain1", "domain2"],
  "complexity": "simple|moderate|complex|enterprise",
  "rationale": "3-4 sentences explaining the plan: what it accomplishes, \
why these specific skills were chosen, how they relate to the user's context.",
  "phases": [
    {{
      "name": "Phase name",
      "description": "What this phase accomplishes",
      "skills": ["skill1", "skill2"],
      "depends_on_phases": []
    }}
  ],
  "skill_chain": ["skill1", "skill2", "skill3"],
  "hitl_gates": [
    {{"after_phase": "Phase name", "reason": "Why human approval is needed here"}}
  ],
  "risks": ["Risk 1", "Risk 2"]
}}

Rules:
- phases: logically group skills into sequential phases. Dependencies come first.
- skill_chain: flat ordered list of all skills across all phases, in execution order.
- Only use skills from the catalog.
- hitl_gates: identify where human-in-the-loop approval is REQUIRED (legal sign-off, \
large spend, irreversible actions, compliance certification).
- risks: 2-4 key execution risks specific to this context.
- Be specific to the user's actual answers — reference their context.
"""


def synthesize_plan(ollama_url: str, request: str, analysis: dict, answers: dict) -> dict | None:
    system = SYNTHESIS_SYSTEM.format(
        skills=_catalog_text(),
        analysis=json.dumps(analysis, indent=2),
        answers=json.dumps(answers, indent=2),
    )
    messages = [
        {"role": "user", "content": request},
        {"role": "assistant", "content": f"I've analyzed your request. Here is what I understood: {analysis.get('understanding', '')}"},
        {"role": "user", "content": f"Here are my answers to your questions: {json.dumps(answers)}"},
    ]
    raw = _ollama_call(
        ollama_url, system, messages,
        as_json=True, max_tokens=1500, temperature=0.2,
    )
    result = _extract_json(raw)
    if result and isinstance(result.get("skill_chain"), list) and len(result["skill_chain"]) > 0:
        valid = {s for s in result["skill_chain"] if s in ALL_SKILLS}
        if valid:
            result["skill_chain"] = [s for s in result["skill_chain"] if s in ALL_SKILLS]
            return result
    return None


def _fallback_plan(request: str, analysis: dict, answers: dict) -> dict:
    skills = analysis.get("skills_preview", ["business-orchestration", "governance", "audit-trail"])
    skills = [s for s in skills if s in ALL_SKILLS] or ["business-orchestration", "governance", "audit-trail"]
    domains = analysis.get("domains", ["business"])
    phases = [{"name": "Execution", "description": "Execute workflow", "skills": skills, "depends_on_phases": []}]
    return {
        "workflow_title":  analysis.get("workflow_title", "Workflow Plan"),
        "domains":         domains,
        "complexity":      analysis.get("complexity", "moderate"),
        "rationale":       f"Plan generated from your request: {request}",
        "phases":          phases,
        "skill_chain":     skills,
        "hitl_gates":      [{"after_phase": "Execution", "reason": "Human approval required before finalising"}],
        "risks":           ["Scope may expand during execution", "External dependencies may cause delays"],
    }

# ─────────────────────────────────────────────────────────────────────────────
# Build & save plan
# ─────────────────────────────────────────────────────────────────────────────

def build_plan(request: str, synthesis: dict, answers: dict) -> dict:
    steps = []
    for i, skill in enumerate(synthesis["skill_chain"], 1):
        info = ALL_SKILLS.get(skill, {"domain": "business", "description": ""})
        steps.append({
            "id":          f"step-{i}",
            "order":       i,
            "title":       f"Run {skill}",
            "skill":       skill,
            "domain":      info["domain"],
            "description": info["description"],
            "depends_on":  [steps[-1]["id"]] if steps else [],
            "inputs":      answers,
            "governance_policy_refs": ["references/business-policy-standard.md"],
            "outputs":     [f"reports/{skill}-output.json"],
        })
    return {
        "id":             f"plan-{int(time.time())}",
        "objective":      request,
        "workflow_title": synthesis.get("workflow_title", "Workflow Plan"),
        "domains":        synthesis.get("domains", ["business"]),
        "complexity":     synthesis.get("complexity", "moderate"),
        "skill_chain":    synthesis["skill_chain"],
        "phases":         synthesis.get("phases", []),
        "hitl_gates":     synthesis.get("hitl_gates", []),
        "risks":          synthesis.get("risks", []),
        "rationale":      synthesis.get("rationale", ""),
        "context":        answers,
        "assistant_working_state": st.session_state.get("assistant_working_state"),
        "steps":          steps,
        "governance_gates": [
            {"id": "gate-policy", "policy_ref": "references/business-policy-standard.md", "enforcement": "blocking"},
        ],
        "dry_run_safety": {
            "enabled": True,
            "no_external_writes": True,
            "require_human_approval_for_mutations": True,
        },
        "planner_metadata": {
            "planner":    "multi-domain-planner",
            "version":    "2.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def save_plan(plan: dict) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    (REPORTS_DIR / f"{plan['id']}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")


def save_conversation(messages: list, plan: dict | None, run_result: dict | None) -> None:
    CONV_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    name = (plan or {}).get("id", f"conv-{ts}")
    record = {
        "saved_at":    datetime.now(timezone.utc).isoformat(),
        "plan_id":     (plan or {}).get("id"),
        "run_result":  run_result,
        "messages":    messages,
        "plan":        plan,
    }
    (CONV_DIR / f"{name}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    register_conversation(
        st.session_state.workspace_state,
        session_id=name,
        title=(plan or {}).get("workflow_title", name),
        plan_id=(plan or {}).get("id"),
        run_id=(run_result or {}).get("run_id") if isinstance(run_result, dict) else None,
        turn_state=snapshot_turn_state(st.session_state),
    )
    save_workspace_state(WORKSPACE_STATE_FILE, st.session_state.workspace_state)


def _persist_turn_state() -> None:
    s = st.session_state
    if s.workspace_state is None:
        return
    session_id = _current_session_id()
    register_conversation(
        s.workspace_state,
        session_id=session_id,
        title=(s.plan or {}).get("workflow_title", session_id),
        plan_id=(s.plan or {}).get("id"),
        run_id=(s.run_result or {}).get("run_id") if isinstance(s.run_result, dict) else None,
        turn_state=snapshot_turn_state(s),
    )
    save_workspace_state(WORKSPACE_STATE_FILE, s.workspace_state)

# ─────────────────────────────────────────────────────────────────────────────
# Conversational response generators
# ─────────────────────────────────────────────────────────────────────────────

CONVO_SYSTEM = """\
You are Apotheon, an AI business workflow planning assistant. You orchestrate complex, \
multi-domain business workflows. You are talking to a business operator.

Keep replies concise and professional. Use plain language. \
Avoid bullet points unless listing items. 1-3 sentences maximum unless showing a plan.\
"""


def gen_analysis_greeting(ollama_url: str, request: str, analysis: dict) -> str:
    domains_str = ", ".join(DOMAIN_LABELS.get(d, d) for d in analysis.get("domains", []))
    n = len(analysis.get("skills_preview", []))
    system = (
        CONVO_SYSTEM + "\n\n"
        f"You've analysed a request and identified it as a '{analysis.get('workflow_title','')}' workflow "
        f"touching these domains: {domains_str}. It requires about {n} skills. "
        f"Understanding: {analysis.get('understanding', '')}\n\n"
        f"Write 2 sentences: acknowledge what the request covers and why it spans multiple domains. "
        f"Then immediately ask the first clarifying question: {analysis.get('questions', ['What is the primary goal?'])[0]}"
    )
    reply = _ollama_call(ollama_url, system, [{"role": "user", "content": request}],
                         max_tokens=200, temperature=0.5)
    if not reply:
        first_q = analysis.get("questions", ["What is the primary goal?"])[0]
        return (
            f"This is a **{analysis.get('workflow_title', 'multi-domain')}** workflow spanning "
            f"**{domains_str}**. To build the right plan I need a few details.\n\n{first_q}"
        )
    return reply


def gen_next_question(ollama_url: str, analysis: dict, next_q: str,
                      answers: dict, llm_messages: list) -> str:
    system = (
        CONVO_SYSTEM + "\n\n"
        f"You're gathering context for a '{analysis.get('workflow_title', '')}' plan. "
        f"The user has answered {len(answers)} question(s) so far. "
        f"Briefly acknowledge their last answer (1 sentence), then ask the next question."
    )
    reply = _ollama_call(ollama_url, system, llm_messages + [{"role": "user", "content": next_q}],
                         max_tokens=150, temperature=0.5)
    return reply or next_q


def gen_synthesis_intro(ollama_url: str, plan: dict, llm_messages: list) -> str:
    domains_str = ", ".join(DOMAIN_LABELS.get(d, d) for d in plan.get("domains", []))
    n = len(plan.get("skill_chain", []))
    phases = [p["name"] for p in plan.get("phases", [])]
    system = (
        CONVO_SYSTEM + "\n\n"
        f"You've built a complete multi-domain plan titled '{plan.get('workflow_title', '')}'. "
        f"Domains: {domains_str}. Total skills: {n}. Phases: {' → '.join(phases)}. "
        f"HITL gates: {len(plan.get('hitl_gates', []))}. "
        f"Write 2 sentences summarising what this plan accomplishes. "
        f"Then tell the user the plan is open in the panel on the right for review."
    )
    reply = _ollama_call(ollama_url, system, llm_messages, max_tokens=200, temperature=0.5)
    if not reply:
        return (
            f"I've built a **{plan.get('workflow_title', 'multi-domain')}** plan spanning "
            f"**{domains_str}** with {n} skills across {len(phases)} phases. "
            "Review the full plan in the panel on the right and approve when ready."
        )
    return reply


def gen_unknown_response(ollama_url: str, request: str) -> str:
    system = (
        CONVO_SYSTEM + "\n\n"
        "Apotheon couldn't fully analyse the request. "
        "Acknowledge what was understood, ask ONE clarifying question to scope it better. "
        "Suggest which 2-3 of these domains seem most relevant: "
        + ", ".join(DOMAIN_LABELS.values())
    )
    reply = _ollama_call(ollama_url, system, [{"role": "user", "content": request}],
                         max_tokens=200, temperature=0.5)
    return reply or ("I want to make sure I build the right plan. "
                     "Could you tell me more about the primary outcome you're trying to achieve?")


def route_conversation_intent(message: str) -> dict[str, Any]:
    payload = {"message": message}
    default = {"intent": "ask_clarifying_question", "confidence": 0.0, "rationale": "routing_failed"}
    try:
        out = subprocess.check_output(
            ["python3", str(INTENT_ROUTER_SCRIPT), "--state", json.dumps(payload)],
            text=True,
            cwd=str(ROOT),
        )
        routed = json.loads(out)
        validate_conversation_intent(routed)
        return routed
    except Exception:
        return default


def validate_conversation_intent(intent_data: dict[str, Any]) -> None:
    schema = json.loads(CONVERSATION_INTENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    required = schema.get("required", [])
    for field in required:
        if field not in intent_data:
            raise ValueError(f"Missing required conversation intent field: {field}")
    intent_enum = schema["properties"]["intent"]["enum"]
    if intent_data.get("intent") not in intent_enum:
        raise ValueError("Conversation intent is not allowed by schema.")
    confidence = intent_data.get("confidence")
    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
        raise ValueError("Conversation intent confidence must be between 0 and 1.")

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

def _init() -> None:
    defaults: dict[str, Any] = {
        # Conversation state
        "phase":             "idle",   # idle|conversational_response|draft_artifact|questioning|reviewing|executing|hitl_pending|done
        "mode":              "conversational",  # conversational|workflow_builder
        "messages":          [],
        "llm_messages":      [],
        "intent_raw":        "",
        "analysis":          None,
        "dynamic_questions": [],
        "q_index":           0,
        "answers":           {},
        "plan":              None,
        "run_result":        None,
        # Execution tracking
        "poll_run_id":       None,    # run_id being polled
        "workflow_data":     None,    # latest fetched workflow from API
        "hitl_approval":     None,    # pending approval dict
        "last_poll_ts":      0.0,
        # Artifact panel
        "panel_open":        True,
        "panel_tab":         "plan",  # plan|progress|hitl|history
        "panel_artifact":    None,    # generic artifact data for the panel
        "workspace_state":   None,
        "active_workspace_conversation": None,
        "assistant_working_state": None,
        "routed_intent": None,
        "routed_intent_confidence": None,
        "selected_mode": "Chat",
        "explicit_mode_override": False,
        "workflow_builder_paused": False,
        "active_goal": "",
        "workflow_stage": "idle",
        "clarification_status": "not_started",
        "clarification_answer_map": {},
        "last_clarification_id": None,
        "completion_status": "incomplete",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def add_msg(role: str, content: str) -> None:
    st.session_state.messages.append(
        {"role": role, "content": content, "ts": datetime.now(timezone.utc).isoformat()}
    )


def add_llm(role: str, content: str) -> None:
    st.session_state.llm_messages.append({"role": role, "content": content})


def reset() -> None:
    for k in ["phase", "messages", "llm_messages", "intent_raw", "analysis",
              "dynamic_questions", "q_index", "answers", "plan", "run_result",
              "poll_run_id", "workflow_data", "hitl_approval", "last_poll_ts"]:
        st.session_state.pop(k, None)


def open_panel(tab: str, artifact: Any = None) -> None:
    st.session_state.panel_open = True
    st.session_state.panel_tab = tab
    if artifact is not None:
        st.session_state.panel_artifact = artifact


def _normalize_legacy_session_state() -> None:
    """Migration-safe session guards for older phase values."""
    phase = st.session_state.get("phase", "idle")
    mode = st.session_state.get("mode", "conversational")
    if mode not in ("conversational", "workflow_builder"):
        st.session_state.mode = "conversational"
        mode = "conversational"

    if phase == "questioning" and mode != "workflow_builder":
        if st.session_state.get("dynamic_questions"):
            st.session_state.mode = "workflow_builder"
        else:
            st.session_state.phase = "conversational_response"
    elif phase not in ("idle", "conversational_response", "draft_artifact", "questioning",
                       "reviewing", "executing", "hitl_pending", "done"):
        st.session_state.phase = "idle"


def _set_selected_mode(mode_label: str) -> None:
    mode = mode_label if mode_label in MODE_OPTIONS else "Chat"
    prev = st.session_state.get("selected_mode", "Chat")
    st.session_state.selected_mode = mode
    st.session_state.explicit_mode_override = mode != "Chat"
    if prev == "Workflow Builder" and mode != "Workflow Builder":
        if st.session_state.get("phase") == "questioning":
            st.session_state.workflow_builder_paused = True
            st.session_state.phase = "done"
    if mode == "Workflow Builder" and st.session_state.get("workflow_builder_paused"):
        st.session_state.workflow_builder_paused = False
        if st.session_state.get("dynamic_questions") and st.session_state.get("q_index", 0) < len(st.session_state.get("dynamic_questions", [])):
            st.session_state.phase = "questioning"


def _resolve_effective_mode(routed_intent: str | None) -> str:
    if st.session_state.get("explicit_mode_override") and st.session_state.get("selected_mode") in MODE_OPTIONS:
        return st.session_state["selected_mode"]
    workflow_intents = {"create_workflow", "run_workflow", "draft_plan", "create_task", "create_schedule"}
    if routed_intent in workflow_intents:
        return "Workflow Builder"
    return "Chat"


def _run_conversational_mode(user_input: str, ollama_url: str, use_ollama: bool) -> None:
    """Default route for new messages."""
    s = st.session_state
    s.phase = "conversational_response"
    s.mode = "conversational"
    s.intent_raw = user_input
    s.q_index = 0
    s.answers = {}
    s.plan = None
    s.run_result = None
    s.poll_run_id = None
    s.workflow_data = None
    s.assistant_working_state = None
    s.llm_messages = [{"role": "user", "content": user_input}]
    s.active_goal = user_input
    s.workflow_stage = "analysis"
    s.completion_status = "in_progress"

    with st.chat_message("assistant"):
        with st.spinner("Analysing across all domains…"):
            analysis = analyze_request(ollama_url, user_input) if use_ollama else None
            if not analysis:
                analysis = _fallback_analysis(user_input, s.routed_intent)

        s.analysis = analysis
        s.dynamic_questions = analysis.get("questions", [])
        s.assistant_working_state = derive_working_state(s.intent_raw, s.answers, analysis)

        if s.dynamic_questions:
            candidate_q = s.dynamic_questions[0]
            dedupe = _clarification_dedupe_check(candidate_q)
            if dedupe["action"] == "skip":
                s.dynamic_questions = s.dynamic_questions[1:]
                s.clarification_status = "skipped"
                append_audit_event(
                    s.workspace_state,
                    _current_session_id(),
                    "clarification_skipped",
                    {"question": candidate_q, "reason": dedupe["reason"]},
                )
            else:
                s.last_clarification_id = dedupe["id"]
                s.clarification_status = "asked"
                append_audit_event(
                    s.workspace_state,
                    _current_session_id(),
                    "clarification_asked",
                    {"question": candidate_q, "clarification_id": dedupe["id"]},
                )
            s.mode = "workflow_builder"
            s.phase = "questioning"
            s.workflow_stage = "clarification"
            with st.spinner("Thinking…"):
                reply = (
                    gen_analysis_greeting(ollama_url, user_input, analysis)
                    if use_ollama else (
                        f"This is a **{analysis.get('workflow_title','')}** workflow touching "
                        + ", ".join(DOMAIN_LABELS.get(d, d) for d in analysis.get("domains", []))
                        + f".\n\n{s.dynamic_questions[0]}"
                    )
                )
        else:
            synthesis = synthesize_plan(ollama_url, s.intent_raw, s.analysis or {}, s.answers) if use_ollama else None
            if not synthesis:
                synthesis = _fallback_plan(s.intent_raw, s.analysis or {}, s.answers)
            plan = build_plan(s.intent_raw, synthesis, s.answers)
            plan["assistant_working_state"] = s.assistant_working_state
            s.plan = plan
            s.phase = "draft_artifact"
            s.workflow_stage = "planning"
            open_panel("plan")
            with st.spinner("Thinking…"):
                reply = (
                    gen_synthesis_intro(ollama_url, plan, s.llm_messages)
                    if use_ollama else (
                        f"I've drafted a **{plan.get('workflow_title', 'workflow')}** plan with explicit assumptions. "
                        "Review it in the Plan panel."
                    )
                )
        st.markdown(reply)

    add_msg("assistant", reply)
    add_llm("assistant", reply)


def _run_workflow_builder_mode(user_input: str, ollama_url: str, use_ollama: bool) -> None:
    """Structured interview intake and synthesis workflow."""
    s = st.session_state
    questions = s.dynamic_questions
    s.answers[str(s.q_index + 1)] = user_input
    if s.last_clarification_id:
        s.clarification_answer_map[s.last_clarification_id] = {
            "answer": user_input,
            "answered_at": datetime.now(timezone.utc).isoformat(),
            "valid": True,
            "question": (s.dynamic_questions[s.q_index] if s.q_index < len(s.dynamic_questions) else ""),
        }
        s.clarification_status = "answered"
        append_audit_event(
            s.workspace_state,
            _current_session_id(),
            "clarification_answered",
            {"clarification_id": s.last_clarification_id, "answer": user_input},
        )
    s.q_index += 1
    s.assistant_working_state = derive_working_state(s.intent_raw, s.answers, s.analysis)

    if s.q_index < len(questions):
        next_q = questions[s.q_index]
        dedupe = _clarification_dedupe_check(next_q)
        if dedupe["action"] == "skip":
            append_audit_event(
                s.workspace_state,
                _current_session_id(),
                "clarification_skipped",
                {"question": next_q, "reason": dedupe["reason"]},
            )
            s.q_index += 1
            if s.q_index >= len(questions):
                next_q = ""
            else:
                next_q = questions[s.q_index]
        if next_q:
            s.last_clarification_id = dedupe["id"] if dedupe["action"] != "skip" else _clarification_id(next_q)
            append_audit_event(
                s.workspace_state,
                _current_session_id(),
                "clarification_asked",
                {"question": next_q, "clarification_id": s.last_clarification_id},
            )
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                reply = (
                    gen_next_question(ollama_url, s.analysis or {}, next_q, s.answers, s.llm_messages)
                    if use_ollama else f"Got it. {next_q}"
                )
            st.markdown(reply)
        add_msg("assistant", reply)
        add_llm("assistant", reply)
        return

    with st.chat_message("assistant"):
        with st.spinner(
            f"Building multi-domain plan across {len(s.analysis.get('domains', []))} domains…"
        ):
            synthesis = synthesize_plan(ollama_url, s.intent_raw, s.analysis, s.answers) if use_ollama else None
            if not synthesis:
                synthesis = _fallback_plan(s.intent_raw, s.analysis or {}, s.answers)

            plan = build_plan(s.intent_raw, synthesis, s.answers)
            plan["assistant_working_state"] = s.assistant_working_state
            s.plan = plan
            s.phase = "draft_artifact"
            open_panel("plan")

        with st.spinner("Drafting summary…"):
            reply = (
                gen_synthesis_intro(ollama_url, plan, s.llm_messages)
                if use_ollama else (
                    f"I've built a {plan.get('workflow_title','')} plan with "
                    f"{len(plan['skill_chain'])} skills. Review in the Plan panel."
                )
            )
        st.markdown(reply)
    add_msg("assistant", reply)
    add_llm("assistant", reply)
    s.phase = "reviewing"
    s.workflow_stage = "reviewing"
    s.completion_status = "ready_for_approval"


def _clarification_id(question: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", question.lower()).strip("_")


def _clarification_dedupe_check(question: str) -> dict[str, str]:
    s = st.session_state
    clarification_id = _clarification_id(question)
    prior = (s.clarification_answer_map or {}).get(clarification_id)
    if not prior:
        return {"action": "ask", "id": clarification_id, "reason": "new_question"}
    if _clarification_requires_reask(prior):
        append_audit_event(
            s.workspace_state,
            _current_session_id(),
            "clarification_invalidated",
            {"clarification_id": clarification_id, "reasons": prior.get("invalid_reasons", [])},
        )
        return {"action": "ask", "id": clarification_id, "reason": "invalidated"}
    return {"action": "skip", "id": clarification_id, "reason": "already_answered"}


def _clarification_requires_reask(prior: dict[str, Any]) -> bool:
    reasons = []
    if prior.get("contradiction_detected"):
        reasons.append("contradiction")
    if prior.get("scope_changed"):
        reasons.append("scope_change")
    expires_at = prior.get("expires_at")
    if expires_at and expires_at < datetime.now(timezone.utc).isoformat():
        reasons.append("expiry")
    answer = str(prior.get("answer", "")).strip()
    if not answer or answer.lower() in {"n/a", "unknown", "idk"}:
        reasons.append("invalid_answer")
    prior["invalid_reasons"] = reasons
    prior["valid"] = len(reasons) == 0
    return bool(reasons)


def _current_session_id() -> str:
    return f"session-{abs(hash(str(st.session_state.get('messages', []))))}"


def _dispatch_mode_for_intent(user_input: str, routed: dict[str, Any], ollama_url: str, use_ollama: bool) -> None:
    effective_mode = _resolve_effective_mode(routed.get("intent"))
    if effective_mode in ("Plan", "Workflow Builder", "Operator"):
        _run_conversational_mode(user_input, ollama_url, use_ollama)
        return

    s = st.session_state
    s.phase = "conversational_response"
    s.mode = "conversational"
    s.intent_raw = user_input
    s.analysis = None
    s.dynamic_questions = []
    s.q_index = 0
    s.answers = {}
    s.plan = None
    s.run_result = None
    s.poll_run_id = None
    s.workflow_data = None
    s.assistant_working_state = derive_working_state(s.intent_raw, s.answers, None)
    s.llm_messages = [{"role": "user", "content": user_input}]
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            if use_ollama:
                reply = gen_unknown_response(ollama_url, user_input)
            elif routed.get("intent") == "answer_only":
                reply = "Got it — here’s a direct response path without workflow intake."
            else:
                reply = "Got it — I can help with that directly."
        st.markdown(reply)
    add_msg("assistant", reply)
    add_llm("assistant", reply)
    s.phase = "done"


def derive_working_state(intent_raw: str, answers: dict[str, Any], analysis: dict | None = None) -> dict[str, Any]:
    assumptions = []
    for key, value in answers.items():
        assumptions.append(
            {
                "text": f"Answer to question {key}: {value}",
                "source": "user_chat",
                "confidence": "high",
                "status": "user_provided",
            }
        )
    return {
        "goal": intent_raw,
        "selected_intent": (analysis or {}).get("intent", ""),
        "intent_confidence": float((analysis or {}).get("confidence", 0.0) or 0.0),
        "assumptions": assumptions,
        "constraints": [],
        "risks": (analysis or {}).get("risks", []),
        "open_questions": [],
        "highest_impact_missing_datum": "",
        "next_safe_action": "Ask clarifying question or draft a safe plan with explicit assumptions.",
        "rationale_trace": [],
        "next_actions": ["Review plan", "Approve or refine before execution"],
    }

# ─────────────────────────────────────────────────────────────────────────────
# Panel renderers
# ─────────────────────────────────────────────────────────────────────────────

def render_plan_panel(plan: dict) -> None:
    st.markdown(f"### {plan.get('workflow_title', 'Workflow Plan')}")

    domains_str = " · ".join(DOMAIN_LABELS.get(d, d) for d in plan.get("domains", []))
    col_a, col_b = st.columns(2)
    col_a.metric("Domains", domains_str or "—")
    col_b.metric("Complexity", COMPLEXITY_LABELS.get(plan.get("complexity", ""), plan.get("complexity", "")))

    n_skills = len(plan.get("skill_chain", []))
    n_gates = len(plan.get("hitl_gates", []))
    col_c, col_d = st.columns(2)
    col_c.metric("Total Skills", n_skills)
    col_d.metric("HITL Gates", n_gates)

    if plan.get("rationale"):
        st.info(plan["rationale"])

    st.markdown("#### Execution Phases")
    for phase in plan.get("phases", []):
        with st.container(border=True):
            st.markdown(f"**{phase['name']}**")
            st.caption(phase.get("description", ""))
            for sk in phase.get("skills", []):
                info = ALL_SKILLS.get(sk, {})
                domain_tag = f"`{info.get('domain', '')}`" if info.get("domain") else ""
                st.markdown(f"- `{sk}` {domain_tag}  \n  *{info.get('description', '')}*")

    if plan.get("hitl_gates"):
        st.markdown("#### Approval Checkpoints")
        for gate in plan["hitl_gates"]:
            st.warning(f"**After {gate['after_phase']}:** {gate['reason']}", icon="🔒")

    if plan.get("risks"):
        with st.expander("Execution Risks"):
            for r in plan["risks"]:
                st.markdown(f"- {r}")

    if plan.get("context"):
        with st.expander("Context Collected"):
            for k, v in plan["context"].items():
                st.markdown(f"**Q{k}:** {v}")

    with st.expander("Raw Plan JSON"):
        st.json(plan)


def render_progress_panel(workflow: dict) -> None:
    run_id = workflow.get("run_id", "—")
    status = workflow.get("status", "unknown")
    color = STATUS_COLORS.get(status, "gray")

    st.markdown(f"### Workflow Progress")
    st.markdown(f"**Run:** `{run_id}`")
    st.markdown(f"**Status:** :{color}[{status.upper()}]")

    total = workflow.get("total_steps", 0)
    done = workflow.get("completed_steps", 0)
    if total > 0:
        st.progress(done / total, text=f"{done}/{total} steps")

    steps = workflow.get("steps", [])
    if steps:
        st.markdown("#### Steps")
        for step in steps:
            icon = STEP_ICONS.get(step.get("status", ""), "⏳")
            skill = step.get("skill_name", "")
            step_status = step.get("status", "pending")
            s_color = STATUS_COLORS.get(step_status, "gray")
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"{icon} `{skill}`")
                c2.markdown(f":{s_color}[{step_status}]")
                if step.get("output_preview"):
                    with st.expander("Output preview"):
                        st.text(step["output_preview"])
                if step.get("error"):
                    st.error(step["error"])
                if step.get("hitl_required"):
                    st.warning("Human approval required", icon="🔒")
    else:
        st.caption("No step data yet — execution in progress…")

    if workflow.get("completed_at"):
        st.success(f"Completed at {workflow['completed_at']}")
    elif status == "paused_for_hitl":
        st.warning("Workflow paused — awaiting your approval below.", icon="🔒")
    elif status in ("running", "queued"):
        st.info("Workflow is running. Refresh to see latest progress.", icon="⚙️")


def render_hitl_panel(approval: dict, api_url: str, token: str) -> None:
    st.markdown("### HITL Approval Required")
    approval_id = approval.get("approval_id", "")
    run_id = approval.get("run_id", "")

    with st.container(border=True):
        st.markdown(f"**Skill:** `{approval.get('skill_name', '—')}`")
        st.markdown(f"**Run:** `{run_id}`")
        risk = approval.get("risk_level", "MEDIUM")
        risk_score = approval.get("risk_score")
        col_a, col_b = st.columns(2)
        col_a.markdown(f"**Risk Level:** {risk}")
        if risk_score is not None:
            col_b.metric("Risk Score", f"{risk_score:.0f}/100")
        if approval.get("hitl_reason"):
            st.warning(approval["hitl_reason"], icon="⚠️")
        if approval.get("sla_deadline"):
            st.markdown(f"**SLA Deadline:** {approval['sla_deadline']}")

    reason = st.text_area("Comment (optional)", key="hitl_reason_input", height=80)

    col_approve, col_reject = st.columns(2)
    if col_approve.button("Approve", type="primary", use_container_width=True, key="panel_approve"):
        result = decide_approval(api_url, token, approval_id, "approved", reason)
        if "error" not in result:
            st.success("Approved! Workflow will resume.")
            st.session_state.hitl_approval = None
            st.session_state.phase = "executing"
            add_msg("user", f"Approved step `{approval.get('skill_name', '')}`. Workflow resuming.")
            st.rerun()
        else:
            st.error(f"Error: {result['error']}")

    if col_reject.button("Reject", type="secondary", use_container_width=True, key="panel_reject"):
        result = decide_approval(api_url, token, approval_id, "rejected", reason)
        if "error" not in result:
            st.error("Rejected. Workflow cancelled.")
            st.session_state.hitl_approval = None
            st.session_state.phase = "done"
            add_msg("assistant", f"The approval for `{approval.get('skill_name', '')}` was rejected. Workflow cancelled.")
            st.rerun()
        else:
            st.error(f"Error: {result['error']}")


def render_history_panel(item: dict) -> None:
    """Render a past conversation or workflow in the panel."""
    data = item.get("data", item)  # supports both conv records and workflow dicts

    # Past conversation
    if "messages" in data:
        plan = data.get("plan") or {}
        st.markdown(f"### {plan.get('workflow_title', 'Past Conversation')}")
        st.caption(f"Saved: {data.get('saved_at', '')}")
        if data.get("run_result"):
            rr = data["run_result"]
            st.markdown(f"**Run:** `{rr.get('run_id', '—')}` — {rr.get('status', '—')}")
        st.divider()
        for msg in data.get("messages", []):
            role = msg.get("role", "assistant")
            with st.chat_message(role):
                st.markdown(msg.get("content", ""))
        if plan:
            with st.expander("View Plan"):
                render_plan_panel(plan)

    # Workflow run from API
    elif "run_id" in data:
        render_progress_panel(data)


def render_workflow_list_panel(runs: list[dict], approvals: list[dict],
                               api_url: str, token: str) -> None:
    """Active workflows + approvals overview panel."""
    st.markdown("### Workflows")

    if approvals:
        st.markdown(f"#### HITL Queue ({len(approvals)} pending)")
        for apv in approvals:
            risk = apv.get("risk_level", "MEDIUM")
            col_a, col_b = st.columns([3, 1])
            col_a.markdown(f"🔒 `{apv.get('skill_name', '—')}`  \n`{apv.get('run_id', '')}`")
            if col_b.button("Review", key=f"rev_{apv['approval_id']}"):
                st.session_state.hitl_approval = apv
                open_panel("hitl")
                st.rerun()
        st.divider()

    if runs:
        st.markdown("#### Recent Runs")
        for run in runs:
            status = run.get("status", "unknown")
            color = STATUS_COLORS.get(status, "gray")
            col_a, col_b = st.columns([4, 1])
            col_a.markdown(f":{color}[●] `{run.get('run_id', '?')}`  \n_{run.get('objective', '')[:60]}_")
            if col_b.button("View", key=f"wf_{run.get('run_id', '')}"):
                detail = get_workflow(api_url, token, run["run_id"])
                if detail:
                    open_panel("progress", artifact=detail)
                st.rerun()
    else:
        st.caption("No workflow runs yet.")

# ─────────────────────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Apotheon",
    layout="wide",
    initial_sidebar_state="expanded",
)
_init()
_normalize_legacy_session_state()
s = st.session_state
if s.workspace_state is None:
    s.workspace_state = load_workspace_state(WORKSPACE_STATE_FILE)
    resume_session_from_workspace(s, s.workspace_state)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Apotheon")
    st.caption("AI Company Operating System")
    st.divider()
    selected_mode = st.selectbox("Mode", MODE_OPTIONS, index=MODE_OPTIONS.index(s.selected_mode))
    if selected_mode != s.selected_mode:
        _set_selected_mode(selected_mode)
        if s.workspace_state:
            s.workspace_state["workspace"]["selected_mode"] = s.selected_mode
        st.rerun()
    st.caption(f"Active mode: **{s.selected_mode}**")
    st.divider()

    # Config
    api_url    = st.text_input("Runtime URL", value=API_URL_ENV, key="cfg_api_url",
                               label_visibility="collapsed",
                               placeholder="http://runtime:8000")
    jwt_token  = st.text_input("JWT Token", value=JWT_ENV, key="cfg_jwt",
                               type="password", label_visibility="collapsed",
                               placeholder="JWT token")
    _api_up    = backend_up(api_url)
    api_status = "connected" if _api_up else "offline"

    ollama_url = st.text_input("Ollama URL", value=OLLAMA_URL, key="cfg_ollama_url",
                               label_visibility="collapsed")
    _ollama_up, _model_ready = ollama_status(ollama_url)
    use_ollama = _model_ready

    st.caption(f"Runtime: {api_status}  ·  LLM: {OLLAMA_MODEL if use_ollama else 'fallback'}")
    st.divider()

    # Execution mode
    dry_run = st.toggle("Dry-run (safe default)", value=True, key="cfg_dry_run")
    if not dry_run and not jwt_token.strip():
        st.warning("Provide JWT token for live mode.", icon="⚠️")
        dry_run = True

    st.divider()

    render_workspace_actions(s.workspace_state)
    st.divider()

    # New conversation
    if st.button("New Conversation", use_container_width=True, type="primary"):
        reset()
        st.rerun()

    st.divider()

    # Active workflows from API
    if _api_up and jwt_token:
        st.markdown("**Active Workflows**")
        _runs = list_workflows(api_url, jwt_token, limit=8)
        _approvals = get_approvals(api_url, jwt_token)
        if _approvals:
            st.markdown(f"🔒 **{len(_approvals)} approval(s) pending**")
            for apv in _approvals[:3]:
                if st.button(f"Review: {apv.get('skill_name','?')[:25]}", key=f"sb_apv_{apv['approval_id']}",
                             use_container_width=True):
                    s.hitl_approval = apv
                    open_panel("hitl")
                    st.rerun()
        if _runs:
            for run in _runs[:5]:
                status = run.get("status", "?")
                color  = STATUS_COLORS.get(status, "gray")
                label  = f":{color}[{status[:3].upper()}] {run.get('objective','')[:28]}"
                if st.button(label, key=f"sb_run_{run.get('run_id','')}", use_container_width=True):
                    detail = get_workflow(api_url, jwt_token, run["run_id"])
                    if detail:
                        open_panel("progress", artifact=detail)
                    st.rerun()
        else:
            st.caption("No runs yet.")
        if st.button("All Workflows", key="sb_all_runs", use_container_width=True):
            open_panel("progress", artifact={"_list": _runs, "_approvals": _approvals})
            st.rerun()
        st.divider()

    # Past conversations
    _convs = load_saved_conversations()
    if _convs:
        st.markdown("**Past Conversations**")
        for conv in _convs[:6]:
            ts = conv.get("saved_at", "")[:10]
            label = f"{ts} — {conv.get('title','?')[:30]}"
            if st.button(label, key=f"sb_conv_{conv['file']}", use_container_width=True):
                open_panel("history", artifact=conv)
                st.rerun()
        st.divider()

    # Skill catalog
    with st.expander("Skill Catalog"):
        st.caption(f"{len(ALL_SKILLS)} skills · {len(DOMAIN_LABELS)} domains")
        for dk, dl in DOMAIN_LABELS.items():
            domain_skills = [n for n, i in ALL_SKILLS.items() if i["domain"] == dk]
            st.markdown(f"**{dl}** ({len(domain_skills)})")
            st.caption(", ".join(domain_skills))

# ─────────────────────────────────────────────────────────────────────────────
# Main layout — chat + artifact panel
# ─────────────────────────────────────────────────────────────────────────────

# Panel toggle in top-right
header_cols = st.columns([8, 1])
with header_cols[0]:
    st.markdown(f"### Active Mode: `{s.selected_mode}`")
with header_cols[1]:
    panel_label = "← Close" if s.panel_open else "Panel →"
    if st.button(panel_label, key="toggle_panel"):
        s.panel_open = not s.panel_open
        st.rerun()

if s.panel_open:
    col_chat, col_panel = st.columns([5, 4], gap="large")
else:
    col_chat   = st.columns(1)[0]
    col_panel  = None

# ─────────────────────────────────────────────────────────────────────────────
# Artifact Panel
# ─────────────────────────────────────────────────────────────────────────────

if col_panel is not None:
    with col_panel:
        # Tab selector
        tab_options = {"plan": "Plan", "cognition": "Cognition", "progress": "Progress", "hitl": "Approvals", "history": "History"}
        tab_cols = st.columns(len(tab_options))
        for i, (tab_key, tab_label) in enumerate(tab_options.items()):
            active = s.panel_tab == tab_key
            btn_type = "primary" if active else "secondary"
            if tab_cols[i].button(tab_label, key=f"tab_{tab_key}", type=btn_type,
                                  use_container_width=True):
                s.panel_tab = tab_key
                st.rerun()

        st.divider()

        # ── Plan tab ──────────────────────────────────────────────────────────
        if s.panel_tab == "plan":
            plan = s.panel_artifact if isinstance(s.panel_artifact, dict) and "skill_chain" in (s.panel_artifact or {}) else s.plan
            if plan:
                render_plan_panel(plan)
                # Approve/cancel buttons when in reviewing phase
                if s.phase == "reviewing":
                    st.divider()
                    c1, c2 = st.columns(2)
                    if c1.button("Approve & Execute" if not dry_run else "Approve (dry-run)",
                                 type="primary", use_container_width=True, key="panel_plan_approve"):
                        add_msg("user", "Approved — proceed.")
                        s.phase = "executing"
                        s.panel_tab = "progress"
                        st.rerun()
                    if c2.button("Cancel", use_container_width=True, key="panel_plan_cancel"):
                        reset()
                        st.rerun()
            else:
                st.info("No plan yet. Start a conversation to build one.")

        # ── Cognition tab ─────────────────────────────────────────────────────
        elif s.panel_tab == "cognition":
            st.caption(f"Working mode: **{s.selected_mode}**")
            updated_state, changed = render_visible_cognition_panel(s.assistant_working_state)
            if changed:
                assumptions_changed = updated_state.get("assumptions", []) != (s.assistant_working_state or {}).get("assumptions", [])
                s.assistant_working_state = updated_state
                s.answers["goal"] = updated_state.get("goal", "")
                s.answers["constraints"] = updated_state.get("constraints", [])
                s.answers["open_questions"] = updated_state.get("open_questions", [])
                if s.plan:
                    s.plan["assistant_working_state"] = updated_state
                    s.plan["risks"] = updated_state.get("risks", s.plan.get("risks", []))
                if assumptions_changed:
                    s.phase = "analyzing"
                    s.plan = None
                    st.warning("Assumptions changed. Re-routing and re-drafting will run on next user turn.")
                st.success("Cognition state updated.")

        # ── Progress tab ──────────────────────────────────────────────────────
        elif s.panel_tab == "progress":
            art = s.panel_artifact
            if isinstance(art, dict) and "_list" in art:
                # Show workflow list + HITL queue
                render_workflow_list_panel(art.get("_list", []), art.get("_approvals", []),
                                           api_url, jwt_token)
            elif isinstance(art, dict) and "run_id" in art:
                render_progress_panel(art)
                if st.button("Refresh", key="progress_refresh"):
                    if art.get("run_id") and _api_up and jwt_token:
                        updated = get_workflow(api_url, jwt_token, art["run_id"])
                        if updated:
                            s.panel_artifact = updated
                    st.rerun()
            elif s.workflow_data:
                render_progress_panel(s.workflow_data)
            elif s.run_result and s.run_result.get("run_id") and _api_up and jwt_token:
                wf = get_workflow(api_url, jwt_token, s.run_result["run_id"])
                if wf:
                    s.workflow_data = wf
                    render_progress_panel(wf)
            else:
                st.info("No active workflow. Approve a plan to start execution.")

        # ── HITL tab ──────────────────────────────────────────────────────────
        elif s.panel_tab == "hitl":
            approval = s.hitl_approval or (s.panel_artifact if isinstance(s.panel_artifact, dict) and "approval_id" in (s.panel_artifact or {}) else None)
            if approval:
                render_hitl_panel(approval, api_url, jwt_token)
            else:
                # Show all pending approvals
                if _api_up and jwt_token:
                    pending = get_approvals(api_url, jwt_token)
                    if pending:
                        st.markdown(f"### {len(pending)} Pending Approval(s)")
                        for apv in pending:
                            with st.container(border=True):
                                st.markdown(f"**`{apv.get('skill_name','—')}`** — {apv.get('risk_level','')}")
                                st.caption(f"Run: {apv.get('run_id','')}")
                                if apv.get("hitl_reason"):
                                    st.markdown(apv["hitl_reason"])
                                if st.button("Review", key=f"panel_rev_{apv['approval_id']}",
                                            use_container_width=True):
                                    s.hitl_approval = apv
                                    st.rerun()
                    else:
                        st.success("No pending approvals.", icon="✅")
                else:
                    st.info("Connect to Runtime API to see live approvals.")

        # ── History tab ───────────────────────────────────────────────────────
        elif s.panel_tab == "history":
            art = s.panel_artifact
            if art and isinstance(art, dict) and ("messages" in art or "run_id" in art):
                render_history_panel(art)
                if st.button("Back to list", key="hist_back"):
                    s.panel_artifact = None
                    st.rerun()
            else:
                # List saved conversations + plan files
                convs = load_saved_conversations()
                plans = load_plan_files()
                if convs:
                    st.markdown("### Conversations")
                    for conv in convs:
                        with st.container(border=True):
                            col_a, col_b = st.columns([4, 1])
                            col_a.markdown(f"**{conv['title']}**")
                            col_a.caption(f"{conv['saved_at'][:19]}  ·  {conv['message_count']} messages")
                            if col_b.button("Open", key=f"h_conv_{conv['file']}", use_container_width=True):
                                open_panel("history", artifact=conv)
                                st.rerun()

                if plans:
                    st.markdown("### Saved Plans")
                    for p in plans:
                        with st.container(border=True):
                            col_a, col_b = st.columns([4, 1])
                            col_a.markdown(f"**{p['title']}**")
                            col_a.caption(" · ".join(DOMAIN_LABELS.get(d, d) for d in p["domains"]))
                            if col_b.button("View", key=f"h_plan_{p['file']}", use_container_width=True):
                                open_panel("plan", artifact=p["plan"])
                                st.rerun()

                if not convs and not plans:
                    st.info("No saved conversations yet. Complete a workflow to see history here.")

# ─────────────────────────────────────────────────────────────────────────────
# Chat Column
# ─────────────────────────────────────────────────────────────────────────────

with col_chat:

    # Message history
    for msg in s.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Welcome message
    if s.phase == "idle" and not s.messages:
        with st.chat_message("assistant"):
            model_note = f"Powered by **{OLLAMA_MODEL}**." if use_ollama else "Running in local fallback mode."
            st.markdown(
                f"**Welcome to Apotheon.** {model_note}\n\n"
                "Describe what your organisation needs to accomplish. I'll analyse the full scope, "
                "identify all relevant domains and skills, ask targeted questions, then build a "
                "complete multi-domain workflow plan for your review.\n\n"
                "Examples:\n"
                "- *We need to contract a new overseas logistics vendor*\n"
                "- *Launch our SaaS product in the European market*\n"
                "- *Close the books for Q2 and produce board reporting*\n"
                "- *Onboard 50 new enterprise customers this quarter*\n"
                "- *Achieve SOC 2 Type II certification by Q4*"
            )

    # HITL notification card in chat
    if s.phase == "hitl_pending" and s.hitl_approval:
        apv = s.hitl_approval
        with st.chat_message("assistant"):
            st.warning(
                f"**Approval required** — the workflow is paused at step `{apv.get('skill_name', '?')}`.\n\n"
                f"Risk level: **{apv.get('risk_level', 'MEDIUM')}**\n\n"
                f"{apv.get('hitl_reason', '')}\n\n"
                "Use the **Approvals** tab in the panel to approve or reject.",
                icon="🔒",
            )
            if st.button("Open Approval Panel", key="chat_open_hitl"):
                open_panel("hitl")
                st.rerun()

    # Plan review notification (full plan is in the panel)
    if s.phase == "reviewing" and s.plan:
        with st.chat_message("assistant"):
            n = len(s.plan.get("skill_chain", []))
            phases = [p["name"] for p in s.plan.get("phases", [])]
            domains = " · ".join(DOMAIN_LABELS.get(d, d) for d in s.plan.get("domains", []))
            st.markdown(
                f"**Plan ready:** [{s.plan.get('workflow_title', 'Workflow')}]\n\n"
                f"**{domains}** · {n} skills · {len(phases)} phases · "
                f"{len(s.plan.get('hitl_gates', []))} approval gate(s)\n\n"
                "Review the full plan in the **Plan** tab on the right."
            )
            c1, c2, c3 = st.columns([3, 2, 1])
            if c1.button(
                "Approve & Execute" if not dry_run else "Approve (dry-run)",
                type="primary", use_container_width=True, key="chat_approve",
            ):
                add_msg("user", "Approved — proceed.")
                s.phase = "executing"
                s.panel_tab = "progress"
                st.rerun()
            if c2.button("Edit Answers", use_container_width=True, key="chat_edit"):
                add_msg("user", "I want to revise my answers.")
                add_llm("user", "I want to revise my answers.")
                s.q_index = 0
                s.answers = {}
                s.plan = None
                s.mode = "workflow_builder"
                s.phase = "questioning"
                first_q = s.dynamic_questions[0] if s.dynamic_questions else "What is the primary goal?"
                reply = gen_next_question(ollama_url, s.analysis or {}, first_q, {}, s.llm_messages)
                add_msg("assistant", reply)
                add_llm("assistant", reply)
                st.rerun()
            if c3.button("Cancel", use_container_width=True, key="chat_cancel"):
                reset()
                st.rerun()

    # Execution progress notification
    if s.phase == "executing" and s.plan and not s.run_result:
        with st.chat_message("assistant"):
            with st.spinner("Submitting workflow to runtime…"):
                result = (
                    submit_to_backend(s.plan, dry_run, api_url, jwt_token)
                    if (_api_up and jwt_token)
                    else {
                        "run_id": f"LOCAL-{int(time.time())}",
                        "status": "dry_run_saved",
                        "note":   "Backend offline — plan saved locally",
                    }
                )
                try:
                    save_plan(s.plan)
                    save_conversation(s.messages, s.plan, result)
                except Exception:
                    pass
                s.run_result = result
                s.poll_run_id = result.get("run_id")

            if "error" in result:
                reply = f"Submission error: `{result['error']}`\n\nCheck sidebar settings."
                s.phase = "done"
            elif dry_run or result.get("status") == "dry_run_saved":
                reply = (
                    f"Plan `{result.get('run_id','—')}` saved as **dry-run** — no live writes.\n\n"
                    "Disable *Dry-run* in the sidebar and add a JWT token to execute for real. "
                    "Your plan is saved in History."
                )
                s.phase = "done"
            else:
                reply = (
                    f"Workflow `{result.get('run_id','—')}` submitted and queued.\n\n"
                    "Progress is shown in the **Progress** tab. I'll alert you if approval is required."
                )
                s.panel_tab = "progress"
                # Don't set phase to done yet — keep polling

            add_msg("assistant", reply)
            st.markdown(reply)

    # Polling while executing live
    if s.phase == "executing" and s.poll_run_id and _api_up and jwt_token and s.run_result:
        now = time.time()
        if now - s.last_poll_ts > 5:
            s.last_poll_ts = now
            wf_data = get_workflow(api_url, jwt_token, s.poll_run_id)
            if wf_data:
                s.workflow_data = wf_data
                wf_status = wf_data.get("status", "")

                if wf_status == "paused_for_hitl":
                    # Fetch pending approval
                    all_approvals = get_approvals(api_url, jwt_token)
                    run_approvals = [a for a in all_approvals if a.get("run_id") == s.poll_run_id]
                    if run_approvals:
                        s.hitl_approval = run_approvals[0]
                        s.phase = "hitl_pending"
                        open_panel("hitl")
                        skill_name = run_approvals[0].get("skill_name", "unknown")
                        add_msg("assistant",
                                f"**Approval required** — the workflow has reached a human checkpoint "
                                f"at skill `{skill_name}`. See the Approvals panel.")
                        st.rerun()

                elif wf_status in ("completed", "failed", "cancelled"):
                    s.phase = "done"
                    open_panel("progress", artifact=wf_data)
                    status_word = "completed successfully" if wf_status == "completed" else f"ended with status **{wf_status}**"
                    add_msg("assistant",
                            f"Workflow `{s.poll_run_id}` has {status_word}. "
                            "Full details are in the Progress tab.")
                    st.rerun()
                else:
                    # Still running — update panel and auto-rerun
                    if s.panel_tab == "progress":
                        s.panel_artifact = wf_data
                    time.sleep(5)
                    st.rerun()

    # Done state
    if s.phase == "done":
        with st.chat_message("assistant"):
            if s.workflow_builder_paused:
                st.markdown("Workflow Builder intake is paused safely. Switch back to **Workflow Builder** mode to resume question collection.")
            else:
                st.markdown("Workflow complete. Type a new request to start another.")

    # Question progress indicator
    if s.phase == "questioning" and s.mode == "workflow_builder" and s.dynamic_questions:
        total = len(s.dynamic_questions)
        st.progress(s.q_index / total if total else 0,
                    text=f"Question {s.q_index}/{total}")

    # ── Chat input ─────────────────────────────────────────────────────────────
    placeholders = {
        "idle":        "Describe what your organisation needs to accomplish…",
        "conversational_response": "Thinking…",
        "draft_artifact": "Drafting artifact…",
        "questioning": "Type your answer…",
        "reviewing":   "Type 'approve' or 'cancel', or use the buttons above…",
        "executing":   "Workflow running…",
        "hitl_pending":"Type 'approve' or 'reject', or use the Approvals panel…",
        "done":        "Type a new request to start another workflow…",
    }
    user_input = st.chat_input(placeholders.get(s.phase, "Type here…"),
                               disabled=(s.phase == "executing"))

    if user_input:
        if WORKSPACE_STATE_FILE.exists():
            s.workspace_state = load_workspace_state(WORKSPACE_STATE_FILE)
        user_input = user_input.strip()
        add_msg("user", user_input)
        add_llm("user", user_input)

        # ── idle / done → route intent then dispatch ─────────────────────────
        if s.phase in ("idle", "done"):
            routed = route_conversation_intent(user_input)
            mode_prior_intent = MODE_TO_INTENT.get(s.selected_mode)
            if s.explicit_mode_override and mode_prior_intent:
                routed["intent"] = mode_prior_intent
                routed["rationale"] = "explicit_mode_override"
                routed["confidence"] = max(float(routed.get("confidence", 0.0)), 0.99)
            s.routed_intent = routed.get("intent")
            s.routed_intent_confidence = routed.get("confidence")
            if isinstance(s.assistant_working_state, dict):
                s.assistant_working_state["selected_intent"] = s.routed_intent or ""
                s.assistant_working_state["intent_confidence"] = float(s.routed_intent_confidence or 0.0)
            _dispatch_mode_for_intent(user_input, routed, ollama_url, use_ollama)
            _persist_turn_state()
            st.rerun()

        # ── questioning → collect answer, advance ─────────────────────────────
        elif s.phase == "questioning" and s.mode == "workflow_builder":
            _run_workflow_builder_mode(user_input, ollama_url, use_ollama)
            _persist_turn_state()
            st.rerun()

        # ── reviewing → text approval ─────────────────────────────────────────
        elif s.phase == "reviewing":
            lower = user_input.lower()
            if any(w in lower for w in ["yes","approve","ok","proceed","run","go","confirm","execute"]):
                s.phase = "executing"
                s.panel_tab = "progress"
            elif any(w in lower for w in ["no","cancel","stop","reset","abort","start over"]):
                reset()
            else:
                add_msg("assistant",
                        "Use the **Approve** / **Cancel** buttons above, or type `approve` / `cancel`.")
            _persist_turn_state()
            st.rerun()

        # ── hitl_pending → text decision ──────────────────────────────────────
        elif s.phase == "hitl_pending":
            lower = user_input.lower()
            if s.hitl_approval and any(w in lower for w in ["approve","yes","proceed","ok","go"]):
                apv = s.hitl_approval
                result = decide_approval(api_url, jwt_token, apv["approval_id"], "approved",
                                         "Approved via chat")
                if "error" not in result:
                    s.hitl_approval = None
                    s.phase = "executing"
                    s.panel_tab = "progress"
                    add_msg("assistant",
                            f"Approved. Workflow `{apv.get('run_id','')}` is resuming.")
                else:
                    add_msg("assistant", f"Error submitting approval: {result['error']}")
            elif s.hitl_approval and any(w in lower for w in ["reject","no","cancel","stop","deny"]):
                apv = s.hitl_approval
                result = decide_approval(api_url, jwt_token, apv["approval_id"], "rejected",
                                         "Rejected via chat")
                if "error" not in result:
                    s.hitl_approval = None
                    s.phase = "done"
                    add_msg("assistant",
                            f"Rejected. Workflow `{apv.get('run_id','')}` has been cancelled.")
                else:
                    add_msg("assistant", f"Error submitting rejection: {result['error']}")
            else:
                add_msg("assistant",
                        "Type `approve` or `reject`, or use the **Approvals** panel to review details.")
            _persist_turn_state()
            st.rerun()
