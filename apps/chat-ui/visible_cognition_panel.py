from __future__ import annotations

from typing import Any

import streamlit as st


def _default_working_state() -> dict[str, Any]:
    return {
        "goal": "",
        "selected_intent": "",
        "intent_confidence": 0.0,
        "assumptions": [],
        "constraints": [],
        "risks": [],
        "open_questions": [],
        "highest_impact_missing_datum": "",
        "next_safe_action": "",
        "rationale_trace": [],
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


def _parse_traceability(value: str) -> list[dict[str, str]]:
    trace: list[dict[str, str]] = []
    for line in _parse_lines(value):
        parts = [part.strip() for part in line.split("|")]
        rationale = parts[0] if parts else ""
        message_id = parts[1] if len(parts) > 1 and parts[1] else "unspecified"
        artifact_id = parts[2] if len(parts) > 2 and parts[2] else "unspecified"
        trace.append({"rationale": rationale, "message_id": message_id, "artifact_id": artifact_id})
    return trace


def _traceability_to_text(items: list[dict[str, str]]) -> str:
    return "\n".join(
        " | ".join([item.get("rationale", ""), item.get("message_id", "unspecified"), item.get("artifact_id", "unspecified")])
        for item in items
    )


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
    st.caption("Editable planning trace with rationale traceability.")

    goal = st.text_input("Goal", value=state.get("goal", ""), key="vc_goal")
    selected_intent = st.text_input("Selected intent", value=state.get("selected_intent", ""), key="vc_selected_intent")
    intent_confidence = st.slider(
        "Intent confidence",
        min_value=0.0,
        max_value=1.0,
        value=float(state.get("intent_confidence", 0.0) or 0.0),
        step=0.01,
        key="vc_intent_confidence",
    )
    assumptions_raw = st.text_area(
        "Assumptions",
        value=_assumptions_to_text(state.get("assumptions", [])),
        height=140,
        key="vc_assumptions",
        help="Format: text | source_message_or_artifact_id | confidence | user_provided|inferred",
    )
    constraints_raw = st.text_area(
        "Constraints (one per line)",
        value="\n".join(state.get("constraints", [])),
        height=100,
        key="vc_constraints",
    )
    risks_raw = st.text_area("Risks (one per line)", value="\n".join(state.get("risks", [])), height=100, key="vc_risks")
    open_q_raw = st.text_area(
        "Open Questions (question | reason)",
        value="\n".join(state.get("open_questions", [])),
        height=100,
        key="vc_open_questions",
        help='Reason should start with: "This changes execution safety/cost/compliance because..."',
    )
    highest_impact_missing_datum = st.text_input(
        "Highest-impact missing datum",
        value=state.get("highest_impact_missing_datum", ""),
        key="vc_highest_impact_missing_datum",
    )
    next_safe_action = st.text_input("Next safe action", value=state.get("next_safe_action", ""), key="vc_next_safe_action")
    rationale_trace_raw = st.text_area(
        "Rationale Trace (rationale | source_message_id | source_artifact_id)",
        value=_traceability_to_text(state.get("rationale_trace", [])),
        height=100,
        key="vc_rationale_trace",
    )
    next_actions_raw = st.text_area(
        "Next Actions (one per line)",
        value="\n".join(state.get("next_actions", [])),
        height=100,
        key="vc_next_actions",
    )

    updated = {
        "goal": goal.strip(),
        "selected_intent": selected_intent.strip(),
        "intent_confidence": intent_confidence,
        "assumptions": _parse_assumptions(assumptions_raw),
        "constraints": _parse_lines(constraints_raw),
        "risks": _parse_lines(risks_raw),
        "open_questions": _parse_lines(open_q_raw),
        "highest_impact_missing_datum": highest_impact_missing_datum.strip(),
        "next_safe_action": next_safe_action.strip(),
        "rationale_trace": _parse_traceability(rationale_trace_raw),
        "next_actions": _parse_lines(next_actions_raw),
    }
    changed = updated != state
    return updated, changed
