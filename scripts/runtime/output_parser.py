from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(slots=True)
class ParsedOutput:
    text: str
    structured: dict


def parse_structured_output(output_text: str) -> ParsedOutput:
    """Require first JSON object from model output and return parsed payload."""
    try:
        data = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model output must be valid JSON object: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Model output JSON must be an object")
    return ParsedOutput(text=output_text, structured=data)
