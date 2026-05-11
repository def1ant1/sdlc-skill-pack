from __future__ import annotations

import os


def resolve_provider(*, dry_run: bool) -> str:
    """Return provider for runtime execution.

    Dry-run always uses local stub provider to guarantee no external calls.
    Live mode allows explicit provider allow-list only.
    """
    if dry_run:
        return "local-stub"

    provider = os.environ.get("APOTHEON_PROVIDER", "anthropic").strip().lower()
    allowed = {"anthropic", "local"}
    if provider not in allowed:
        raise ValueError(f"Provider '{provider}' is not permitted. Allowed: {sorted(allowed)}")
    return provider
