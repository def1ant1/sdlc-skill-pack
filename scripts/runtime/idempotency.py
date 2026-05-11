"""Idempotency and side-effect safety guards."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from error_types import SideEffectSafetyError


@dataclass(slots=True)
class IdempotencyRecord:
    key: str
    operation: str
    payload_hash: str


def compute_idempotency_key(operation: str, payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(f"{operation}:{blob}".encode()).hexdigest()
    return f"idem-{digest[:20]}"


def assert_side_effect_allowed(*, dry_run: bool, has_side_effect: bool, high_risk: bool, operation: str) -> None:
    if dry_run and has_side_effect:
        raise SideEffectSafetyError(f"Dry-run prohibits side effects for operation '{operation}'")
    if high_risk:
        raise SideEffectSafetyError(f"Unsafe retry prohibited for high-risk side-effect operation '{operation}'")


def write_idempotency_record(path: Path, record: IdempotencyRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record.__dict__, sort_keys=True, indent=2), encoding="utf-8")


def read_idempotency_record(path: Path) -> IdempotencyRecord | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return IdempotencyRecord(**data)
