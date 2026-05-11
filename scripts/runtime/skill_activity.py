#!/usr/bin/env python3
"""
skill_activity.py — Temporal Activity wrappers for Apotheon skills.

Each skill is exposed as a Temporal Activity. Activities handle:
  - Loading the skill's behavioral contract (SKILL.md)
  - Constructing the LLM prompt with context packet
  - Calling the inference API
  - Detecting HITL gates (structured marker > risk-list > phrase fallback)
  - Returning the structured output

This module is imported by temporal_worker.py to register activities.

Environment variables:
    ANTHROPIC_API_KEY    Required for Claude API calls
    CLAUDE_MODEL         Model to use (default: claude-sonnet-4-6)
    SKILLS_ROOT          Path to skills/ directory (default: auto-detected)
    MAX_TOKENS           Max output tokens per activity call (default: 4096)

HITL gate detection (three-layer, in priority order):
  1. Structured marker in output:
         <!-- HITL_GATE: {"required": true, "level": "L3", "reason": "..."} -->
  2. Skill name matches the known high-risk skill list (_HITL_REQUIRED_SKILLS)
  3. Phrase matching fallback on output text (_HITL_PHRASES)
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger("skill_activity")

_HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Observability helpers (graceful — no-ops when app/ package not available)
# ---------------------------------------------------------------------------

def _record_llm(model: str, duration_s: float, retry_count: int = 0, http_status: int = 200) -> None:
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from app.observability.metrics import record_llm_call
        record_llm_call(model=model, duration_s=duration_s, retry_count=retry_count, http_status=http_status)
    except Exception:
        pass


def _record_tokens(skill: str, model: str, input_tokens: int, output_tokens: int) -> None:
    try:
        from app.observability.metrics import record_token_usage
        record_token_usage(skill_name=skill, model=model, input_tokens=input_tokens, output_tokens=output_tokens)
    except Exception:
        pass


def _record_skill(skill: str, status: str, duration_s: float) -> None:
    try:
        from app.observability.metrics import record_skill_call
        record_skill_call(skill_name=skill, status=status, duration_s=duration_s)
    except Exception:
        pass


def _record_hitl(skill: str, outcome: str) -> None:
    try:
        from app.observability.metrics import record_hitl_event
        record_hitl_event(skill_name=skill, outcome=outcome)
    except Exception:
        pass
REPO_ROOT = _HERE.parent.parent
SKILLS_ROOT = Path(os.environ.get("SKILLS_ROOT", str(REPO_ROOT / "skills")))
CORE_ROOT = REPO_ROOT / "core"
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "4096"))

from model_router import resolve_provider
from local_model_fallback import fallback_response
from output_parser import parse_structured_output
from schema_validation import validate_structured_skill_output


# ---------------------------------------------------------------------------
# HITL gate detection
# ---------------------------------------------------------------------------

# Regex to parse structured HITL marker the model may emit in its output:
#   <!-- HITL_GATE: {"required": true, "level": "L3", "reason": "..."} -->
_HITL_MARKER_RE = re.compile(
    r"<!--\s*HITL_GATE:\s*(\{.*?\})\s*-->",
    re.DOTALL | re.IGNORECASE,
)

# Skills that always require L3 human approval regardless of output content.
# Source: docs/governance/hitl-gate-audit.md (P1 gaps — production-impact risks)
_HITL_REQUIRED_SKILLS: frozenset[str] = frozenset({
    "cloud-deployment",
    "devsecops",
    "release-management",
    "compliance-automation",
    "local-security",
    "database-migration",
    "infrastructure-provisioning",
    "secret-rotation",
    "incident-response",
    "sre",
})

# Phrase-based fallback (backward compat)
_HITL_PHRASES: tuple[str, ...] = (
    "requires approval",
    "level-3 approval",
    "human approval",
    "hitl gate",
    "awaiting approval",
    "l3 approval",
)

# Instruction appended to every user message so models can emit structured markers
_HITL_GATE_INSTRUCTION = """\

