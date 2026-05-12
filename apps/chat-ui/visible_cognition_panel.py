from __future__ import annotations

from typing import Any

import streamlit as st


def _default_working_state() -> dict[str, Any]:
    return {
        "goal": "",
        "assumptions": [],
        "constraints": [],
        "risks": [],
        "open_questions": [],
        "next_actions": [],
    }


def _parse_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _parse_assumptions(value: str) -> list[dict[str, Any]]:
    assumptions: list[dict[str, Any]] = []
    for line in _parse_lines(value):
        parts = [part.strip() for part in line.split("|")]
        text = parts[0] if parts else ""
        source = parts[1] if len(parts) > 1 and parts[1] else "unspecified"
        confidence = parts[2] if len(parts) > 2 and parts[2] else "medium"
        provided = parts[3].lower() if len(parts) > 3 else "inferred"
        assumptions.append(
            {
                "text": text,
                "source": source,
                "confidence": confidence,
                "status": "user_provided" if provided in {"user", "user_provided"} else "inferred",
            }
        )
    return assumptions


def _assumptions_to_text(items: list[dict[str, Any]]) -> str:
    lines = []
    for item in items:
        lines.append(
            " | ".join(
                [
                    item.get("text", ""),
                    item.get("source", "unspecified"),
                    item.get("confidence", "medium"),
                    item.get("status", "inferred"),
                ]
            )
        )
    return "\n".join(lines)


def render_visible_cognition_panel(current: dict[str, Any] | None = None) -> tuple[dict[str, Any], bool]:
    state = _default_working_state()
    if isinstance(current, dict):
        state.update(current)

    st.markdown("### Visible Cognition")
    st.caption("Editable planning trace. Assumptions format: text | source | confidence | user_provided|inferred")

    goal = st.text_input("Goal", value=state.get("goal", ""), key="vc_goal")
    assumptions_raw = st.text_area(
        "Assumptions",
        value=_assumptions_to_text(state.get("assumptions", [])),
        height=140,
        key="vc_assumptions",
    )
    constraints_raw = st.text_area(
        "Constraints (one per line)",
        value="\n".join(state.get("constraints", [])),
        height=100,
        key="vc_constraints",
    )
    risks_raw = st.text_area("Risks (one per line)", value="\n".join(state.get("risks", [])), height=100, key="vc_risks")
    open_q_raw = st.text_area(
        "Open Questions (one per line)",
        value="\n".join(state.get("open_questions", [])),
        height=100,
        key="vc_open_questions",
    )
    next_actions_raw = st.text_area(
        "Next Actions (one per line)",
        value="\n".join(state.get("next_actions", [])),
        height=100,
        key="vc_next_actions",
    )

    updated = {
        "goal": goal.strip(),
        "assumptions": _parse_assumptions(assumptions_raw),
        "constraints": _parse_lines(constraints_raw),
        "risks": _parse_lines(risks_raw),
        "open_questions": _parse_lines(open_q_raw),
        "next_actions": _parse_lines(next_actions_raw),
    }
    changed = updated != state
    return updated, changed
