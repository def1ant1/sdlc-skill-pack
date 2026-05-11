from __future__ import annotations

from typing import Any, Callable


class EvaluatorHooks:
    def __init__(self) -> None:
        self._hooks: list[Callable[[dict[str, Any]], None]] = []

    def register(self, hook: Callable[[dict[str, Any]], None]) -> None:
        self._hooks.append(hook)

    def run(self, event: dict[str, Any]) -> None:
        for hook in self._hooks:
            hook(event)
