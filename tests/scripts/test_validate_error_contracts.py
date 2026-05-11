from scripts.runtime.error_envelope import build_error_envelope


def test_user_facing_errors_have_remediation():
    envelope = build_error_envelope(
        correlation_id="corr-test",
        workflow_run_id="RUN-abc",
        skill="runtime",
        step=1,
        category="runtime",
        message="Step failed",
        remediation="Retry this step after correcting connector credentials.",
        source_exception="RuntimeError",
    )
    assert envelope["user_action_required"] is True
    assert envelope["remediation"].strip()
    assert "retry" in envelope["remediation"].lower() or "correct" in envelope["remediation"].lower()
