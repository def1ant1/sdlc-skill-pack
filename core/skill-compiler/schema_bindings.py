from dataclasses import dataclass


@dataclass(frozen=True)
class CompiledSkill:
    skill_name: str
    compiler_version: str
    activity_stub: str
    eval_stub: str
    package_metadata: dict