---
**HITL Gate Protocol**: If this action requires blocking human approval before
proceeding (e.g. production deployment, irreversible infrastructure change, or
security policy exception), include the following marker at the very end of your
response — otherwise omit it:
<!-- HITL_GATE: {"required": true, "level": "L3", "reason": "<brief reason>"} -->"""


def detect_hitl(skill_name: str, output_text: str) -> tuple[bool, str]:
    """
    Determine whether this skill output requires HITL approval.

    Returns (requires_hitl, reason). Priority:
      1. Structured <!-- HITL_GATE: {...} --> marker in output
      2. Skill name in the known high-risk list
      3. Phrase matching on output text (fallback)
    """
    # Layer 1: structured marker (authoritative — short-circuits lower layers if valid)
    match = _HITL_MARKER_RE.search(output_text)
    if match:
        try:
            marker = json.loads(match.group(1))
            if marker.get("required"):
                level = marker.get("level", "L3")
                reason = marker.get("reason", "HITL marker present in output")
                return True, f"[{level}] {reason}"
            else:
                # Marker explicitly says not required — trust it over risk-list
                return False, ""
        except (json.JSONDecodeError, AttributeError):
            logger.debug("Malformed HITL_GATE marker in %s output — ignored", skill_name)

    # Layer 2: risk-based lookup
    if skill_name in _HITL_REQUIRED_SKILLS:
        return True, f"Skill '{skill_name}' is classified as high-risk (always requires L3 approval)"

    # Layer 3: phrase matching
    lower = output_text.lower()
    for phrase in _HITL_PHRASES:
        if phrase in lower:
            return True, f"Output contains approval gate phrase: '{phrase}'"

    return False, ""


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

_RETRYABLE_HTTP_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504, 529})
_MAX_CALL_RETRIES: int = 3
_INITIAL_BACKOFF: float = 1.0
_BACKOFF_MULTIPLIER: float = 2.0
_MAX_BACKOFF: float = 60.0


def call_claude(system_prompt: str, user_message: str) -> tuple[str, int, int]:
    """Call the Anthropic Messages API and return (text, input_tokens, output_tokens).

    Retries on transient errors (429/5xx/network) with exponential backoff.
    Raises RuntimeError on non-retryable errors or exhausted retries.
    """
    import urllib.error
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
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    backoff = _INITIAL_BACKOFF
    last_exc: Exception | None = None
    retry_count = 0

    for attempt in range(1, _MAX_CALL_RETRIES + 2):
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers=headers,
            method="POST",
        )
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                try:
                    response = json.loads(resp.read())
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Claude API returned non-JSON response: {exc}") from exc

            duration_s = time.perf_counter() - t0
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            _record_llm(CLAUDE_MODEL, duration_s, retry_count=retry_count)

            for block in response.get("content", []):
                if block.get("type") == "text":
                    return block["text"], input_tokens, output_tokens
            raise RuntimeError(f"No text content in Claude response: {response}")

        except urllib.error.HTTPError as exc:
            status = exc.code
            if status not in _RETRYABLE_HTTP_CODES or attempt > _MAX_CALL_RETRIES:
                body = ""
                try:
                    body = exc.read().decode(errors="replace")[:500]
                except Exception:
                    pass
                _record_llm(CLAUDE_MODEL, time.perf_counter() - t0, retry_count=retry_count, http_status=status)
                raise RuntimeError(f"Claude API HTTP {status}: {body}") from exc

            retry_after = float(exc.headers.get("retry-after", backoff))
            wait = max(retry_after, backoff)
            logger.warning(
                "Claude API HTTP %s on attempt %d/%d — retrying in %.1fs",
                status, attempt, _MAX_CALL_RETRIES, wait,
            )
            time.sleep(wait)
            backoff = min(backoff * _BACKOFF_MULTIPLIER, _MAX_BACKOFF)
            retry_count += 1
            last_exc = exc

        except OSError as exc:
            if attempt > _MAX_CALL_RETRIES:
                raise RuntimeError(f"Claude API network error after {_MAX_CALL_RETRIES} retries: {exc}") from exc
            logger.warning(
                "Claude API network error on attempt %d/%d: %s — retrying in %.1fs",
                attempt, _MAX_CALL_RETRIES, exc, backoff,
            )
            time.sleep(backoff)
            backoff = min(backoff * _BACKOFF_MULTIPLIER, _MAX_BACKOFF)
            retry_count += 1
            last_exc = exc

    raise RuntimeError(f"Claude API: all retries exhausted. Last error: {last_exc}")


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
        _validate_skill_activity_input(d)
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
        structured_output: dict | None = None,
        estimated_cost_usd: float = 0.0,
        correlation_id: str = "",
    ):
        self.skill_name = skill_name
        self.success = success
        self.output = output
        self.error = error
        self.requires_hitl = requires_hitl
        self.hitl_reason = hitl_reason
        self.structured_output = structured_output or {}
        self.estimated_cost_usd = estimated_cost_usd
        self.correlation_id = correlation_id

    def to_dict(self) -> dict:
        return {
            "skill_name": self.skill_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "requires_hitl": self.requires_hitl,
            "hitl_reason": self.hitl_reason,
            "structured_output": self.structured_output,
            "estimated_cost_usd": self.estimated_cost_usd,
            "correlation_id": self.correlation_id,
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
    correlation_id = f"skill-{uuid.uuid4().hex[:10]}"
    dry_run = os.environ.get("APOTHEON_DRY_RUN", "").lower() in {"1", "true", "yes"}
    provider = resolve_provider(dry_run=dry_run)

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

    # Append HITL gate protocol so the model can emit a structured marker
    parts.append(_HITL_GATE_INSTRUCTION)

    user_message = "\n\n".join(parts)

    t0 = time.perf_counter()
    try:
        if provider == "local-stub":
            output_text = fallback_response(inp.skill_name, inp.objective)
            input_tokens, output_tokens = 0, 0
        else:
            output_text, input_tokens, output_tokens = call_claude(system_prompt, user_message)
        duration_s = time.perf_counter() - t0
        logger.info("Skill %s completed successfully (%d chars)", inp.skill_name, len(output_text))

        _record_tokens(inp.skill_name, CLAUDE_MODEL, input_tokens, output_tokens)
        _record_skill(inp.skill_name, "completed", duration_s)

        parsed = parse_structured_output(output_text)
        validate_structured_skill_output(parsed.structured)
        requires_hitl, hitl_reason = detect_hitl(inp.skill_name, output_text)
        estimated_cost_usd = round((input_tokens * 0.000003) + (output_tokens * 0.000015), 6)
        if requires_hitl:
            logger.info("HITL gate triggered for %s: %s", inp.skill_name, hitl_reason)
            _record_hitl(inp.skill_name, "triggered")

        return SkillActivityOutput(
            skill_name=inp.skill_name,
            success=True,
            output=output_text,
            requires_hitl=requires_hitl,
            hitl_reason=hitl_reason,
            structured_output=parsed.structured,
            estimated_cost_usd=estimated_cost_usd,
            correlation_id=correlation_id,
        )
    except Exception as exc:
        duration_s = time.perf_counter() - t0
        logger.error("Skill %s failed: %s", inp.skill_name, exc, exc_info=True)
        _record_skill(inp.skill_name, "failed", duration_s)
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
def _validate_skill_activity_input(payload: dict[str, Any]) -> None:
    required = {"skill_name", "objective"}
    missing = sorted(required - set(payload.keys()))
    if missing:
        raise ValueError(f"Invalid skill activity input; missing keys: {', '.join(missing)}")
