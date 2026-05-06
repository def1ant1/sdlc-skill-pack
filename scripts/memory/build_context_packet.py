#!/usr/bin/env python3
from dataclasses import dataclass, asdict
import json, sys

@dataclass
class ContextPacket:
    objective: str
    phase: str
    decisions: list
    constraints: list
    artifacts: list
    risks: list
    next_action: str

def build_packet(data: dict) -> dict:
    return asdict(ContextPacket(
        objective=data.get("objective", ""),
        phase=data.get("phase", ""),
        decisions=data.get("decisions", []),
        constraints=data.get("constraints", []),
        artifacts=data.get("artifacts", []),
        risks=data.get("risks", []),
        next_action=data.get("next_action", ""),
    ))

if __name__ == "__main__":
    payload = json.load(sys.stdin)
    print(json.dumps(build_packet(payload), indent=2))
