#!/usr/bin/env python3
"""
mtls_client.py — mTLS (mutual TLS) certificate authentication for connectors.

Wraps Python's ssl module to create an SSLContext with client certificate
and private key loaded from files or PEM strings.

Used by: on-premise connectors, Kafka, some enterprise ITSM integrations.

Environment variables (optional overrides):
    MTLS_CERT_FILE   Path to client certificate (PEM)
    MTLS_KEY_FILE    Path to private key (PEM)
    MTLS_CA_FILE     Path to CA bundle for server verification (PEM)
"""
from __future__ import annotations

import os
import ssl
import tempfile
from pathlib import Path


class MTLSContext:
    """
    Build and hold an ssl.SSLContext for mTLS connections.

    Usage::

        ctx = MTLSContext.from_files(
            cert_file="/certs/client.pem",
            key_file="/certs/client.key",
            ca_file="/certs/ca.pem",
        )
        # Pass ctx.ssl_context to urllib.request.urlopen(req, context=ctx.ssl_context)
    """

    def __init__(self, ssl_context: ssl.SSLContext):
        self.ssl_context = ssl_context

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_files(
        cls,
        cert_file: str | Path,
        key_file: str | Path,
        ca_file: str | Path | None = None,
    ) -> "MTLSContext":
        """Load cert/key from files on disk."""
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if ca_file:
            ctx.load_verify_locations(cafile=str(ca_file))
        ctx.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
        return cls(ctx)

    @classmethod
    def from_pem_strings(
        cls,
        cert_pem: str,
        key_pem: str,
        ca_pem: str | None = None,
    ) -> "MTLSContext":
        """Load cert/key from PEM strings (e.g. fetched from Vault)."""
        # Write to temp files because ssl.SSLContext requires file paths
        with tempfile.TemporaryDirectory() as tmpdir:
            cert_path = Path(tmpdir) / "client.pem"
            key_path = Path(tmpdir) / "client.key"
            cert_path.write_text(cert_pem)
            key_path.write_text(key_pem)

            ca_path: Path | None = None
            if ca_pem:
                ca_path = Path(tmpdir) / "ca.pem"
                ca_path.write_text(ca_pem)

            return cls.from_files(cert_path, key_path, ca_path)

    @classmethod
    def from_env(cls) -> "MTLSContext":
        """
        Build context from environment variables:
          MTLS_CERT_FILE, MTLS_KEY_FILE, MTLS_CA_FILE (optional).
        """
        cert = os.environ.get("MTLS_CERT_FILE", "")
        key = os.environ.get("MTLS_KEY_FILE", "")
        ca = os.environ.get("MTLS_CA_FILE", "")
        if not cert or not key:
            raise EnvironmentError(
                "MTLS_CERT_FILE and MTLS_KEY_FILE must be set for mTLS auth"
            )
        return cls.from_files(cert, key, ca or None)