from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TriggerEngine:
    def __init__(self, registry_path: Path, history_path: Path) -> None:
        self.registry_path = registry_path
        self.history_path = history_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def load_registry(self) -> list[dict[str, Any]]:
        if not self.registry_path.exists():
            return []
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def register_trigger(self, trigger: dict[str, Any]) -> dict[str, Any]:
        registry = self.load_registry()
        registry.append(trigger)
        self.registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return trigger

    def matching_triggers(self, event_type: str) -> list[dict[str, Any]]:
        return [t for t in self.load_registry() if t.get("event_type") == event_type and t.get("enabled", True)]

    def append_history(self, entry: dict[str, Any]) -> None:
        entry = {"recorded_at": datetime.now(timezone.utc).isoformat(), **entry}
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
