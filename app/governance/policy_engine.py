"""
app/governance/policy_engine.py — Policy-as-Code evaluation engine.

Evaluates DSL rule expressions against a skill execution context.
Supported actions: BLOCK, WARN, REQUIRE_APPROVAL.

Rule DSL is a restricted Python expression evaluated with a safe
subset of builtins. Available variables in rule context:
  skill_name, risk_score, input_tokens, output_tokens, mode, org_id,
  user_role, hitl_required, tags (list[str])
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("apotheon.policy_engine")

_SAFE_BUILTINS = {
    "True": True, "False": False, "None": None,
    "len": len, "abs": abs, "min": min, "max": max,
    "int": int, "float": float, "str": str, "bool": bool,
    "any": any, "all": all,
}

# Simple whitelist: allow identifiers, comparisons, logical ops, numbers, strings
_SAFE_EXPR_RE = re.compile(
    r'^[\w\s\.\[\]\'\"<>=!&|(),%+\-*/]+$'
)


@dataclass
class PolicyResult:
    policy_id: str
    policy_name: str
    action: str          # BLOCK | WARN | REQUIRE_APPROVAL | PASS
    matched: bool
    reason: str = ""


@dataclass
class EvalContext:
    skill_name: str
    risk_score: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    mode: str = "local"
    org_id: str = ""
    user_role: str = "developer"
    hitl_required: bool = False
    tags: list = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "risk_score": self.risk_score,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "mode": self.mode,
            "org_id": self.org_id,
            "user_role": self.user_role,
            "hitl_required": self.hitl_required,
            "tags": self.tags,
        }


class PolicyEngine:
    """
    Evaluates a list of active Policy ORM objects against an EvalContext.

    Usage:
        engine = PolicyEngine(policies)
        results = engine.evaluate(ctx)
        # Iterate results; first BLOCK wins; WARNs are collected.
    """

    def __init__(self, policies: list):
        self._policies = policies

    def evaluate(self, ctx: EvalContext) -> list[PolicyResult]:
        results = []
        for policy in self._policies:
            if not self._scope_matches(policy.scope_pattern, ctx.skill_name):
                continue
            matched, reason = self._eval_rule(policy.rule_expression, ctx)
            results.append(PolicyResult(
                policy_id=str(policy.id),
                policy_name=policy.name,
                action=policy.action if matched else "PASS",
                matched=matched,
                reason=reason,
            ))
        return results

    # ------------------------------------------------------------------

    def _scope_matches(self, pattern: str, skill_name: str) -> bool:
        """Glob-style scope match: '*' matches all, 'devsecops*' prefix, exact."""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return skill_name.startswith(pattern[:-1])
        return pattern == skill_name

    def _eval_rule(self, expression: str, ctx: EvalContext) -> tuple[bool, str]:
        """
        Evaluate a rule expression safely. Returns (matched, reason).
        Returns (False, error_msg) if expression is invalid or raises.
        """
        expr = expression.strip()
        if not expr:
            return False, "empty expression"

        if not _SAFE_EXPR_RE.match(expr):
            logger.warning("Policy rule contains unsafe characters: %r", expr)
            return False, "unsafe expression rejected"

        env = {**_SAFE_BUILTINS, **ctx.as_dict()}
        try:
            result = eval(expr, {"__builtins__": {}}, env)  # noqa: S307
            matched = bool(result)
            return matched, expr if matched else ""
        except Exception as exc:
            logger.warning("Policy rule eval error for %r: %s", expr, exc)
            return False, f"eval error: {exc}"


def first_blocking_result(results: list[PolicyResult]) -> Optional[PolicyResult]:
    """Return the first BLOCK result, or None."""
    for r in results:
        if r.matched and r.action == "BLOCK":
            return r
    return None


def requires_approval(results: list[PolicyResult]) -> bool:
    """True if any matched result has REQUIRE_APPROVAL action."""
    return any(r.matched and r.action == "REQUIRE_APPROVAL" for r in results)


def warnings(results: list[PolicyResult]) -> list[PolicyResult]:
    """Return all matched WARN results."""
    return [r for r in results if r.matched and r.action == "WARN"]