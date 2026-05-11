"""Checkpoint/resume, partial-failure reporting, and safe cancellation helpers."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from error_types import CancellationFailure, ErrorCategory


@dataclass(slots=True)
class PartialFailure:
    step: int
    category: ErrorCategory
    message: str
    retryable: bool


def save_checkpoint(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, sort_keys=True, indent=2), encoding="utf-8")


def load_checkpoint(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resume_from_checkpoint(path: Path, default_state: dict[str, Any] | None = None) -> dict[str, Any]:
    state = load_checkpoint(path)
    if state is None:
        return default_state or {}
    return state


def partial_failure_report(failures: list[PartialFailure]) -> dict[str, Any]:
    return {
        "failed": len(failures),
        "retryable": sum(1 for f in failures if f.retryable),
        "categories": sorted({f.category.value for f in failures}),
        "items": [f.__dict__ | {"category": f.category.value} for f in failures],
    }


def enforce_not_cancelled(cancelled: bool, *, reason: str = "") -> None:
    if cancelled:
        raise CancellationFailure(f"Execution cancelled safely. {reason}".strip())
