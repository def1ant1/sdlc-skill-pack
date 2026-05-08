"""
End-to-end integration tests for the Apotheon workflow pipeline.

Tests the full local pipeline:
  plan_workflow → execute_workflow (dry-run) → context_manager → retrieve_context

No LLM calls, no live Qdrant, no Temporal required.
All external calls are mocked at the urllib level.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import unittest.mock as mock
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
PLAN_WORKFLOW = REPO_ROOT / "scripts" / "orchestration" / "plan_workflow.py"
PLAN_GTM = REPO_ROOT / "scripts" / "orchestration" / "plan_gtm_workflow.py"
EXECUTE_WORKFLOW = REPO_ROOT / "scripts" / "runtime" / "execute_workflow.py"

_PYTHON = sys.executable


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan(objective: str, planner: Path = PLAN_WORKFLOW) -> dict:
    result = subprocess.run(
        [_PYTHON, str(planner), objective],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"Planner failed:\n{result.stderr}"
    return json.loads(result.stdout)


def _execute(plan: dict, dry_run: bool = True) -> dict:
    cmd = [_PYTHON, str(EXECUTE_WORKFLOW)]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(
        cmd,
        input=json.dumps(plan),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Execution failed:\n{result.stderr}\n{result.stdout}"
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Plan → Execute (dry-run) pipeline
# ---------------------------------------------------------------------------

class TestSDLCPipeline:
    def test_plan_and_dry_run_produces_execution_log(self):
        plan = _plan("Build a REST API with authentication")
        log = _execute(plan, dry_run=True)

        assert "run_id" in log
        assert log["status"] == "dry_run"
        assert len(log["steps"]) > 0

    def test_all_dry_run_steps_are_skipped(self):
        plan = _plan("Deploy to production")
        log = _execute(plan, dry_run=True)

        for step in log["steps"]:
            assert step["status"] == "dry_run", f"Expected dry_run, got {step['status']} for {step['skill']}"

    def test_execution_log_preserves_objective(self):
        objective = "Implement zero-trust security architecture"
        plan = _plan(objective)
        log = _execute(plan, dry_run=True)

        assert log["objective"] == objective

    def test_step_numbers_in_log_are_sequential(self):
        plan = _plan("Build and test a payment service")
        log = _execute(plan, dry_run=True)
        steps = [s["step"] for s in log["steps"]]
        assert steps == list(range(1, len(steps) + 1))

    def test_plan_id_preserved_in_execution_log(self):
        plan = _plan("Design microservices architecture")
        log = _execute(plan, dry_run=True)
        assert log.get("plan_id") == plan.get("plan_id")

    def test_total_steps_matches_skill_chain_length(self):
        plan = _plan("Full SDLC for a SaaS product")
        log = _execute(plan, dry_run=True)
        assert log["total_steps"] == len(plan["skill_chain"])


class TestGTMPipeline:
    def test_gtm_plan_and_dry_run(self):
        plan = _plan("Launch developer tools to enterprise market", planner=PLAN_GTM)
        log = _execute(plan, dry_run=True)

        assert log["status"] == "dry_run"
        assert len(log["steps"]) > 0

    def test_gtm_skills_are_registered_on_disk(self):
        plan = _plan("Full go-to-market motion", planner=PLAN_GTM)
        for step in plan["skill_chain"]:
            skill_path = REPO_ROOT / "skills" / step["skill"] / "SKILL.md"
            assert skill_path.exists(), f"GTM skill missing SKILL.md: {step['skill']}"


# ---------------------------------------------------------------------------
# Context manager (unit tests with mocked Qdrant)
# ---------------------------------------------------------------------------

_RUNTIME_PATH = str(REPO_ROOT / "scripts" / "runtime")
if _RUNTIME_PATH not in sys.path:
    sys.path.insert(0, _RUNTIME_PATH)


class TestContextManager:
    def _make_cm(self, run_id: str = "TEST-RUN-001"):
        from context_manager import ContextManager
        return ContextManager(run_id=run_id, objective="Test objective")

    def test_load_returns_fresh_packet_when_no_snapshot(self):
        with mock.patch("context_manager._qdrant_request", return_value={}):
            cm = self._make_cm()
            packet = cm.load()
            assert packet["objective"] == "Test objective"
            assert packet["decisions"] == []
            assert packet["artifacts"] == []

    def test_load_restores_snapshot_when_available(self):
        snapshot = {
            "objective": "Test objective",
            "phase": "backend",
            "decisions": ["Use PostgreSQL"],
            "artifacts": ["backend_output"],
            "constraints": [],
            "risks": [],
            "next_action": "",
        }
        mock_response = {
            "result": {
                "points": [{"payload": {"context_json": json.dumps(snapshot)}}]
            }
        }
        with mock.patch("context_manager._qdrant_request", return_value=mock_response):
            cm = self._make_cm()
            packet = cm.load()
            assert packet["decisions"] == ["Use PostgreSQL"]
            assert packet["artifacts"] == ["backend_output"]

    def test_save_step_calls_qdrant_when_embedding_available(self):
        fake_vector = [0.1] * 768
        with mock.patch("context_manager._embed", return_value=fake_vector), \
             mock.patch("context_manager._qdrant_request") as mock_req:
            cm = self._make_cm()
            cm.save_step(step=1, skill="backend-engineering", output="Generated API spec.")
            mock_req.assert_called_once()
            call_args = mock_req.call_args
            assert "PUT" in call_args[0]

    def test_save_step_skips_qdrant_when_no_embedding(self):
        with mock.patch("context_manager._embed", return_value=None), \
             mock.patch("context_manager._qdrant_request") as mock_req:
            cm = self._make_cm()
            cm.save_step(step=1, skill="backend-engineering", output="Output text")
            mock_req.assert_not_called()

    def test_finalize_records_status(self):
        fake_vector = [0.0] * 768
        captured = {}
        def mock_qdrant(method, path, payload=None):
            if method == "PUT":
                captured["payload"] = payload
            return {}

        with mock.patch("context_manager._embed", return_value=fake_vector), \
             mock.patch("context_manager._qdrant_request", side_effect=mock_qdrant):
            cm = self._make_cm()
            cm.finalize("completed")
            assert captured.get("payload") is not None
            points = captured["payload"].get("points", [])
            assert len(points) == 1
            assert points[0]["payload"]["status"] == "completed"


# ---------------------------------------------------------------------------
# skill_activity (unit tests with mocked Claude API)
# ---------------------------------------------------------------------------

class TestSkillActivity:
    def _mock_claude_response(self, text: str) -> bytes:
        response = {
            "content": [{"type": "text", "text": text}],
            "model": "claude-sonnet-4-6",
            "stop_reason": "end_turn",
        }
        return json.dumps(response).encode()

    def test_call_claude_returns_text_content(self):
        from skill_activity import call_claude

        mock_response = self._mock_claude_response("This is the skill output.")

        with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
            with mock.patch("urllib.request.urlopen") as mock_open:
                mock_open.return_value.__enter__ = lambda s: s
                mock_open.return_value.__exit__ = mock.Mock(return_value=False)
                mock_open.return_value.read = lambda: mock_response

                result = call_claude("System prompt", "User message")
                assert result == "This is the skill output."

    def test_call_claude_raises_on_missing_api_key(self):
        from skill_activity import call_claude

        with mock.patch.dict("os.environ", {}, clear=True):
            os_env = {k: v for k, v in __import__("os").environ.items() if k != "ANTHROPIC_API_KEY"}
            with mock.patch.dict("os.environ", os_env, clear=True):
                with pytest.raises(EnvironmentError, match="ANTHROPIC_API_KEY"):
                    call_claude("System", "User")

    def test_run_skill_activity_returns_output_on_missing_skill(self):
        from skill_activity import SkillActivityInput, run_skill_activity

        inp = SkillActivityInput(
            skill_name="skill-that-does-not-exist-xyz",
            objective="Test",
        )
        result = run_skill_activity(inp)
        assert result.success is False
        assert "not found" in result.error.lower()


# ---------------------------------------------------------------------------
# Validate → Plan → Execute round-trip
# ---------------------------------------------------------------------------

class TestFullRoundTrip:
    def test_validate_then_plan_then_dry_run(self):
        """Complete pipeline: validate repo → plan → dry-run execute."""
        # Step 1: Validate structure
        r = subprocess.run(
            [_PYTHON, str(REPO_ROOT / "scripts" / "validation" / "validate_skill_structure.py"), str(REPO_ROOT)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"Validation failed:\n{r.stderr}"

        # Step 2: Plan
        plan = _plan("Build and deploy a microservice")
        assert len(plan["skill_chain"]) > 0

        # Step 3: Dry-run execute
        log = _execute(plan, dry_run=True)
        assert log["status"] == "dry_run"
        assert log["total_steps"] == len(plan["skill_chain"])