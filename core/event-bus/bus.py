from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class EventRecord:
    event_type: str
    source: str
    payload: dict[str, Any]
    emitted_at: str


class EventBus:
    """Lightweight local event bus backed by jsonl files."""

    def __init__(self, history_path: Path) -> None:
        self.history_path = history_path
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def publish(self, event_type: str, *, source: str, payload: dict[str, Any]) -> EventRecord:
        record = EventRecord(
            event_type=event_type,
            source=source,
            payload=payload,
            emitted_at=datetime.now(timezone.utc).isoformat(),
        )
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        return record
