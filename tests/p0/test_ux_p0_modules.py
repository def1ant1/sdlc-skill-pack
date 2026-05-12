from __future__ import annotations

import importlib.util
from pathlib import Path

from core.ui_p0_common import P0OperationContext, rollback_update

MODULE_DIRS = [
    "action-suggestions",
    "assistant-insights",
    "workflow-control",
    "execution-stream",
    "timeline",
    "task-schedule-center",
    "approval-center",
    "execution-simulation",
    "knowledge-curation-assistant",
]


def load_module(name: str):
    path = Path(f"core/{name}/module.py")
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_payload():
    return {"id": "x-1", "status": "active", "updated_at": "2026-05-12T00:00:00Z"}


def test_acceptance_qa_checks_and_audit_logging():
    for name in MODULE_DIRS:
        module = load_module(name)
        ctx = P0OperationContext()
        state = {"initial": True}
        payload = _valid_payload()
        interaction = {"event": "submit"}
        out = module.process_action(state, payload, interaction, ctx)
        assert out["id"] == "x-1"
        assert ctx.audit_log[-1]["module"] == name.replace('-', '_')


def test_policy_checks_and_reversible_operations():
    for name in MODULE_DIRS:
        module = load_module(name)
        ctx = P0OperationContext()
        state = {"initial": True}
        payload = _valid_payload()
        payload["policy_blocked"] = True
        try:
            module.process_action(state, payload, {"event": "submit"}, ctx)
            assert False, "expected PermissionError"
        except PermissionError:
            pass

        before = {"foo": "bar"}
        working = dict(before)
        module.process_action(working, _valid_payload(), {"event": "submit"}, ctx)
        rollback_update(working, before)
        assert working == before
