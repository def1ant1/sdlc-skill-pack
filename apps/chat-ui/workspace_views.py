from __future__ import annotations

import json
import streamlit as st


def render_workspace_actions(workspace_state: dict) -> None:
    st.markdown("### Workspace State")
    if st.button("Inspect Workspace", use_container_width=True):
        st.session_state.panel_artifact = {"workspace_state": workspace_state}
        st.session_state.panel_tab = "history"
    st.download_button(
        "Export Workspace",
        data=json.dumps(workspace_state, indent=2),
        file_name="workspace-state.json",
        mime="application/json",
        use_container_width=True,
    )
