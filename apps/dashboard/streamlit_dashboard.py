"""
Apotheon Control Plane Dashboard — multi-tab operator console.

Tabs: Overview · Workflows · HITL Queue · Telemetry · Schedules · Settings

Data sources (in priority order):
  1. FastAPI runtime (JWT required) — live DB data
  2. Local JSON/YAML files          — always available
  3. Direct service TCP/HTTP probes — no auth required

All configuration stored in reports/dashboard_config.json.
"""
from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

ROOT           = Path(__file__).resolve().parents[2]
REPORTS_DIR    = ROOT / "reports"
SCHEDULES_PATH = ROOT / "schedules" / "registry.yaml"
CONFIG_PATH    = REPORTS_DIR / "dashboard_config.json"
STATE_PATH     = REPORTS_DIR / "dashboard_state.json"

# ─────────────────────────────────────────────────────────────────────────────
# Config persistence
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG: dict[str, Any] = {
    "api_url":       os.environ.get("APOTHEON_API_URL", "http://runtime:8000"),
    "jwt_token":     "",
    "ollama_url":    os.environ.get("OLLAMA_URL",       "http://ollama:11434"),
    "ollama_model":  os.environ.get("OLLAMA_MODEL",     "qwen3:4b"),
    "postgres_host": "postgres",
    "postgres_port": 5432,
    "redis_host":    "redis",
    "redis_port":    6379,
    "qdrant_url":    os.environ.get("QDRANT_URL",       "http://qdrant:6333"),
    "temporal_host": "temporal",
    "temporal_port": 7233,
    "refresh_secs":  30,
    "page_size":     20,
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {**DEFAULT_CONFIG, **stored}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# HTTP / TCP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _http(url: str, method: str = "GET", data: Any = None,
          token: str = "", timeout: int = 5) -> tuple[int, Any]:
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
            detail = {"error": exc.reason, "status": exc.code}
        return exc.code, detail
    except Exception as exc:
        return 0, {"error": str(exc)}


