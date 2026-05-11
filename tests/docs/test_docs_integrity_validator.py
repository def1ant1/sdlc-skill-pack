from scripts.docs.validate_docs_integrity import main


def test_docs_integrity_validator_passes() -> None:
    assert main() == 0
