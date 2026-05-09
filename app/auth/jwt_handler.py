"""
app/auth/jwt_handler.py — JWT token issue and verification.

Uses HS256 for dev; switch JWT_ALGORITHM=RS256 and provide
JWT_PUBLIC_KEY / JWT_PRIVATE_KEY env vars for production.
"""
from __future__ import annotations

import time
from typing import Any

from app.config import get_settings

settings = get_settings()

try:
    import jwt as pyjwt
    _HAS_JWT = True
except ImportError:
    _HAS_JWT = False

# Fallback: stdlib-based minimal JWT (HS256 only) when PyJWT not installed
import base64
import hashlib
import hmac
import json


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)


def _hs256_sign(header_b64: str, payload_b64: str, secret: str) -> str:
    msg = f"{header_b64}.{payload_b64}".encode()
    sig = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
    return _b64url_encode(sig)


def issue_token(
    user_id: str,
    org_id: str,
    role: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Issue a JWT for the given user."""
    now = int(time.time())
    payload = {
        "sub": user_id,
        "org": org_id,
        "role": role,
        "iat": now,
        "exp": now + settings.jwt_expire_minutes * 60,
        **(extra_claims or {}),
    }

    if _HAS_JWT:
        return pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    # Stdlib fallback (HS256 only)
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = _b64url_encode(json.dumps(payload).encode())
    sig = _hs256_sign(header, body, settings.jwt_secret)
    return f"{header}.{body}.{sig}"


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT. Raises ValueError on failure."""
    if _HAS_JWT:
        try:
            return pyjwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except Exception as exc:
            raise ValueError(f"Invalid token: {exc}") from exc

    # Stdlib fallback
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token")
        header_b64, body_b64, sig = parts
        expected_sig = _hs256_sign(header_b64, body_b64, settings.jwt_secret)
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Invalid signature")
        payload = json.loads(_b64url_decode(body_b64))
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        return payload
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Invalid token: {exc}") from exc
