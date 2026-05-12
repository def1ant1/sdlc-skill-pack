import json
from pathlib import Path


FIXTURE_PATH = Path("tests/fixtures/chat-ui/analysis_prompt_regression_cases.json")


def test_analysis_prompt_regression_fixtures_cover_required_intents() -> None:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    intents = {case.get("intent") for case in data}
    assert {"q_and_a", "brainstorm", "draft_plan", "workflow"}.issubset(intents)


def test_analysis_prompt_regression_fixture_contract_rules() -> None:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    for case in data:
        expected = case.get("expected", {})
        assert expected.get("allow_empty_questions") is True
        assert expected.get("require_assumptions") is True
        assert expected.get("require_open_questions") is True
        questions_max = expected.get("questions_max")
        assert isinstance(questions_max, int)
        if case.get("full_intake_requested"):
            assert questions_max >= 1
        else:
            assert questions_max <= 1
