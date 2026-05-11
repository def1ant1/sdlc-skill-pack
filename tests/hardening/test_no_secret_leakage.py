from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.connectors.base_connector import redact_secrets  # noqa: E402


def test_redact_secrets_masks_credentials():
    msg = "Authorization: Bearer abc123 token=mytoken password=letmein x-api-key: key123"
    redacted = redact_secrets(msg)
    assert "abc123" not in redacted
    assert "mytoken" not in redacted
    assert "letmein" not in redacted
    assert "key123" not in redacted
    assert "***" in redacted
