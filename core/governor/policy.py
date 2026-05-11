from __future__ import annotations

from typing import Any


class PolicyGovernor:
    def enforce(self, node: dict[str, Any], state: dict[str, Any]) -> None:
        required_approval = node.get("approval", {}).get("required", False)
        if required_approval and node["id"] not in state.get("approvals", {}):
            raise PermissionError(f"approval required for {node['id']}")
