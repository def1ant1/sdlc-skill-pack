#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from scripts.runtime.circuit_breaker import CircuitBreaker
from scripts.runtime.error_envelope import build_error_envelope

logger = logging.getLogger(__name__)


class DryRunSideEffectBlocked(RuntimeError):
    """Raised when connector outbound calls are blocked in dry-run mode."""


class CircuitOpenBlocked(RuntimeError):
    """Raised when outbound requests are blocked because the circuit is open."""


def _dry_run_enabled() -> bool:
    return os.environ.get("APOTHEON_DRY_RUN", "").strip().lower() in {"1", "true", "yes", "on"}


def _read_only_default() -> bool:
    return os.environ.get("APOTHEON_CONNECTORS_READ_ONLY", "true").strip().lower() not in {"0", "false", "no", "off"}


@dataclass(slots=True)
class PaginationState:
    page: int = 1
    next_cursor: str | None = None


def redact_secrets(value: str) -> str:
    value = re.sub(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._\-]+", r"\1***", value)
    value = re.sub(r"(?i)(x-api-key\s*:\s*)[^\s,;]+", r"\1***", value)
    value = re.sub(r"(?i)(token|password|secret|api[_-]?key)\s*[=:]\s*[^\s,;]+", r"\1=***", value)
    return value


class SecretRedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_secrets(str(record.msg))
        if record.args:
            record.args = tuple(redact_secrets(str(a)) for a in record.args)
        return True


class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self._rpm = requests_per_minute
        self._tokens = float(requests_per_minute)
        self._last_refill = time.monotonic()
        self._interval = 60.0 / requests_per_minute

    def acquire(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._rpm, self._tokens + elapsed * (self._rpm / 60.0))
        self._last_refill = now
        if self._tokens < 1.0:
            time.sleep((1.0 - self._tokens) * self._interval)
            self._tokens = 0.0
        else:
            self._tokens -= 1.0

    def handle_429(self, retry_after_seconds: float = 60.0) -> None:
        self._tokens = 0.0
        time.sleep(retry_after_seconds)


