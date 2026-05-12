"""
Apotheon Chat UI — multi-domain, multi-skill conversational workflow planner.

Flow:
    idle → [Ollama analysis: domains + dynamic questions] → questioning
         → [Ollama synthesis: full multi-phase plan] → reviewing
         → executing → done

Ollama (qwen3:4b) drives intent analysis, question generation, and plan synthesis.
All configuration lives in the sidebar — no code changes required.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

OLLAMA_URL   = os.environ.get("OLLAMA_URL",         "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL",       "qwen3:4b")
API_URL_ENV  = os.environ.get("APOTHEON_API_URL",   "http://localhost:8000")

ROOT        = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"

# ─────────────────────────────────────────────────────────────────────────────
# Skill catalog
# All skills Apotheon can orchestrate, with domain + description.
# Ollama selects from this catalog during plan synthesis.
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

# Domain labels and rich descriptions for Ollama context
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
    "done": "green", "queued": "blue", "running": "orange",
    "failed": "red",  "dry_run_saved": "gray", "cancelled": "gray",
}

COMPLEXITY_LABELS = {
    "simple":     "Simple (1–3 skills)",
    "moderate":   "Moderate (4–7 skills)",
    "complex":    "Complex (8–15 skills)",
    "enterprise": "Enterprise (15+ skills, multi-phase)",
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


def list_recent_runs(api_url: str, token: str, limit: int = 8) -> list[dict]:
    code, resp = _http(f"{api_url}/v1/workflows?limit={limit}", token=token)
    return resp if (code == 200 and isinstance(resp, list)) else []

# ─────────────────────────────────────────────────────────────────────────────
# Skill catalog helpers
# ─────────────────────────────────────────────────────────────────────────────

def _catalog_text() -> str:
    """Compact skill catalog for Ollama prompts."""
    lines = []
    for name, info in ALL_SKILLS.items():
        lines.append(f"  {name} [{info['domain']}]: {info['description']}")
    return "\n".join(lines)


def _domain_context() -> str:
    return "\n".join(
        f"  {k}: {DOMAIN_DESCRIPTIONS[k]}" for k in DOMAIN_LABELS
    )

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Analyze request: identify domains, skills, generate questions
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
  "questions": [
    "Question 1 — must be specific to THIS request?",
    "Question 2?",
    "Question 3?"
  ]
}}

Rules for questions:
- Generate 3 to 6 questions that SPAN ALL identified domains.
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
    """
    Stage 1: Multi-domain analysis.
    Returns {workflow_title, understanding, domains, complexity, skills_preview, questions}
    or None on failure.
    """
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
    # Validate minimal structure
    if result and isinstance(result.get("questions"), list) and len(result["questions"]) > 0:
        return result
    return None


def _fallback_analysis(request: str) -> dict:
    """Python fallback when Ollama analysis fails."""
    return {
        "workflow_title": "Workflow Plan",
        "understanding": request,
        "domains": ["business", "legal", "finance"],
        "complexity": "moderate",
        "skills_preview": ["business-orchestration", "governance", "compliance-runtime",
                           "accounts-payable-automation", "audit-trail"],
        "questions": [
            "What is the primary goal of this initiative?",
            "Which teams or stakeholders need to be involved?",
            "What is the timeline and any hard deadlines?",
            "Are there budget, regulatory, or technical constraints?",
            "What does a successful outcome look like?",
        ],
    }

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Synthesize plan from analysis + answers
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
    """
    Stage 2: Build the full multi-domain plan from analysis + collected answers.
    Returns synthesized plan dict or None on failure.
    """
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
        # Validate skills against catalog, remove unknown ones
        valid = {s for s in result["skill_chain"] if s in ALL_SKILLS}
        if valid:
            result["skill_chain"] = [s for s in result["skill_chain"] if s in ALL_SKILLS]
            return result
    return None


def _fallback_plan(request: str, analysis: dict, answers: dict) -> dict:
    """Python fallback plan when Ollama synthesis fails."""
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
# Build final plan dict (wraps synthesis output into API-compatible plan)
# ─────────────────────────────────────────────────────────────────────────────

def build_plan(request: str, synthesis: dict, answers: dict) -> dict:
    steps = []
    for i, skill in enumerate(synthesis["skill_chain"], 1):
        info = ALL_SKILLS.get(skill, {"domain": "business", "description": ""})
        steps.append({
            "id":       f"step-{i}",
            "order":    i,
            "title":    f"Run {skill}",
            "skill":    skill,
            "domain":   info["domain"],
            "description": info["description"],
            "depends_on":  [steps[-1]["id"]] if steps else [],
            "inputs":   answers,
            "governance_policy_refs": ["references/business-policy-standard.md"],
            "outputs":  [f"reports/{skill}-output.json"],
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
            "planner": "multi-domain-planner",
            "version": "2.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def save_plan(plan: dict) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    (REPORTS_DIR / f"{plan['id']}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Conversational response generators
# ─────────────────────────────────────────────────────────────────────────────

CONVO_SYSTEM = """\
You are Apotheon, an AI business workflow planning assistant. You orchestrate complex, \
multi-domain business workflows. You are talking to a business operator.

