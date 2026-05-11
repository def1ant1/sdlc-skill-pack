from __future__ import annotations

import streamlit as st

from scripts.api.apotheon_api import (
    get_app_health,
    get_cost_status,
    get_rate_limit_status,
    get_schedule_registry,
    list_oldfarmtrucks_templates,
    load_oldfarmtrucks_template,
    submit_objective,
)

st.set_page_config(page_title="Apotheon Chat UI MVP", layout="wide")
st.title("Apotheon Chat UI MVP")
st.caption("Safe-by-default planning console with dry-run only execution unless explicit operator approval is granted.")

with st.sidebar:
    st.header("Execution safety")
    approval_flow_enabled = st.checkbox("I acknowledge live-write risk and want to enable approval flow", value=False)
    approval_token = st.text_input("Approval ticket/reference", placeholder="e.g., CAB-2026-0511")
    live_writes_allowed = approval_flow_enabled and bool(approval_token.strip())
    if live_writes_allowed:
        st.success("Approval flow satisfied. Live writes can be enabled by downstream runtime systems.")
    else:
        st.warning("Live writes are blocked by default until explicit approval flow is satisfied.")

st.subheader("1) Submit objective")
planner = st.selectbox("Domain planner", ["business", "customer", "finance", "gtm", "inventory", "legal", "data-security"])
objective = st.text_area("Objective", placeholder="Describe the business objective to plan.")

if st.button("Generate plan", type="primary", use_container_width=True):
    if not objective.strip():
        st.error("Please provide an objective.")
    else:
        result = submit_objective(objective=objective, planner=planner)
        if not result.ok:
            st.error("Planner failed.")
            st.code(result.stderr or "No stderr available")
        else:
            st.success("Plan generated successfully (dry-run).")
            st.json(result.plan)
            st.caption(f"Command: {' '.join(result.command or [])}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("2) OldFarmTrucks template import")
    template_names = list_oldfarmtrucks_templates()
    selected_template = st.selectbox("Template", template_names)
    if st.button("Import template", use_container_width=True):
        template = load_oldfarmtrucks_template(selected_template)
        st.success(f"Imported {selected_template}")
        st.json(template)

with col2:
    st.subheader("3) Schedules")
    st.code(get_schedule_registry(), language="yaml")

st.subheader("4) Runtime status")
status_col1, status_col2, status_col3 = st.columns(3)
with status_col1:
    st.markdown("**App health**")
    st.json(get_app_health())
with status_col2:
    st.markdown("**Cost estimates & warnings**")
    st.json(get_cost_status())
with status_col3:
    st.markdown("**Rate-limit warnings**")
    st.json(get_rate_limit_status())

st.subheader("5) Approvals")
st.info(
    "Approval state is managed as explicit operator intent: checkbox + non-empty ticket. "
    "Without both, UI remains in safe mode and blocks live writes."
)

if live_writes_allowed:
    st.success("Current mode: approval-ready")
else:
    st.error("Current mode: read-only / dry-run")
