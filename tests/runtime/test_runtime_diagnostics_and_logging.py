from __future__ import annotations

import json
from pathlib import Path

from scripts.reports.generate_runtime_diagnostics import generate
from scripts.runtime.execute_workflow import _log


def test_runtime_diagnostics_failure_aggregation(tmp_path: Path):
    log = tmp_path / "telemetry.log.yaml"
    log.write_text(
        "\n".join([
            json.dumps({"event_name": "workflow.lifecycle.step_completed", "status": "ok"}),
            json.dumps({"event_name": "workflow.policy.failure", "status": "error"}),
            json.dumps({"event_name": "workflow.schema.failure", "status": "error"}),
        ])
    )
    report = generate(log)
    assert report["failure_categories"]["policy"] == 1
    assert report["failure_categories"]["schema failures"] == 1
    assert "remediation" in report


def test_json_logging_includes_correlation_id(monkeypatch, capsys):
    monkeypatch.setenv("LOG_FORMAT", "json")
    _log("info", "hello", run_id="RUN-1")
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["correlation_id"] == "RUN-1"
    assert payload["message"] == "hello"