class BaseConnector(ABC):
    RATE_LIMIT_RPM: int = 60
    MAX_RETRIES: int = 3
    INITIAL_BACKOFF_SECONDS: float = 1.0
    BACKOFF_MULTIPLIER: float = 2.0
    MAX_BACKOFF_SECONDS: float = 60.0
    RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 502, 503, 504})
    NON_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({400, 401, 403, 404, 422})
    WRITE_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})

    def __init__(self):
        self._auth_headers: dict[str, str] = {}
        self._rate_limiter = RateLimiter(self.RATE_LIMIT_RPM)
        self._authenticated = False
        self.logger = logging.getLogger(f"connector.{self.__class__.__name__.lower()}")
        self.logger.addFilter(SecretRedactionFilter())
        self.correlation_id = os.environ.get("APOTHEON_CORRELATION_ID", "corr-connector")
        self.workflow_run_id = os.environ.get("APOTHEON_WORKFLOW_RUN_ID", "n/a")
        self.schedule_run_id = os.environ.get("APOTHEON_SCHEDULE_RUN_ID", "n/a")
        self._read_only_mode = _read_only_default()
        self._circuit = CircuitBreaker(
            failure_threshold=int(os.environ.get("APOTHEON_CONNECTOR_CB_FAILURE_THRESHOLD", "5")),
            recovery_timeout_seconds=float(os.environ.get("APOTHEON_CONNECTOR_CB_RECOVERY_SECONDS", "30")),
        )

    @abstractmethod
    def _authenticate(self) -> None: ...

    @abstractmethod
    def health_check(self) -> bool: ...

    def _ensure_authenticated(self) -> None:
        if not self._authenticated:
            self._authenticate()
            self._authenticated = True

    def _assert_write_allowed(self, method: str, *, idempotency_key: str | None = None, hitl_approved: bool = False) -> None:
        if method.upper() not in self.WRITE_METHODS:
            return
        if self._read_only_mode:
            raise PermissionError("Connector writes are disabled by default (read-only mode).")
        if not idempotency_key:
            raise PermissionError("Write rejected: idempotency key is required.")
        if not hitl_approved:
            raise PermissionError("Write rejected: HITL approval required.")

    def _parse_response(self, body: bytes | str | None) -> dict[str, Any]:
        if not body:
            return {}
        if isinstance(body, bytes):
            body = body.decode(errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Schema drift or invalid JSON response: {body[:200]}") from exc

    def _request(self, method: str, url: str, payload: dict | None = None, extra_headers: dict[str, str] | None = None, timeout: int = 30, *, idempotency_key: str | None = None, hitl_approved: bool = False) -> dict[str, Any]:
        if _dry_run_enabled():
            raise DryRunSideEffectBlocked(f"Outbound connector call blocked during dry-run: {method} {url}")
        self._assert_write_allowed(method, idempotency_key=idempotency_key, hitl_approved=hitl_approved)
        if not self._circuit.allow_request():
            raise CircuitOpenBlocked(f"Circuit open for {self.__class__.__name__}; refusing outbound request")

        self._ensure_authenticated()
        self._rate_limiter.acquire()
        headers = {"Content-Type": "application/json", **self._auth_headers}
        if extra_headers:
            headers.update(extra_headers)
        if idempotency_key:
            headers.setdefault("Idempotency-Key", idempotency_key)
        data = json.dumps(payload).encode() if payload is not None else None
        backoff = self.INITIAL_BACKOFF_SECONDS
        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    result = self._parse_response(resp.read())
                    self._circuit.record_success()
                    return result
            except urllib.error.HTTPError as exc:
                status = exc.code
                if status == 429:
                    self._rate_limiter.handle_429(float(exc.headers.get("Retry-After", backoff)))
                    self._circuit.record_failure()
                    continue
                if status in self.NON_RETRYABLE_STATUS_CODES:
                    self._circuit.record_failure()
                    error_body = exc.read().decode(errors="replace")
                    envelope = build_error_envelope(correlation_id=self.correlation_id, workflow_run_id=self.workflow_run_id, schedule_run_id=self.schedule_run_id, skill=f"connector:{self.__class__.__name__.lower()}", severity="error", category="auth" if status in {401,403} else "connector", retryable=False, user_action_required=True, message="Connector request failed.", technical_detail=f"HTTP {status} {method} {url}: {redact_secrets(error_body)}", root_cause_hint="Invalid credentials, permissions, or request payload.", remediation="Verify connector credentials/permissions and retry.", source_exception=str(exc))
                    raise RuntimeError(json.dumps(envelope, sort_keys=True)) from exc
                if status in self.RETRYABLE_STATUS_CODES and attempt <= self.MAX_RETRIES:
                    self._circuit.record_failure()
                    time.sleep(backoff)
                    backoff = min(backoff * self.BACKOFF_MULTIPLIER, self.MAX_BACKOFF_SECONDS)
                    continue
                self._circuit.record_failure()
                raise RuntimeError(f"HTTP {status} {method} {url}") from exc
            except OSError:
                self._circuit.record_failure()
                if attempt <= self.MAX_RETRIES:
                    time.sleep(backoff)
                    backoff = min(backoff * self.BACKOFF_MULTIPLIER, self.MAX_BACKOFF_SECONDS)
                    continue
                raise
        raise RuntimeError(f"All {self.MAX_RETRIES} retries exhausted for {method} {url}")

    def _paginate(self, method: str, url: str, *, payload: dict | None = None, page_param: str = "page", cursor_param: str = "cursor", items_key: str = "items", max_pages: int = 100, timeout: int = 30) -> list[dict[str, Any]]:
        state = PaginationState()
        items: list[dict[str, Any]] = []
        while state.page <= max_pages:
            params = {page_param: state.page}
            if state.next_cursor:
                params[cursor_param] = state.next_cursor
            page_url = f"{url}{'&' if '?' in url else '?'}{urllib.parse.urlencode(params)}"
            try:
                data = self._request(method, page_url, payload=payload, timeout=timeout)
            except Exception:
                # partial-page recovery: continue with next page
                state.page += 1
                continue
            chunk = data.get(items_key, [])
            if isinstance(chunk, list):
                items.extend(chunk)
            state.next_cursor = data.get("next_cursor") or data.get("next")
            if not state.next_cursor and not chunk:
                break
            state.page += 1
        return items
