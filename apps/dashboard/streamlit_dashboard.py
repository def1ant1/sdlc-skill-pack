from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "reports" / "dashboard_state.json"


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"approvals": [], "last_updated": None}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


st.set_page_config(page_title="Apotheon Control Plane Dashboard", layout="wide")
st.title("Apotheon Control Plane Dashboard")
state = load_state()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Workflow Progress", f"{state['workflow_progress']['completion_pct']}%")
with k2:
    st.metric("Open Approvals", state["approvals_summary"]["pending"])
with k3:
    st.metric("Budget Burn", f"{state['budgets']['month_to_date_burn_usd']:,} USD")
with k4:
    st.metric("Rate Limit Events", state["rate_limits"]["violations_24h"])

left, right = st.columns(2)
with left:
    st.subheader("Workflow + Scheduling")
    st.json({"workflow_progress": state["workflow_progress"], "schedules": state["schedules"]})
    st.subheader("Budgets + Rate Limits")
    st.json({"budgets": state["budgets"], "rate_limits": state["rate_limits"]})
    st.subheader("Memory + Telemetry + Skill Maturity")
    st.json({"memory": state["memory"], "telemetry": state["telemetry"], "skill_maturity": state["skill_maturity"]})

with right:
    st.subheader("Connectors + Local Apps")
    st.json({"connectors": state["connectors"], "local_apps": state["local_apps"]})
    st.subheader("OldFarmTrucks Template Status")
    st.json(state["template_status"])

st.subheader("HITL Approval Queue")
rows = []
for item in state["approvals"]:
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 2])
    c1.write(item["id"])
    c2.write(item["workflow"])
    c3.write(item["status"])
    if c4.button("Approve", key=f"approve-{item['id']}"):
        item["status"] = "approved"
        item["decided_at"] = datetime.now(timezone.utc).isoformat()
        rows.append(f"Approved {item['id']}")
    if c5.button("Reject", key=f"reject-{item['id']}"):
        item["status"] = "rejected"
        item["decided_at"] = datetime.now(timezone.utc).isoformat()
        rows.append(f"Rejected {item['id']}")

if rows:
    save_state(state)
    for r in rows:
        st.success(r)

st.caption(f"Last updated: {state.get('last_updated', 'unknown')}")