def tcp_ok(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        s = socket.socket()
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception:
        return False


def http_ok(url: str, timeout: int = 3) -> bool:
    code, _ = _http(url, timeout=timeout)
    return 200 <= code < 400

# ─────────────────────────────────────────────────────────────────────────────
# API callers
# ─────────────────────────────────────────────────────────────────────────────

def api(cfg: dict, path: str, method: str = "GET",
        data: Any = None, params: str = "") -> tuple[bool, Any]:
    """Call runtime API. Returns (success, payload)."""
    url = f"{cfg['api_url']}{path}{params}"
    code, resp = _http(url, method=method, data=data, token=cfg["jwt_token"], timeout=10)
    return (200 <= code < 300), resp


def api_workflows(cfg: dict, limit: int = 50, offset: int = 0) -> list[dict]:
    ok, resp = api(cfg, "/v1/workflows", params=f"?limit={limit}&offset={offset}")
    return resp if ok and isinstance(resp, list) else []


def api_workflow_detail(cfg: dict, run_id: str) -> dict | None:
    ok, resp = api(cfg, f"/v1/workflows/{run_id}")
    return resp if ok else None


def api_cancel_workflow(cfg: dict, run_id: str) -> bool:
    ok, _ = api(cfg, f"/v1/workflows/{run_id}/cancel", method="POST")
    return ok


def api_approvals(cfg: dict) -> list[dict]:
    ok, resp = api(cfg, "/v1/approvals")
    return resp if ok and isinstance(resp, list) else []


def api_decide(cfg: dict, approval_id: str, decision: str, reason: str = "") -> bool:
    ok, _ = api(cfg, f"/v1/approvals/{approval_id}/decide", method="POST",
                data={"decision": decision, "reason": reason})
    return ok


def api_audit_events(cfg: dict, limit: int = 100, run_id: str = "",
                     actor: str = "", action: str = "") -> list[dict]:
    params = f"?limit={limit}"
    if run_id:  params += f"&run_id={run_id}"
    if actor:   params += f"&actor={actor}"
    if action:  params += f"&action={action}"
    ok, resp = api(cfg, "/v1/telemetry/events", params=params)
    return resp if ok and isinstance(resp, list) else []


def api_token_usage(cfg: dict, limit: int = 100) -> list[dict]:
    ok, resp = api(cfg, "/v1/telemetry/token-usage", params=f"?limit={limit}")
    return resp if ok and isinstance(resp, list) else []


def api_governance(cfg: dict) -> dict:
    ok, resp = api(cfg, "/v1/governance/dashboard")
    return resp if ok and isinstance(resp, dict) else {}


def api_policies(cfg: dict) -> list[dict]:
    ok, resp = api(cfg, "/v1/governance/policies")
    return resp if ok and isinstance(resp, list) else []


def api_health(cfg: dict) -> dict:
    ok, resp = api(cfg, "/health")
    return resp if ok else {}

# ─────────────────────────────────────────────────────────────────────────────
# Local file loaders
# ─────────────────────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict | list | None:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def load_local_plans() -> list[dict]:
    """Load saved plan JSON files from reports/."""
    plans = []
    for p in sorted(REPORTS_DIR.glob("plan-*.json"), reverse=True):
        try:
            plan = json.loads(p.read_text(encoding="utf-8"))
            plan["_source"] = "local"
            plan["_file"] = p.name
            plans.append(plan)
        except Exception:
            pass
    return plans


def load_schedules() -> list[dict]:
    if not SCHEDULES_PATH.exists():
        return []
    try:
        data = yaml.safe_load(SCHEDULES_PATH.read_text(encoding="utf-8"))
        return data.get("schedules", []) if isinstance(data, dict) else []
    except Exception:
        return []


def save_schedules(schedules: list[dict]) -> None:
    SCHEDULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULES_PATH.write_text(yaml.dump({"schedules": schedules}, default_flow_style=False),
                              encoding="utf-8")


def load_state() -> dict:
    d = load_json(STATE_PATH)
    return d if isinstance(d, dict) else {}


def save_state(state: dict) -> None:
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Service health probes
# ─────────────────────────────────────────────────────────────────────────────

def probe_services(cfg: dict) -> dict[str, dict]:
    services: dict[str, dict] = {}

    def _svc(name: str, up: bool, detail: str = "") -> None:
        services[name] = {"up": up, "detail": detail,
                          "label": "healthy" if up else "offline"}

    _svc("PostgreSQL", tcp_ok(cfg["postgres_host"], cfg["postgres_port"]),
         f"{cfg['postgres_host']}:{cfg['postgres_port']}")
    _svc("Redis",      tcp_ok(cfg["redis_host"], cfg["redis_port"]),
         f"{cfg['redis_host']}:{cfg['redis_port']}")
    _svc("Temporal",   tcp_ok(cfg["temporal_host"], cfg["temporal_port"]),
         f"{cfg['temporal_host']}:{cfg['temporal_port']}")
    _svc("Qdrant",     http_ok(f"{cfg['qdrant_url']}/readyz"),
         cfg["qdrant_url"])
    _svc("Ollama",     http_ok(f"{cfg['ollama_url']}/api/tags"),
         cfg["ollama_url"])
    _svc("Runtime API",http_ok(f"{cfg['api_url']}/health"),
         cfg["api_url"])

    return services

# ─────────────────────────────────────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────────────────────────────────────

STATUS_COLOR = {
    "queued": "blue", "running": "orange", "done": "green",
    "completed": "green", "failed": "red", "cancelled": "gray",
    "paused_for_hitl": "violet", "pending": "orange",
    "approved": "green", "rejected": "red", "dry_run_saved": "gray",
}

def _badge(status: str) -> str:
    color = STATUS_COLOR.get(status.lower(), "gray")
    return f":{color}[{status}]"


def _ts(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso[:16]


def _ago(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - dt
        s = int(diff.total_seconds())
        if s < 60:   return f"{s}s ago"
        if s < 3600: return f"{s//60}m ago"
        if s < 86400:return f"{s//3600}h ago"
        return f"{s//86400}d ago"
    except Exception:
        return iso[:16]

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

def _init() -> None:
    if "cfg" not in st.session_state:
        st.session_state.cfg = load_config()
    if "selected_run" not in st.session_state:
        st.session_state.selected_run = None
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = 0.0

# ─────────────────────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Apotheon Control Plane",
    layout="wide",
    initial_sidebar_state="expanded",
)

_init()
cfg = st.session_state.cfg

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Control Plane")
    st.caption("Apotheon operator console")
    st.divider()

    # Connection status
    _api_up = http_ok(f"{cfg['api_url']}/health")
    if _api_up:
        st.success("Runtime API connected", icon="✅")
    else:
        st.warning("Runtime API offline — showing local data", icon="⚠️")

    has_jwt = bool(cfg.get("jwt_token", "").strip())
    if _api_up and not has_jwt:
        st.info("Set JWT token in **Settings** to enable live data.", icon="🔑")

    st.divider()

    # Refresh
    if st.button("Refresh now", use_container_width=True):
        st.session_state.last_refresh = 0.0
        st.rerun()

    last = st.session_state.last_refresh
    if last:
        st.caption(f"Last refresh: {_ago(datetime.fromtimestamp(last, tz=timezone.utc).isoformat())}")

    st.divider()

    # Quick nav
    if st.button("Clear selected workflow", use_container_width=True):
        st.session_state.selected_run = None
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────────────────

t_overview, t_workflows, t_hitl, t_telemetry, t_schedules, t_settings = st.tabs([
    "Overview", "Workflows", "HITL Queue", "Telemetry", "Schedules", "Settings"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════

with t_overview:
    st.subheader("System overview")

    # KPI row — pull live data where possible, fallback to state file
    state = load_state()
    workflows_live = api_workflows(cfg, limit=200) if (_api_up and has_jwt) else []
    approvals_live = api_approvals(cfg) if (_api_up and has_jwt) else []
    governance_live = api_governance(cfg) if (_api_up and has_jwt) else {}

    active_count   = sum(1 for w in workflows_live if w.get("status") in ("queued","running","paused_for_hitl")) if workflows_live else state.get("workflow_progress", {}).get("active", "—")
    done_count     = sum(1 for w in workflows_live if w.get("status") in ("done","completed")) if workflows_live else state.get("workflow_progress", {}).get("completed_today", "—")
    pending_approvals = len([a for a in approvals_live if a.get("status") == "pending"]) if approvals_live else state.get("approvals_summary", {}).get("pending", "—")
    budget_burn    = state.get("budgets", {}).get("month_to_date_burn_usd", "—")
    rate_events    = state.get("rate_limits", {}).get("violations_24h", "—")
    total_runs     = len(workflows_live) if workflows_live else "—"

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Active workflows", active_count)
    k2.metric("Completed", done_count)
    k3.metric("Pending HITL", pending_approvals)
    k4.metric("Total runs", total_runs)
    k5.metric("Budget burn (MTD)", f"${budget_burn:,}" if isinstance(budget_burn, (int, float)) else budget_burn)
    k6.metric("Rate limit events", rate_events)

    st.divider()

    # Service health grid
    st.subheader("Infrastructure health")
    with st.spinner("Probing services…"):
        services = probe_services(cfg)

    s_cols = st.columns(len(services))
    for col, (name, info) in zip(s_cols, services.items()):
        color = "green" if info["up"] else "red"
        col.markdown(f":{color}[●] **{name}**")
        col.caption(info["detail"])

    st.divider()

    col_left, col_right = st.columns(2)

    # Workflow status breakdown
    with col_left:
        st.subheader("Workflow status")
        if workflows_live:
            from collections import Counter
            counts = Counter(w.get("status", "unknown") for w in workflows_live)
            for status, n in sorted(counts.items(), key=lambda x: -x[1]):
                color = STATUS_COLOR.get(status, "gray")
                st.markdown(f":{color}[●] **{status}** — {n}")
        else:
            wp = state.get("workflow_progress", {})
            st.markdown(f"- Active: **{wp.get('active','—')}**")
            st.markdown(f"- Completed today: **{wp.get('completed_today','—')}**")
            st.markdown(f"- Completion: **{wp.get('completion_pct','—')}%**")
            st.caption("Live data requires JWT in Settings.")

        # Local plans summary
        local_plans = load_local_plans()
        if local_plans:
            st.divider()
            st.subheader(f"Saved plans ({len(local_plans)})")
            for p in local_plans[:5]:
                with st.container(border=True):
                    st.markdown(f"**{p.get('workflow_title', p.get('id','—'))}**")
                    st.caption(f"{p.get('objective','')[:80]}")
                    cols = p.get("domains", [])
                    st.caption("Domains: " + ", ".join(cols) if cols else "")

    # Memory + connectors
    with col_right:
        st.subheader("Memory & connectors")
        mem = state.get("memory", {})
        tele = state.get("telemetry", {})
        connectors = state.get("connectors", {})

        mc1, mc2 = st.columns(2)
        mc1.metric("Memory health", mem.get("health", "—"))
        mc1.metric("Embedding coverage", f"{mem.get('collection_coverage_pct','—')}%")
        mc2.metric("Telemetry events (24h)", tele.get("events_24h", "—"))
        mc2.metric("Errors (24h)", tele.get("errors_24h", "—"))

        st.markdown("**Connectors**")
        st.markdown(f"- Healthy: {connectors.get('healthy','—')}")
        st.markdown(f"- Degraded: {connectors.get('degraded','—')}")
        st.markdown(f"- Down: {connectors.get('down','—')}")

        if governance_live:
            st.divider()
            st.subheader("Governance")
            st.metric("Pending approvals (API)", governance_live.get("pending_approvals", "—"))
            violations = governance_live.get("policy_violations", [])
            if violations:
                st.markdown("**Policy violations:**")
                for v in violations[:5]:
                    st.markdown(f"- Policy `{v['policy_id']}`: {v['count']} hit(s)")

    # Rate limits + budget
    st.divider()
    b_cols = st.columns(3)
    budgets = state.get("budgets", {})
    rl = state.get("rate_limits", {})
    b_cols[0].metric("Monthly budget", f"${budgets.get('monthly_budget_usd',0):,}")
    b_cols[1].metric("MTD burn",        f"${budgets.get('month_to_date_burn_usd',0):,}")
    b_cols[2].metric("Forecast (EOM)",  f"${budgets.get('forecast_month_end_usd',0):,}")

    b_cols2 = st.columns(3)
    b_cols2[0].metric("Rate violations (24h)",   rl.get("violations_24h","—"))
    b_cols2[1].metric("Throttled requests (24h)", rl.get("throttled_requests_24h","—"))
    b_cols2[2].metric("Peak utilisation",         f"{rl.get('highest_utilization_pct','—')}%")

    st.caption(f"State file: {_ago(state.get('last_updated'))} | API: {'connected' if _api_up else 'offline'} | JWT: {'set' if has_jwt else 'not set'}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — WORKFLOWS
# ═════════════════════════════════════════════════════════════════════════════

with t_workflows:

    # If a run is selected, show detail view
    if st.session_state.selected_run:
        run_id = st.session_state.selected_run

        if st.button("← Back to list"):
            st.session_state.selected_run = None
            st.rerun()

        st.subheader(f"Workflow: `{run_id}`")

        detail = api_workflow_detail(cfg, run_id) if (_api_up and has_jwt) else None
        if detail:
            # Header metrics
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Status", detail.get("status","—"))
            d2.metric("Total steps", detail.get("total_steps","—"))
            d3.metric("Completed steps", detail.get("completed_steps","—"))
            d4.metric("Mode", detail.get("mode","—"))

            st.markdown(f"**Objective:** {detail.get('objective','—')}")
            st.markdown(f"**Started:** {_ts(detail.get('started_at'))}  |  **Completed:** {_ts(detail.get('completed_at'))}")

            # Steps
            steps = detail.get("steps", [])
            if steps:
                st.markdown("---")
                st.subheader("Execution steps")
                for step in steps:
                    color = STATUS_COLOR.get(step.get("status",""), "gray")
                    with st.expander(
                        f"Step {step['step']} — `{step['skill']}` — :{color}[{step.get('status','?')}]",
                        expanded=step.get("status") in ("failed","paused_for_hitl"),
                    ):
                        sc1, sc2, sc3 = st.columns(3)
                        sc1.markdown(f"**Duration:** {step.get('duration_ms','—')} ms")
                        sc2.markdown(f"**HITL required:** {'Yes' if step.get('hitl_required') else 'No'}")
                        sc3.markdown(f"**Status:** {step.get('status','—')}")
                        if step.get("output_preview"):
                            st.markdown("**Output preview:**")
                            st.code(step["output_preview"], language="text")
                        if step.get("error"):
                            st.error(step["error"])

            # Actions
            st.markdown("---")
            act_cols = st.columns(3)
            if detail.get("status") in ("queued","running","paused_for_hitl"):
                if act_cols[0].button("Cancel workflow", type="secondary", key=f"cancel_{run_id}"):
                    if api_cancel_workflow(cfg, run_id):
                        st.success(f"Run {run_id} cancelled.")
                        st.rerun()
                    else:
                        st.error("Cancel failed.")

            with st.expander("Full run JSON"):
                st.json(detail)

        else:
            # Try local plan files
            local_plans = load_local_plans()
            match = next((p for p in local_plans if run_id in p.get("id","") or run_id in p.get("_file","")), None)
            if match:
                st.info("Showing locally saved plan (API offline or no JWT).")
                _render_local_plan(match) if False else None  # placeholder
                st.json(match)
            else:
                st.warning(f"Run `{run_id}` not found. API may be offline or JWT not set.")

    else:
        # Workflow list
        st.subheader("Workflow runs")

        # Filters
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        status_filter = fc1.selectbox("Filter by status", ["all","queued","running","done","completed","failed","cancelled","paused_for_hitl"], key="wf_status_filter")
        search_q      = fc2.text_input("Search objective", placeholder="keyword…", key="wf_search")
        page_size     = fc3.number_input("Per page", min_value=5, max_value=100, value=cfg.get("page_size",20), key="wf_page_size")

        # Load from API or local
        if _api_up and has_jwt:
            runs = api_workflows(cfg, limit=200)
        else:
            # Use locally saved plans as surrogate workflow records
            plans = load_local_plans()
            runs = [
                {
                    "run_id":     p.get("id","—"),
                    "objective":  p.get("objective","—"),
                    "status":     "dry_run_saved",
                    "mode":       "local",
                    "total_steps":len(p.get("skill_chain",[])),
                    "created_at": p.get("planner_metadata",{}).get("created_at"),
                    "_source":    "local",
                    "_plan":      p,
                }
                for p in plans
            ]

        # Apply filters
        if status_filter != "all":
            runs = [r for r in runs if r.get("status") == status_filter]
        if search_q:
            runs = [r for r in runs if search_q.lower() in (r.get("objective","") + r.get("run_id","")).lower()]

        st.caption(f"{len(runs)} run{'s' if len(runs) != 1 else ''} {'(from API)' if (_api_up and has_jwt) else '(local plans only — set JWT for live data)'}")

        if not runs:
            st.info("No workflow runs found. Submit a plan from the Chat UI to create one.")
        else:
            # Table header
            th = st.columns([3, 1, 1, 1, 1, 1])
            th[0].markdown("**Objective**")
            th[1].markdown("**Status**")
            th[2].markdown("**Steps**")
            th[3].markdown("**Mode**")
            th[4].markdown("**Created**")
            th[5].markdown("**Action**")

            st.divider()

            for run in runs[:page_size]:
                row = st.columns([3, 1, 1, 1, 1, 1])
                objective = (run.get("objective") or "—")[:60]
                status    = run.get("status","—")
                color     = STATUS_COLOR.get(status,"gray")

                row[0].markdown(f"{objective}{'…' if len(run.get('objective','')) > 60 else ''}")
                row[1].markdown(f":{color}[{status}]")
                row[2].markdown(str(run.get("total_steps","—")))
                row[3].markdown(run.get("mode","—"))
                row[4].markdown(_ago(run.get("created_at")))

                run_id = run.get("run_id","")
                if run_id and row[5].button("View", key=f"view_{run_id}"):
                    st.session_state.selected_run = run_id
                    st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — HITL QUEUE
# ═════════════════════════════════════════════════════════════════════════════

with t_hitl:
    st.subheader("Human-in-the-loop approval queue")

    if not (_api_up and has_jwt):
        st.warning("HITL queue requires the Runtime API + JWT token. Configure in Settings.", icon="🔑")

        # Fallback: show local HITL items from state file
        state = load_state()
        local_approvals = state.get("approvals", [])
        if local_approvals:
            st.info(f"Showing {len(local_approvals)} approval(s) from local state file (read-only).")
            for item in local_approvals:
                with st.container(border=True):
                    ac = st.columns([2, 1, 1, 2])
                    ac[0].markdown(f"**{item.get('id','—')}** — `{item.get('workflow','—')}`")
                    ac[1].markdown(_badge(item.get("status","—")))
                    ac[2].markdown(_ago(item.get("requested_at")))
                    ac[3].markdown(f"Status: **{item.get('status','—')}**")
        else:
            st.info("No pending approvals in local state file.")
    else:
        approvals = api_approvals(cfg)
        pending = [a for a in approvals if a.get("status") == "pending"]

        if not pending:
            st.success("No pending approvals.", icon="✅")
        else:
            st.warning(f"{len(pending)} approval(s) waiting for decision.", icon="⚠️")

        for item in pending:
            risk = item.get("risk_level","medium")
            risk_color = {"high":"red","critical":"red","medium":"orange","low":"blue"}.get(risk,"gray")

            with st.container(border=True):
                st.markdown(f"**Approval `{item.get('approval_id','—')}`** — Run `{item.get('run_id','—')}`")

                hc = st.columns([2, 1, 1, 1])
                hc[0].markdown(f"**Skill:** `{item.get('skill_name','—')}`")
                hc[1].markdown(f"**Risk:** :{risk_color}[{risk}]")
                hc[2].markdown(f"**Score:** {item.get('risk_score','—')}")
                hc[3].markdown(f"**SLA:** {_ts(item.get('sla_deadline'))}")

                if item.get("hitl_reason"):
                    st.info(item["hitl_reason"])

                approval_id = item.get("approval_id","")
                reason_key  = f"reason_{approval_id}"
                reason = st.text_input("Reason (optional)", key=reason_key, placeholder="e.g. reviewed and confirmed")

                btn_cols = st.columns([1, 1, 3])
                if btn_cols[0].button("Approve", type="primary", key=f"app_{approval_id}"):
                    if api_decide(cfg, approval_id, "approved", st.session_state.get(reason_key,"")):
                        st.success(f"Approved `{approval_id}`")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Approval failed.")

                if btn_cols[1].button("Reject", type="secondary", key=f"rej_{approval_id}"):
                    if api_decide(cfg, approval_id, "rejected", st.session_state.get(reason_key,"")):
                        st.warning(f"Rejected `{approval_id}`")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Rejection failed.")

        # Governance dashboard from API
        if _api_up and has_jwt:
            gov = api_governance(cfg)
            hitl_rates = gov.get("hitl_rates_by_skill", [])
            if hitl_rates:
                st.divider()
                st.subheader("HITL rate by skill")
                for hr in sorted(hitl_rates, key=lambda x: -x.get("hitl_rate",0))[:15]:
                    rate_pct = int(hr.get("hitl_rate",0) * 100)
                    bar = "█" * (rate_pct // 5) + "░" * (20 - rate_pct // 5)
                    st.markdown(
                        f"`{hr['skill_name']}` — {rate_pct}% HITL rate "
                        f"({hr.get('hitl_count',0)}/{hr.get('total_executions',0)} runs)  \n"
                        f"`{bar}`"
                    )

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — TELEMETRY
# ═════════════════════════════════════════════════════════════════════════════

with t_telemetry:
    tele_tab1, tele_tab2, tele_tab3 = st.tabs(["Audit Log", "Token Usage", "Governance Policies"])

    # ── Audit Log ─────────────────────────────────────────────────────────────
    with tele_tab1:
        st.subheader("Audit log")
        if not (_api_up and has_jwt):
            st.warning("Audit log requires Runtime API + JWT token.", icon="🔑")
        else:
            af1, af2, af3, af4 = st.columns(4)
            a_limit  = af1.number_input("Limit", 10, 500, 100, key="a_limit")
            a_run    = af2.text_input("Run ID filter", key="a_run")
            a_actor  = af3.text_input("Actor filter", key="a_actor")
            a_action = af4.selectbox("Action", ["","submitted","approved","rejected","cancelled"], key="a_action")

            events = api_audit_events(cfg, limit=a_limit, run_id=a_run, actor=a_actor, action=a_action)
            st.caption(f"{len(events)} event(s)")

            if events:
                for e in events:
                    risk    = e.get("risk_level","")
                    outcome = e.get("outcome","")
                    c = st.columns([2,1,1,1,1,2])
                    c[0].markdown(f"`{e.get('actor','—')}`")
                    c[1].markdown(f"**{e.get('action','—')}**")
                    c[2].markdown(e.get("resource_type","—"))
                    c[3].markdown(f":{('green' if outcome=='success' else 'red') if outcome else 'gray'}[{outcome or '—'}]")
                    c[4].markdown(f":{('red' if risk in ('high','critical') else 'orange' if risk=='medium' else 'blue') if risk else 'gray'}[{risk or '—'}]")
                    c[5].markdown(_ago(e.get("occurred_at")))
            else:
                st.info("No events found.")

    # ── Token Usage ───────────────────────────────────────────────────────────
    with tele_tab2:
        st.subheader("Token usage")
        if not (_api_up and has_jwt):
            st.warning("Token usage requires Runtime API + JWT token.", icon="🔑")
        else:
            token_rows = api_token_usage(cfg, limit=200)
            st.caption(f"{len(token_rows)} record(s)")

            if token_rows:
                # Aggregated by skill
                from collections import defaultdict
                agg: dict[str, dict] = defaultdict(lambda: {"input":0,"output":0,"cost":0.0,"runs":0})
                for r in token_rows:
                    sk = r.get("skill_name","unknown")
                    agg[sk]["input"]  += r.get("input_tokens",0)
                    agg[sk]["output"] += r.get("output_tokens",0)
                    agg[sk]["cost"]   += r.get("estimated_cost_usd",0.0) or 0.0
                    agg[sk]["runs"]   += 1

                st.subheader("By skill (aggregated)")
                th = st.columns([3,1,1,1,1])
                th[0].markdown("**Skill**"); th[1].markdown("**Runs**")
                th[2].markdown("**Input tokens**"); th[3].markdown("**Output tokens**")
                th[4].markdown("**Est. cost (USD)**")
                st.divider()

                for sk, data in sorted(agg.items(), key=lambda x: -x[1]["cost"]):
                    rc = st.columns([3,1,1,1,1])
                    rc[0].markdown(f"`{sk}`")
                    rc[1].markdown(str(data["runs"]))
                    rc[2].markdown(f"{data['input']:,}")
                    rc[3].markdown(f"{data['output']:,}")
                    rc[4].markdown(f"${data['cost']:.4f}")

                with st.expander("Raw records"):
                    st.json(token_rows[:50])
            else:
                st.info("No token usage records yet.")

    # ── Governance Policies ───────────────────────────────────────────────────
    with tele_tab3:
        st.subheader("Active governance policies")
        if not (_api_up and has_jwt):
            st.warning("Policies require Runtime API + JWT token.", icon="🔑")
        else:
            policies = api_policies(cfg)
            if not policies:
                st.info("No active policies found.")
            else:
                for p in policies:
                    action_color = {"BLOCK":"red","WARN":"orange","REQUIRE_APPROVAL":"violet"}.get(p.get("action",""),"gray")
                    with st.expander(f"**{p.get('name','—')}** — :{action_color}[{p.get('action','—')}]"):
                        pc = st.columns(3)
                        pc[0].markdown(f"**Scope:** `{p.get('scope_pattern','*')}`")
                        pc[1].markdown(f"**Immutable:** {'Yes' if p.get('is_immutable') else 'No'}")
                        pc[2].markdown(f"**Created:** {_ts(p.get('created_at'))}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — SCHEDULES
# ═════════════════════════════════════════════════════════════════════════════

with t_schedules:
    st.subheader("Schedule registry")
    st.caption(f"Source: `{SCHEDULES_PATH.relative_to(ROOT)}`")

    schedules = load_schedules()

    if not schedules:
        st.warning("No schedules found in `schedules/registry.yaml`.")
    else:
        changed = False
        st.markdown(f"**{len(schedules)} schedule(s)** defined")

        for i, sched in enumerate(schedules):
            risk  = sched.get("risk_tier","low")
            risk_color = {"high":"red","medium":"orange","low":"blue"}.get(risk,"gray")
            enabled = sched.get("enabled", True)
            mode  = sched.get("mode","—")

            with st.container(border=True):
                sc1, sc2, sc3, sc4 = st.columns([3, 1, 1, 1])

                sc1.markdown(f"**`{sched.get('schedule_id','—')}`**")
                sc1.caption(sched.get("metadata",{}).get("description",""))

                sc2.markdown(f"**Mode:** {mode}")
                if mode == "cron":
                    sc2.caption(f"Cron: `{sched.get('cron','—')}`")
                elif mode == "interval":
                    sc2.caption(f"Every {sched.get('interval_minutes','—')} min")
                elif mode == "event":
                    event = sched.get("event",{})
                    sc2.caption(f"Event: `{event.get('name','—')}`")

                sc3.markdown(f"**Risk:** :{risk_color}[{risk}]")
                sc3.markdown(f"**Owner:** {sched.get('owner','—')}")

                new_enabled = sc4.toggle(
                    "Enabled",
                    value=enabled,
                    key=f"sched_toggle_{i}",
                )
                if new_enabled != enabled:
                    schedules[i]["enabled"] = new_enabled
                    changed = True

                sc4.caption(f"Target: `{Path(sched.get('planner_target','')).name}`")

        if changed:
            save_schedules(schedules)
            st.success("Schedule registry updated.")
            st.rerun()

    st.divider()

    # Add new schedule
    with st.expander("Add schedule"):
        with st.form("new_schedule"):
            ns1, ns2 = st.columns(2)
            new_id    = ns1.text_input("Schedule ID", placeholder="daily-finance-close")
            new_mode  = ns2.selectbox("Mode", ["cron","interval","event"])
            new_cron  = st.text_input("Cron expression", placeholder="0 9 * * 1-5", help="Mode: cron only")
            new_interval = st.number_input("Interval (minutes)", min_value=1, value=60, help="Mode: interval only")
            new_target= st.text_input("Planner target", placeholder="scripts/orchestration/plan_finance_workflow.py")
            new_owner = st.text_input("Owner", placeholder="finance-ops")
            new_risk  = st.selectbox("Risk tier", ["low","medium","high"])
            new_desc  = st.text_area("Description", placeholder="What does this schedule do?")
            new_enabled_form = st.checkbox("Enabled", value=True)

            if st.form_submit_button("Add schedule"):
                if not new_id.strip() or not new_target.strip():
                    st.error("Schedule ID and target are required.")
                else:
                    entry: dict = {
                        "schedule_id": new_id.strip(),
                        "mode": new_mode,
                        "enabled": new_enabled_form,
                        "owner": new_owner.strip(),
                        "planner_target": new_target.strip(),
                        "risk_tier": new_risk,
                        "metadata": {"description": new_desc.strip()},
                    }
                    if new_mode == "cron":
                        entry["cron"] = new_cron.strip()
                    elif new_mode == "interval":
                        entry["interval_minutes"] = int(new_interval)
                    schedules.append(entry)
                    save_schedules(schedules)
                    st.success(f"Schedule `{new_id}` added.")
                    st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# TAB 6 — SETTINGS
# ═════════════════════════════════════════════════════════════════════════════

with t_settings:
    st.subheader("Configuration")
    st.caption(f"Stored in `{CONFIG_PATH.relative_to(ROOT)}`")

    with st.form("settings_form"):
        st.markdown("### Runtime API")
        sf1, sf2 = st.columns(2)
        new_api_url  = sf1.text_input("API URL",     value=cfg.get("api_url",""))
        new_jwt      = sf2.text_input("JWT token",   value=cfg.get("jwt_token",""), type="password",
                                      help="Bearer token for API authentication. Obtain from `apotheon init` or your auth system.")

        st.markdown("### Local LLM (Ollama)")
        ol1, ol2 = st.columns(2)
        new_ollama_url   = ol1.text_input("Ollama URL",   value=cfg.get("ollama_url",""))
        new_ollama_model = ol2.text_input("Ollama model", value=cfg.get("ollama_model",""))

        st.markdown("### Infrastructure endpoints")
        inf1, inf2, inf3 = st.columns(3)
        new_pg_host   = inf1.text_input("Postgres host", value=cfg.get("postgres_host","postgres"))
        new_pg_port   = inf1.number_input("Postgres port", value=int(cfg.get("postgres_port",5432)))
        new_redis_host= inf2.text_input("Redis host",    value=cfg.get("redis_host","redis"))
        new_redis_port= inf2.number_input("Redis port",  value=int(cfg.get("redis_port",6379)))
        new_qdrant_url= inf3.text_input("Qdrant URL",   value=cfg.get("qdrant_url","http://qdrant:6333"))
        new_temp_host = inf3.text_input("Temporal host", value=cfg.get("temporal_host","temporal"))
        new_temp_port = inf3.number_input("Temporal port",value=int(cfg.get("temporal_port",7233)))

        st.markdown("### Display")
        dp1, dp2 = st.columns(2)
        new_page_size   = dp1.number_input("Workflow page size", min_value=5, max_value=100, value=int(cfg.get("page_size",20)))

        submitted = st.form_submit_button("Save settings", type="primary")
        if submitted:
            new_cfg = {
                "api_url":       new_api_url.strip(),
                "jwt_token":     new_jwt.strip(),
                "ollama_url":    new_ollama_url.strip(),
                "ollama_model":  new_ollama_model.strip(),
                "postgres_host": new_pg_host.strip(),
                "postgres_port": int(new_pg_port),
                "redis_host":    new_redis_host.strip(),
                "redis_port":    int(new_redis_port),
                "qdrant_url":    new_qdrant_url.strip(),
                "temporal_host": new_temp_host.strip(),
                "temporal_port": int(new_temp_port),
                "page_size":     int(new_page_size),
            }
            save_config(new_cfg)
            st.session_state.cfg = new_cfg
            st.success("Settings saved.")
            st.rerun()

    # Connection test
    st.divider()
    st.markdown("### Connection test")
    if st.button("Test all connections"):
        with st.spinner("Testing…"):
            results = probe_services(cfg)
            # Also test JWT
            if cfg.get("jwt_token") and cfg.get("api_url"):
                ok, resp = api(cfg, "/v1/workflows", params="?limit=1")
                results["API (auth)"] = {
                    "up": ok,
                    "detail": "JWT valid" if ok else str(resp.get("error","auth failed")),
                    "label": "authenticated" if ok else "auth failed",
                }
        for name, info in results.items():
            color = "green" if info["up"] else "red"
            st.markdown(f":{color}[●] **{name}** — {info['detail']} ({info['label']})")

    # Environment viewer
    st.divider()
    st.markdown("### Environment variables")
    env_keys = [
        "APOTHEON_API_URL","OLLAMA_URL","OLLAMA_MODEL","ANTHROPIC_API_KEY",
        "DATABASE_URL","REDIS_URL","QDRANT_URL","TEMPORAL_HOST",
        "TEMPORAL_NAMESPACE","JWT_SECRET","LOG_LEVEL","EXECUTION_MODE",
    ]
    for k in env_keys:
        v = os.environ.get(k)
        if v:
            masked = v if k not in ("ANTHROPIC_API_KEY","JWT_SECRET") else v[:4] + "***"
            st.code(f"{k}={masked}")
        else:
            st.markdown(f"- `{k}` — _not set_")

    # Reports file explorer
    st.divider()
    st.markdown("### Report files")
    report_files = sorted(REPORTS_DIR.glob("*.json"), reverse=True)
    st.caption(f"{len(report_files)} JSON files in `reports/`")
    selected_report = st.selectbox("View report file", [f.name for f in report_files], key="report_sel")
    if selected_report:
        rpath = REPORTS_DIR / selected_report
        if rpath.exists():
            data = load_json(rpath)
            if data is not None:
                st.json(data, expanded=False)
            else:
                st.error("Could not parse file.")