Rules:
- Be concise, specific, and professional.
- Responses must be under 4 sentences.
- Ask only ONE question at a time.
- Reference the user's specific context, not generic placeholders.
- Do not use bullet points inside your questions.\
"""


def gen_analysis_greeting(ollama_url: str, request: str, analysis: dict) -> str:
    domains_str = ", ".join(DOMAIN_LABELS.get(d, d) for d in analysis.get("domains", []))
    n_skills = len(analysis.get("skills_preview", []))
    complexity = COMPLEXITY_LABELS.get(analysis.get("complexity", "moderate"), "")
    first_q = analysis["questions"][0]

    system = (
        CONVO_SYSTEM + "\n\n"
        f"You have analyzed the user's request and identified:\n"
        f"  Workflow: {analysis.get('workflow_title', '')}\n"
        f"  Domains involved: {domains_str}\n"
        f"  Estimated complexity: {complexity} (~{n_skills} skills)\n"
        f"  Your understanding: {analysis.get('understanding', '')}\n\n"
        f"Write a response that:\n"
        f"1. Confirms you understand the full scope (mention the multiple domains involved).\n"
        f"2. Explains this will be a multi-domain plan.\n"
        f"3. Asks this first question conversationally (do NOT copy verbatim — rephrase naturally):\n"
        f"   {first_q}"
    )
    reply = _ollama_call(ollama_url, system, [{"role": "user", "content": request}],
                         max_tokens=300, temperature=0.5)
    if not reply:
        return (
            f"This is a multi-domain workflow touching **{domains_str}**. "
            f"I've identified approximately {n_skills} skills across {len(analysis.get('domains',[]))} domains. "
            f"Let me ask a few targeted questions to build the right plan.\n\n{first_q}"
        )
    return reply


def gen_next_question(ollama_url: str, analysis: dict, question: str,
                      answers: dict, llm_messages: list[dict]) -> str:
    domains_str = ", ".join(DOMAIN_LABELS.get(d, d) for d in analysis.get("domains", []))
    system = (
        CONVO_SYSTEM + "\n\n"
        f"Workflow being planned: {analysis.get('workflow_title', '')}\n"
        f"Domains: {domains_str}\n"
        f"Context collected so far: {json.dumps(answers)}\n\n"
        f"Briefly acknowledge the user's last answer (5–8 words, be specific), "
        f"then ask this next question conversationally — rephrase naturally, do NOT copy:\n"
        f"  {question}"
    )
    reply = _ollama_call(ollama_url, system, llm_messages, max_tokens=200, temperature=0.5)
    if not reply:
        return f"Understood. {question}"
    return reply


def gen_synthesis_intro(ollama_url: str, plan: dict, llm_messages: list[dict]) -> str:
    domains_str = ", ".join(DOMAIN_LABELS.get(d, d) for d in plan.get("domains", []))
    n = len(plan.get("skill_chain", []))
    phases = [p["name"] for p in plan.get("phases", [])]
    system = (
        CONVO_SYSTEM + "\n\n"
        f"You have synthesized a complete multi-domain workflow plan.\n"
        f"Title: {plan.get('workflow_title', '')}\n"
        f"Domains: {domains_str}\n"
        f"Total skills: {n}\n"
        f"Phases: {' → '.join(phases)}\n"
        f"Rationale: {plan.get('rationale', '')}\n"
        f"HITL gates: {len(plan.get('hitl_gates', []))} approval checkpoint(s)\n\n"
        f"Write 2–3 sentences:\n"
        f"1. Summarise what the plan accomplishes end-to-end.\n"
        f"2. Highlight why this spans multiple domains.\n"
        f"3. Tell the user to review and approve below."
    )
    reply = _ollama_call(ollama_url, system, llm_messages, max_tokens=300, temperature=0.5)
    if not reply:
        return (
            f"I've built a **{plan.get('workflow_title', 'multi-domain')}** plan spanning "
            f"**{domains_str}** with {n} skills across {len(phases)} phases. "
            "Review the full plan below and approve when ready."
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
    if not reply:
        return ("I want to make sure I build the right plan. Could you tell me more about "
                "the primary outcome you're trying to achieve?")
    return reply

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

def _init() -> None:
    defaults: dict[str, Any] = {
        "phase":            "idle",     # idle|questioning|reviewing|executing|done
        "messages":         [],         # [{role, content, ts}] — display history
        "llm_messages":     [],         # [{role, content}]     — Ollama context
        "intent_raw":       "",
        "analysis":         None,       # Stage 1 result
        "dynamic_questions":[],         # list of question strings from analysis
        "q_index":          0,
        "answers":          {},
        "plan":             None,       # final plan dict
        "run_result":       None,
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
              "dynamic_questions", "q_index", "answers", "plan", "run_result"]:
        st.session_state.pop(k, None)

# ─────────────────────────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Apotheon", layout="wide", initial_sidebar_state="expanded")
_init()
s = st.session_state

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Apotheon")
    st.caption("AI Company Operating System")
    st.divider()

    st.markdown("**Runtime API**")
    api_url = st.text_input("URL", value=API_URL_ENV, label_visibility="collapsed", key="cfg_api_url")
    _api_up = backend_up(api_url)
    st.caption("Runtime: " + ("connected" if _api_up else "offline"))
    st.divider()

    st.markdown("**Local LLM**")
    ollama_url = st.text_input("Ollama URL", value=OLLAMA_URL, label_visibility="collapsed", key="cfg_ollama_url")
    _ollama_up, _model_ready = ollama_status(ollama_url)
    if _model_ready:
        st.success(f"{OLLAMA_MODEL} ready", icon="✅")
        use_ollama = True
    elif _ollama_up:
        st.warning(f"Pulling {OLLAMA_MODEL}…", icon="⏳")
        use_ollama = False
    else:
        st.error("Ollama offline — local fallback active", icon="❌")
        use_ollama = False
    st.divider()

    st.markdown("**Execution mode**")
    dry_run = st.toggle("Dry-run only (safe default)", value=True, key="cfg_dry_run")
    jwt_token = ""
    if not dry_run:
        st.warning("Live mode: real writes will occur.", icon="⚠️")
        jwt_token    = st.text_input("JWT token", type="password", key="cfg_jwt")
        approval_ref = st.text_input("Approval ticket", placeholder="CAB-2026-0511", key="cfg_approval")
        if not (jwt_token.strip() and approval_ref.strip()):
            st.error("Provide JWT + approval ticket.")
            dry_run = True
    st.divider()

    if st.button("New conversation", use_container_width=True):
        reset()
        st.rerun()

    with st.expander("Skill catalog"):
        st.caption(f"{len(ALL_SKILLS)} skills across {len(DOMAIN_LABELS)} domains")
        for domain_key, domain_label in DOMAIN_LABELS.items():
            domain_skills = [n for n, i in ALL_SKILLS.items() if i["domain"] == domain_key]
            st.markdown(f"**{domain_label}** ({len(domain_skills)})")
            st.caption(", ".join(domain_skills))

    if _api_up:
        with st.expander("Recent runs"):
            for r in list_recent_runs(api_url, jwt_token):
                status = r.get("status", "unknown")
                color  = STATUS_COLORS.get(status, "gray")
                st.markdown(f":{color}[●] `{r.get('run_id','?')}`  \n_{r.get('objective','')[:50]}_")

# ─── Layout ───────────────────────────────────────────────────────────────────
col_chat, col_ctx = st.columns([3, 1], gap="large")

# ─── Context panel ────────────────────────────────────────────────────────────
with col_ctx:
    st.markdown("### Session")
    phase_labels = {
        "idle":        "Waiting",
        "questioning": "Gathering context",
        "reviewing":   "Awaiting approval",
        "executing":   "Executing",
        "done":        "Complete",
    }
    st.markdown(f"**Status:** {phase_labels.get(s.phase, s.phase)}")
    st.markdown(f"**LLM:** {'Ollama / ' + OLLAMA_MODEL if use_ollama else 'Local fallback'}")

    if s.analysis:
        st.markdown("---")
        a = s.analysis
        st.markdown(f"**Workflow:** {a.get('workflow_title','—')}")
        st.markdown(f"**Complexity:** {COMPLEXITY_LABELS.get(a.get('complexity',''), a.get('complexity',''))}")
        domains = a.get("domains", [])
        if domains:
            st.markdown("**Domains:**")
            for d in domains:
                st.markdown(f"- {DOMAIN_LABELS.get(d, d)}")

    if s.phase == "questioning" and s.dynamic_questions:
        total = len(s.dynamic_questions)
        st.progress(s.q_index / total, text=f"Questions {s.q_index}/{total}")

    if s.answers:
        st.markdown("---")
        st.markdown("**Context**")
        for k, v in s.answers.items():
            st.markdown(f"**Q{k}:** {v[:80]}{'…' if len(v) > 80 else ''}")

    if s.plan:
        st.markdown("---")
        st.markdown("**Plan**")
        st.caption(s.plan.get("id", ""))
        for phase in s.plan.get("phases", []):
            st.markdown(f"**{phase['name']}**")
            for sk in phase.get("skills", []):
                st.markdown(f"  `{sk}`")

    if s.run_result:
        st.markdown("---")
        run_id = s.run_result.get("run_id", "—")
        status = s.run_result.get("status", s.run_result.get("error", "unknown"))
        color  = STATUS_COLORS.get(status, "gray")
        st.markdown(f"**Run:** `{run_id}`")
        st.markdown(f":{color}[{status}]")

# ─── Chat panel ───────────────────────────────────────────────────────────────
with col_chat:

    for msg in s.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Welcome
    if s.phase == "idle" and not s.messages:
        with st.chat_message("assistant"):
            model_note = f"Powered by **{OLLAMA_MODEL}**." if use_ollama else "Running in local fallback mode."
            st.markdown(
                f"**Welcome to Apotheon.** {model_note}\n\n"
                "Describe what your organisation needs to accomplish. I'll analyse the full scope, "
                "identify all relevant domains and skills, ask targeted questions, then build a "
                "complete multi-domain workflow plan.\n\n"
                "Examples:\n"
                "- *We need to contract a new overseas logistics vendor*\n"
                "- *Launch our SaaS product in the European market*\n"
                "- *Close the books for Q2 and produce board reporting*\n"
                "- *Onboard 50 new enterprise customers this quarter*\n"
                "- *Achieve SOC 2 Type II certification by Q4*"
            )

    # Approval UI
    if s.phase == "reviewing" and s.plan:
        with st.chat_message("assistant"):
            st.markdown("**Multi-domain workflow plan ready for review:**")
            plan = s.plan

            # Rationale
            if plan.get("rationale"):
                st.info(plan["rationale"])

            # Domains + complexity
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Domains involved:**")
                for d in plan.get("domains", []):
                    st.markdown(f"- {DOMAIN_LABELS.get(d, d)}")
            with col_b:
                st.markdown(f"**Complexity:** {COMPLEXITY_LABELS.get(plan.get('complexity',''), '')}")
                st.markdown(f"**Total skills:** {len(plan.get('skill_chain', []))}")
                st.markdown(f"**HITL gates:** {len(plan.get('hitl_gates', []))}")

            # Phases
            st.markdown("**Execution phases:**")
            for phase in plan.get("phases", []):
                with st.container(border=True):
                    st.markdown(f"**{phase['name']}** — {phase.get('description','')}")
                    skills_in_phase = phase.get("skills", [])
                    for sk in skills_in_phase:
                        info = ALL_SKILLS.get(sk, {})
                        st.markdown(f"  `{sk}` — {info.get('description', '')}")

            # HITL gates
            if plan.get("hitl_gates"):
                st.markdown("**Human approval checkpoints:**")
                for gate in plan["hitl_gates"]:
                    st.warning(f"After **{gate['after_phase']}**: {gate['reason']}", icon="🔒")

            # Risks
            if plan.get("risks"):
                with st.expander("Execution risks"):
                    for r in plan["risks"]:
                        st.markdown(f"- {r}")

            with st.expander("Full plan JSON"):
                st.json(plan)

            st.markdown("**Context collected:**")
            for k, v in plan.get("context", {}).items():
                st.markdown(f"- **Q{k}:** {v}")

            c1, c2, c3 = st.columns([2, 2, 1])
            if c1.button(
                "Approve and execute" if not dry_run else "Approve (dry-run)",
                type="primary", use_container_width=True, key="btn_approve",
            ):
                add_msg("user", "Approved — proceed.")
                s.phase = "executing"
                st.rerun()

            if c2.button("Edit answers", use_container_width=True, key="btn_edit"):
                add_msg("user", "I want to revise my answers.")
                add_llm("user", "I want to revise my answers.")
                s.q_index = 0
                s.answers = {}
                s.plan = None
                s.phase = "questioning"
                first_q = s.dynamic_questions[0] if s.dynamic_questions else "What is the primary goal?"
                reply = gen_next_question(ollama_url, s.analysis or {}, first_q, {}, s.llm_messages)
                add_msg("assistant", reply)
                add_llm("assistant", reply)
                st.rerun()

            if c3.button("Cancel", use_container_width=True, key="btn_cancel"):
                reset()
                st.rerun()

    # Execution
    if s.phase == "executing" and s.plan and not s.run_result:
        with st.chat_message("assistant"):
            with st.spinner("Submitting plan to runtime…"):
                result = (
                    submit_to_backend(s.plan, dry_run, api_url, jwt_token)
                    if _api_up
                    else {"run_id": f"LOCAL-{int(time.time())}", "status": "dry_run_saved",
                          "note": "Backend offline — plan saved locally"}
                )
                try:
                    save_plan(s.plan)
                except Exception:
                    pass
                s.run_result = result
                s.phase = "done"

            if "error" in result:
                reply = f"Execution error: `{result['error']}`\n\nCheck sidebar settings."
            elif dry_run:
                reply = (
                    f"Plan `{result.get('run_id','—')}` submitted as **dry-run** — no live writes made.\n\n"
                    "Disable *Dry-run only* in the sidebar and provide JWT + approval ticket to execute for real."
                )
            else:
                reply = (
                    f"Plan `{result.get('run_id','—')}` queued.\n\n"
                    "Monitor progress in the **Control Plane Dashboard** at port 8502."
                )
            add_msg("assistant", reply)
            st.markdown(reply)

    # Done
    if s.phase == "done":
        with st.chat_message("assistant"):
            st.markdown("Workflow submitted. Type a new request to plan another workflow.")

    # ── Chat input ─────────────────────────────────────────────────────────────
    placeholders = {
        "idle":        "Describe what your organisation needs to accomplish…",
        "questioning": "Type your answer…",
        "reviewing":   "Type 'yes' to approve or 'no' to cancel…",
        "done":        "Type a new request…",
    }
    user_input = st.chat_input(placeholders.get(s.phase, "Type here…"))

    if user_input:
        user_input = user_input.strip()
        add_msg("user", user_input)
        add_llm("user", user_input)

        # ── idle/done → analyze request ───────────────────────────────────────
        if s.phase in ("idle", "done"):
            s.intent_raw = user_input
            s.q_index = 0
            s.answers = {}
            s.plan = None
            s.run_result = None
            s.llm_messages = [{"role": "user", "content": user_input}]

            with st.chat_message("assistant"):
                with st.spinner(f"Analysing request across all domains…"):
                    analysis = analyze_request(ollama_url, user_input) if use_ollama else None
                    if not analysis:
                        analysis = _fallback_analysis(user_input)

                s.analysis = analysis
                s.dynamic_questions = analysis.get("questions", [])

                if s.dynamic_questions:
                    s.phase = "questioning"
                    with st.spinner("Thinking…"):
                        reply = gen_analysis_greeting(ollama_url, user_input, analysis) if use_ollama else (
                            f"This is a **{analysis.get('workflow_title','')}** workflow touching "
                            + ", ".join(DOMAIN_LABELS.get(d, d) for d in analysis.get("domains", []))
                            + f".\n\n{s.dynamic_questions[0]}"
                        )
                else:
                    with st.spinner("Thinking…"):
                        reply = gen_unknown_response(ollama_url, user_input) if use_ollama else (
                            "Could you describe the primary goal in more detail?"
                        )

                st.markdown(reply)

            add_msg("assistant", reply)
            add_llm("assistant", reply)
            st.rerun()

        # ── questioning → collect answer, advance ─────────────────────────────
        elif s.phase == "questioning":
            questions = s.dynamic_questions
            # Store answer keyed by question index
            s.answers[str(s.q_index + 1)] = user_input
            s.q_index += 1

            if s.q_index < len(questions):
                next_q = questions[s.q_index]
                with st.chat_message("assistant"):
                    with st.spinner("Thinking…"):
                        reply = (
                            gen_next_question(ollama_url, s.analysis or {}, next_q,
                                              s.answers, s.llm_messages)
                            if use_ollama else f"Got it. {next_q}"
                        )
                    st.markdown(reply)
                add_msg("assistant", reply)
                add_llm("assistant", reply)
            else:
                # All answered → synthesize plan
                with st.chat_message("assistant"):
                    with st.spinner(f"Building multi-domain plan across {len(s.analysis.get('domains',[]))} domains…"):
                        synthesis = (
                            synthesize_plan(ollama_url, s.intent_raw, s.analysis, s.answers)
                            if use_ollama else None
                        )
                        if not synthesis:
                            synthesis = _fallback_plan(s.intent_raw, s.analysis or {}, s.answers)

                        plan = build_plan(s.intent_raw, synthesis, s.answers)
                        s.plan = plan
                        s.phase = "reviewing"

                        with st.spinner("Drafting summary…"):
                            reply = (
                                gen_synthesis_intro(ollama_url, plan, s.llm_messages)
                                if use_ollama else
                                f"I've built a {plan.get('workflow_title','')} plan with "
                                f"{len(plan['skill_chain'])} skills. Review and approve below."
                            )
                    st.markdown(reply)
                add_msg("assistant", reply)
                add_llm("assistant", reply)

            st.rerun()

        # ── reviewing → text approval ─────────────────────────────────────────
        elif s.phase == "reviewing":
            lower = user_input.lower()
            if any(w in lower for w in ["yes","approve","ok","proceed","run","go","confirm","execute"]):
                s.phase = "executing"
            elif any(w in lower for w in ["no","cancel","stop","reset","abort","start over"]):
                reset()
            else:
                add_msg("assistant", "Use the **Approve** or **Cancel** buttons above, or type `yes` / `no`.")
            st.rerun()