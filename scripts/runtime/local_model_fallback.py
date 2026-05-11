from __future__ import annotations


def fallback_response(skill_name: str, objective: str) -> str:
    return (
        "{\"status\": \"dry_run\", "
        f"\"skill\": \"{skill_name}\", "
        f"\"objective\": \"{objective[:120]}\", "
        "\"summary\": \"No external model call executed in dry-run mode.\"}"
    )
