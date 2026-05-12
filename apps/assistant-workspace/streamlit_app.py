from __future__ import annotations

from datetime import datetime, timezone
import uuid

import streamlit as st

st.set_page_config(page_title="Assistant Workspace", layout="wide")
NAV_ITEMS = ["Assistant Home", "Plan Builder", "Workflow Studio", "Skill Library", "Knowledge Base", "Task & Schedule Center"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _init_state() -> None:
    if "workspace" in st.session_state:
        return
    now = _now()
    st.session_state.workspace = {
        "active_nav": NAV_ITEMS[0],
        "context": {
            "session_id": datetime.now(timezone.utc).strftime("WS-%Y%m%d-%H%M%S"),
            "goal": "",
            "last_action": "initialized",
            "updated_at": now,
        },
        "panels": {
            "conversation": [],
            "plan": [
                {"step": "Define objective", "status": "pending"},
                {"step": "Draft execution plan", "status": "pending"},
            ],
            "artifacts": [],
            "knowledge": [],
        },
        "execution": {
            "candidate": None,
            "pending_approvals": [],
            "audit_trail": [],
        },
    }


def _append_audit(event: str, details: dict) -> None:
    ws = st.session_state.workspace
    ws["execution"]["audit_trail"].append({"at": _now(), "event": event, "details": details})


def _sync_action(user_text: str) -> None:
    ws = st.session_state.workspace
    now = _now()
    ws["panels"]["conversation"] += [
        {"role": "user", "text": user_text, "at": now},
        {"role": "assistant", "text": f"Captured request: {user_text}. Plan/artifacts/knowledge synchronized.", "at": now},
    ]
    ws["context"].update({"goal": user_text, "last_action": "chat_message", "updated_at": now})
    ws["panels"]["plan"][0]["status"] = "done"
    ws["panels"]["plan"][1]["status"] = "in_progress"
    ws["panels"]["plan"].append({"step": f"Execute: {user_text}", "status": "queued"})


def _build_candidate_execution(trigger: str) -> None:
    ws = st.session_state.workspace
    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    candidate = {
        "run_id": run_id,
        "trigger": trigger,
        "steps": [
            {"name": "Load workflow and policies", "gate": "none", "side_effect_class": "read", "missing_inputs": []},
            {
                "name": "Generate order recommendations",
                "gate": "soft_hitl",
                "side_effect_class": "analysis",
                "missing_inputs": ["jurisdiction"] if not ws["context"]["goal"] else [],
            },
            {
                "name": "Publish external action",
                "gate": "hard_hitl",
                "side_effect_class": "external_write",
                "missing_inputs": ["approver"]
            },
        ],
    }
    ws["execution"]["candidate"] = candidate
    _append_audit("execution.preview_generated", {"run_id": run_id, "trigger": trigger})


def _route_for_approval(policy_context: str) -> None:
    ws = st.session_state.workspace
    candidate = ws["execution"]["candidate"]
    if not candidate:
        return
    req = {
        "approval_id": f"APR-{uuid.uuid4().hex[:8].upper()}",
        "run_id": candidate["run_id"],
        "risk_reason": "Contains hard HITL external_write step.",
        "policy_context": policy_context,
        "status": "pending",
        "requested_at": _now(),
    }
    ws["execution"]["pending_approvals"].append(req)
    _append_audit("runtime.paused_for_hitl", {"run_id": candidate["run_id"], "approval_id": req["approval_id"]})


def _decide_approval(approval_id: str, decision: str, note: str) -> None:
    ws = st.session_state.workspace
    for req in ws["execution"]["pending_approvals"]:
        if req["approval_id"] == approval_id and req["status"] == "pending":
            req["status"] = decision
            req["decision_note"] = note
            req["decided_at"] = _now()
            event = "runtime.resumed" if decision == "approved" else "runtime.cancelled"
            _append_audit(event, {"run_id": req["run_id"], "approval_id": approval_id, "decision": decision, "note": note})


def main() -> None:
    _init_state()
    ws = st.session_state.workspace
    st.sidebar.title("Workspace Navigation")
    ws["active_nav"] = st.sidebar.radio("Surface", NAV_ITEMS, index=NAV_ITEMS.index(ws["active_nav"]))
    st.sidebar.caption(f"Session: {ws['context']['session_id']}")

    st.title("Assistant Workspace")
    st.info(f"Active surface: **{ws['active_nav']}**")

    st.subheader("Execution Entry")
    cta1, cta2 = st.columns(2)
    with cta1:
        if st.button("Direct execution preview", use_container_width=True):
            _build_candidate_execution("direct")
    with cta2:
        if st.button("Scheduled execution preview", use_container_width=True):
            _build_candidate_execution("scheduled")

    candidate = ws["execution"]["candidate"]
    if candidate:
        st.subheader("Dry-run Preview (Assistant Home / Workflow Studio)")
        st.caption(f"Run `{candidate['run_id']}` via `{candidate['trigger']}` path. Both paths share approval/evidence routing.")
        for i, step in enumerate(candidate["steps"], 1):
            st.write(f"{i}. **{step['name']}** | gate: `{step['gate']}` | side-effect class: `{step['side_effect_class']}`")
            if step["missing_inputs"]:
                st.warning(f"Missing inputs: {', '.join(step['missing_inputs'])}")
        policy_context = st.text_input("Policy context", value="external-action-policy:v1")
        if st.button("Route to Approval Center", use_container_width=True):
            _route_for_approval(policy_context)

    st.subheader("Approval Center")
    pending = ws["execution"]["pending_approvals"]
    if not pending:
        st.caption("No approvals in queue.")
    for req in pending:
        st.markdown(f"**{req['approval_id']}** — run `{req['run_id']}` — status `{req['status']}`")
        st.write(f"Risk reason: {req['risk_reason']}")
        st.write(f"Policy context: {req['policy_context']}")
        if req["status"] == "pending":
            note = st.text_input(f"Decision detail for {req['approval_id']}", key=f"note-{req['approval_id']}")
            a, b, c, d = st.columns(4)
            if a.button("Approve", key=f"approve-{req['approval_id']}"): _decide_approval(req["approval_id"], "approved", note)
            if b.button("Reject", key=f"reject-{req['approval_id']}"): _decide_approval(req["approval_id"], "rejected", note)
            if c.button("Edit", key=f"edit-{req['approval_id']}"): _decide_approval(req["approval_id"], "edit_requested", note or "Please update inputs.")
            if d.button("Request detail", key=f"detail-{req['approval_id']}"): _decide_approval(req["approval_id"], "detail_requested", note or "Need more evidence.")

    st.subheader("Pause/Resume Audit Trail")
    for entry in reversed(ws["execution"]["audit_trail"][-12:]):
        st.write(f"- {entry['at']} — `{entry['event']}` — {entry['details']}")


if __name__ == "__main__":
    main()
