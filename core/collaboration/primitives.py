
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class RolePermissionMatrix:
    roles: Dict[str, List[str]] = field(default_factory=dict)

    def allows(self, role: str, permission: str) -> bool:
        return permission in self.roles.get(role, [])
