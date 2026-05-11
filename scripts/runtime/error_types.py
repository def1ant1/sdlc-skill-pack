"""Typed runtime exception hierarchy for resilient orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    CONFIG = "config"
    AUTH = "auth"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    DEPENDENCY = "dependency"
    CONNECTOR = "connector"
    CONFLICT = "conflict"
    SIDE_EFFECT = "side_effect"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class RuntimeErrorBase(Exception):
    message: str
    category: ErrorCategory = ErrorCategory.UNKNOWN
    retryable: bool = False
    high_risk_side_effect: bool = False
    dry_run_safe: bool = True
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message


class ValidationFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.VALIDATION, retryable=False, **kwargs)


class ConfigurationFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.CONFIG, retryable=False, **kwargs)


class AuthenticationFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.AUTH, retryable=False, **kwargs)


class NetworkFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.NETWORK, retryable=True, **kwargs)


class RateLimitFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.RATE_LIMIT, retryable=True, **kwargs)


class TimeoutFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.TIMEOUT, retryable=True, **kwargs)


class DependencyFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.DEPENDENCY, retryable=True, **kwargs)


class ConnectorFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.CONNECTOR, retryable=True, **kwargs)


class ConflictFailure(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.CONFLICT, retryable=False, **kwargs)


class SideEffectSafetyError(RuntimeErrorBase):
    def __init__(self, message: str, **kwargs: Any):
        super().__init__(
            message=message,
            category=ErrorCategory.SIDE_EFFECT,
            retryable=False,
            high_risk_side_effect=True,
            dry_run_safe=False,
            **kwargs,
        )


class CancellationFailure(RuntimeErrorBase):
    def __init__(self, message: str = "Operation cancelled", **kwargs: Any):
        super().__init__(message=message, category=ErrorCategory.CANCELLED, retryable=False, **kwargs)
