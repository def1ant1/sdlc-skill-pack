#!/usr/bin/env python3
"""
skill_activity.py — Temporal Activity wrappers for Apotheon skills.

Each skill is exposed as a Temporal Activity. Activities handle:
  - Loading the skill's behavioral contract (SKILL.md)
  - Constructing the LLM prompt with context packet
  - Calling the inference API
  - Returning the structured output

This module is imported by temporal_worker.py to register activities.

Environment variables:
    ANTHROPIC_API_KEY    Required for Claude API calls
    CLAUDE_MODEL         Model to use (default: claude-sonnet-4-6)
    SKILLS_ROOT          Path to skills/ directory (default: auto-detected)
    MAX_TOKENS           Max output tokens per activity call (default: 4096)
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("skill_activity")

_HERE = Path(__file__).parent
REPO_ROOT = _HERE.parent.parent
SKILLS_ROOT = Path(os.environ.get("SKILLS_ROOT", str(REPO_ROOT / "skills")))
CORE_ROOT = REPO_ROOT / "core"
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "4096"))


# ---------------------------------------------------------------------------
# Skill contract loader
# ---------------------------------------------------------------------------

def load_skill_contract(skill_name: str) -> str:
    """Return the full text of a skill's SKILL.md."""
    for base in (SKILLS_ROOT, CORE_ROOT):
        path = base / skill_name / "SKILL.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"SKILL.md not found for skill: {skill_name!r}")


# ---------------------------------------------------------------------------
# Inference call
# ---------------------------------------------------------------------------

def call_claude(system_prompt: str, user_message: str) -> str:
    """Call the Anthropic Messages API and return the assistant text."""
    import urllib.request

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is required")

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        response = json.loads(resp.read())

    # Extract text from first content block
    for block in response.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    raise RuntimeError(f"No text content in Claude response: {response}")


# ---------------------------------------------------------------------------
# Activity input/output types
# ---------------------------------------------------------------------------

class SkillActivityInput:
    """Input to a skill activity."""

    def __init__(
        self,
        skill_name: str,
        objective: str,
        context_packet: dict[str, Any] | None = None,
        additional_context: str = "",
    ):
        self.skill_name = skill_name
        self.objective = objective
        self.context_packet = context_packet or {}
        self.additional_context = additional_context

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "objective": self.objective,
            "context_packet": self.context_packet,
            "additional_context": self.additional_context,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SkillActivityInput":
        return cls(
            skill_name=d["skill_name"],
            objective=d["objective"],
            context_packet=d.get("context_packet", {}),
            additional_context=d.get("additional_context", ""),
        )


class SkillActivityOutput:
    """Output from a skill activity."""

    def __init__(
        self,
        skill_name: str,
        success: bool,
        output: str,
        error: str = "",
        requires_hitl: bool = False,
        hitl_reason: str = "",
    ):
        self.skill_name = skill_name
        self.success = success
        self.output = output
        self.error = error
        self.requires_hitl = requires_hitl
        self.hitl_reason = hitl_reason

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "requires_hitl": self.requires_hitl,
            "hitl_reason": self.hitl_reason,
        }


# ---------------------------------------------------------------------------
# Core activity implementation
# ---------------------------------------------------------------------------

def run_skill_activity(inp: SkillActivityInput) -> SkillActivityOutput:
    """
    Execute a skill activity:
      1. Load the skill's SKILL.md as system prompt
      2. Build user message from objective + context packet
      3. Call Claude API
      4. Return structured output
    """
    logger.info("Running skill activity: %s", inp.skill_name)

    try:
        system_prompt = load_skill_contract(inp.skill_name)
    except FileNotFoundError as exc:
        logger.error("Skill not found: %s", exc)
        return SkillActivityOutput(
            skill_name=inp.skill_name,
            success=False,
            output="",
            error=f"Skill contract not found: {exc}",
        )

    # Build user message
    parts = [f"## Objective\n{inp.objective}"]

    if inp.context_packet:
        parts.append(f"## Context Packet\n```json\n{json.dumps(inp.context_packet, indent=2)}\n```")

    if inp.additional_context:
        parts.append(f"## Additional Context\n{inp.additional_context}")

    user_message = "\n\n".join(parts)

    try:
        output_text = call_claude(system_prompt, user_message)
        logger.info("Skill %s completed successfully (%d chars)", inp.skill_name, len(output_text))

        # Simple HITL detection: check if output mentions approval gates
        requires_hitl = any(
            phrase in output_text.lower()
            for phrase in ["requires approval", "level-3 approval", "human approval", "hitl gate"]
        )

        return SkillActivityOutput(
            skill_name=inp.skill_name,
            success=True,
            output=output_text,
            requires_hitl=requires_hitl,
            hitl_reason="Output flagged approval gate" if requires_hitl else "",
        )
    except Exception as exc:
        logger.error("Skill %s failed: %s", inp.skill_name, exc, exc_info=True)
        return SkillActivityOutput(
            skill_name=inp.skill_name,
            success=False,
            output="",
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# CLI — run a single skill activity directly
# ---------------------------------------------------------------------------

def main() -> int:
    """Run a single skill activity from the command line for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Run a single Apotheon skill activity")
    parser.add_argument("skill_name", help="Skill name (e.g. code-review)")
    parser.add_argument("objective", help="Objective text")
    parser.add_argument("--context", help="Context packet JSON string", default="{}")
    args = parser.parse_args()

    inp = SkillActivityInput(
        skill_name=args.skill_name,
        objective=args.objective,
        context_packet=json.loads(args.context),
    )
    result = run_skill_activity(inp)
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())