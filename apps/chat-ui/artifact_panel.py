from __future__ import annotations

import json
from typing import Any

import streamlit as st


def render_artifact_panel(artifacts: list[dict[str, Any]]) -> None:
    st.subheader("Artifacts")
    if not artifacts:
        st.info("No artifacts created yet.")
        return

    selected = st.selectbox(
        "Browse artifacts",
        options=range(len(artifacts)),
        format_func=lambda i: f"{artifacts[i].get('type', 'artifact')} · {artifacts[i].get('title', 'Untitled')}",
    )
    artifact = artifacts[selected]

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("ID", value=artifact.get("id", ""), disabled=True)
        st.text_input("Type", value=artifact.get("type", ""), disabled=True)
        st.text_input("Owner", value=artifact.get("owner", ""), disabled=True)
    with col2:
        st.text_input("Version", value=artifact.get("version", "1.0.0"), disabled=True)
        st.text_input("Status", value=artifact.get("status", "draft"), disabled=True)

    st.markdown("**Relationships**")
    for rel in artifact.get("relationships", []):
        st.caption(f"{rel.get('rel')} → {rel.get('target')}")

    st.markdown("**Editable Content**")
    content_text = st.text_area("JSON content", value=json.dumps(artifact.get("content", {}), indent=2), height=260)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save revision", key=f"save-{artifact.get('id')}"):
            try:
                parsed = json.loads(content_text)
                artifact["content"] = parsed
                artifact["version"] = _bump_patch(artifact.get("version", "1.0.0"))
                artifact.setdefault("audit_events", []).append({"event": "artifact.updated", "version": artifact["version"]})
                st.success("Saved new revision.")
            except json.JSONDecodeError as exc:
                st.error(f"Invalid JSON: {exc}")
    with c2:
        if st.button("Undo", key=f"undo-{artifact.get('id')}"):
            st.warning("Undo must be handled by workspace state history.")
    with c3:
        if st.button("Show audit", key=f"audit-{artifact.get('id')}"):
            st.json(artifact.get("audit_events", []))


def _bump_patch(version: str) -> str:
    major, minor, patch = [int(part) for part in version.split(".")]
    return f"{major}.{minor}.{patch + 1}"
