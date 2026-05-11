from __future__ import annotations

from typing import Any


class SkillRouter:
    def route(self, node: dict[str, Any], registry: dict[str, str]) -> str:
        skill = node.get("skill")
        if not skill:
            raise ValueError(f"node {node.get('id')} missing skill")
        return registry.get(skill, "noop")
