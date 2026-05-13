from core.timeline.module import validate_schema


def test_timeline_accepts_intermediate_and_terminal_statuses():
    statuses = [
        "ready_to_execute",
        "executing",
        "awaiting_approval",
        "delivered",
        "failed_recoverable",
        "failed_terminal",
    ]
    for status in statuses:
        payload = {"id": "evt-1", "status": status, "updated_at": "2026-05-12T00:00:00Z"}
        assert validate_schema(payload) == []
