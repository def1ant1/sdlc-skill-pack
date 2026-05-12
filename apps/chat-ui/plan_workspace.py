from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from core.plan_system.lifecycle import PlanLifecycleManager


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def render_plan_workspace(plan_state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render a lightweight plan editing workspace with version history."""
    st.subheader("Plan Workspace")
    manager = PlanLifecycleManager(plan_state)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("Plan ID", value=manager.plan_id, disabled=True)
    with c2:
        st.text_input("Version", value=f"v{manager.current_version}", disabled=True)
    with c3:
        st.text_input("Status", value=manager.status, disabled=True)

    title = st.text_input("Title", value=manager.title)
    objectives_text = st.text_area(
        "Objectives (one per line)",
        value="\n".join(manager.objectives),
        height=100,
    )

    phases_json = st.text_area(
        "Phases JSON",
        value=json.dumps(manager.phases, indent=2),
        height=280,
        help="Edit phases, tasks, dependencies, gates, and skills.",
    )

    assumptions_json = st.text_area(
        "Cost assumptions JSON",
        value=json.dumps(manager.cost_assumptions, indent=2),
        height=140,
    )

    action1, action2, action3 = st.columns(3)
    with action1:
        if st.button("Save revision", use_container_width=True):
            try:
                manager.update_plan(
                    title=title,
                    objectives=[line.strip() for line in objectives_text.splitlines() if line.strip()],
                    phases=json.loads(phases_json),
                    cost_assumptions=json.loads(assumptions_json),
                    edited_at=_iso_now(),
                )
                st.success(f"Saved version {manager.current_version}")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON in editor: {exc}")
    with action2:
        if st.button("Approve plan", use_container_width=True):
            manager.transition("approved")
            st.success("Plan approved")
    with action3:
        if st.button("Archive plan", use_container_width=True):
            manager.transition("archived")
            st.success("Plan archived")

    st.markdown("### Version History")
    history = manager.history
    if not history:
        st.caption("No revisions yet.")
    else:
        selected_idx = st.selectbox(
            "Revision",
            options=list(range(len(history))),
            format_func=lambda i: f"v{history[i]['version']} · {history[i]['event']} · {history[i]['timestamp']}",
        )
        selected = history[selected_idx]
        st.json(selected)

        if selected.get("snapshot"):
            with st.expander("Revision snapshot", expanded=False):
                st.json(selected["snapshot"])

    return copy.deepcopy(manager.data)
