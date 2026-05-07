#!/usr/bin/env python3
"""
Scan a file, directory, or stdin payload for secrets and credentials.

Detects common patterns including API keys, tokens, passwords, private keys,
connection strings, and other sensitive values before they are transmitted
or committed.

Usage:
    python scan_for_secrets.py --file payload.json
    python scan_for_secrets.py --dir ./output/
    cat payload.txt | python scan_for_secrets.py --stdin
    python scan_for_secrets.py --file config.yaml --output-format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Secret patterns
# ---------------------------------------------------------------------------

# Each rule: (name, regex_pattern, severity, description)
SECRET_RULES: list[tuple[str, str, str, str]] = [
    # Private keys
    ("private-key-pem",
     r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
     "critical", "PEM private key block"),
    # Generic high-entropy tokens
    ("github-token",
     r"gh[ps]_[A-Za-z0-9]{36,}",
     "critical", "GitHub personal access token"),
    ("github-oauth",
     r"gho_[A-Za-z0-9]{36,}",
     "critical", "GitHub OAuth token"),
    ("openai-key",
     r"sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}",
     "critical", "OpenAI API key"),
    ("anthropic-key",
     r"sk-ant-[A-Za-z0-9\-_]{20,}",
     "critical", "Anthropic API key"),
    ("aws-access-key",
     r"AKIA[0-9A-Z]{16}",
     "critical", "AWS access key ID"),
    ("aws-secret-key",
     r"(?i)aws.{0,20}secret.{0,10}['\"]([A-Za-z0-9/+]{40})['\"]",
     "critical", "AWS secret access key"),
    ("stripe-key",
     r"sk_live_[A-Za-z0-9]{24,}",
     "critical", "Stripe live secret key"),
    ("stripe-restricted",
     r"rk_live_[A-Za-z0-9]{24,}",
     "high", "Stripe restricted key (live)"),
    ("slack-token",
     r"xox[baprs]-[A-Za-z0-9\-]{10,}",
     "critical", "Slack token"),
    ("jwt-token",
     r"eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
     "high", "JSON Web Token (JWT)"),
    # Passwords in common patterns
    ("password-assignment",
     r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
     "high", "Password value in assignment"),
    ("secret-assignment",
     r"(?i)(secret|api_secret|client_secret)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
     "high", "Secret value in assignment"),
    # Database connection strings
    ("postgres-dsn",
     r"postgresql://[^:]+:[^@]+@",
     "critical", "PostgreSQL connection string with credentials"),
    ("mysql-dsn",
     r"mysql://[^:]+:[^@]+@",
     "critical", "MySQL connection string with credentials"),
    ("redis-auth",
     r"redis://:[^@]+@",
     "high", "Redis connection string with password"),
    ("mongodb-dsn",
     r"mongodb(\+srv)?://[^:]+:[^@]+@",
     "critical", "MongoDB connection string with credentials"),
    # Generic bearer tokens in headers
    ("bearer-token",
     r"Authorization:\s*Bearer\s+[A-Za-z0-9\-_\.]{20,}",
     "high", "Bearer token in Authorization header"),
    # GCP credentials
    ("gcp-service-account",
     r'"type"\s*:\s*"service_account"',
     "critical", "GCP service account credential file"),
    # Sendgrid
    ("sendgrid-key",
     r"SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}",
     "critical", "SendGrid API key"),
    # Generic high-entropy string warning (lower severity)
    ("high-entropy-hex",
     r"(?<![A-Za-z0-9])[0-9a-f]{64}(?![A-Za-z0-9])",
     "medium", "High-entropy hex string (possible key/hash)"),
]

# Files to always skip
SKIP_EXTENSIONS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz"}
SKIP_NAMES = {"scan_for_secrets.py"}  # Don't flag ourselves


def _scan_text(text: str, source: str) -> list[dict]:
    """Scan text for secret patterns. Returns list of findings."""
    findings = []
    for name, pattern, severity, description in SECRET_RULES:
        for match in re.finditer(pattern, text):
            line_num = text[:match.start()].count("\n") + 1
            # Redact the matched value for safe reporting
            matched = match.group(0)
            redacted = matched[:6] + "..." + matched[-4:] if len(matched) > 12 else "***"
            findings.append({
                "rule": name,
                "severity": severity,
                "description": description,
                "source": source,
                "line": line_num,
                "match_preview": redacted,
            })
    return findings


def scan_text(text: str, source: str = "stdin") -> list[dict]:
    """Scan a text string for secrets."""
    return _scan_text(text, source)


def scan_file(path: Path) -> list[dict]:
    """Scan a single file for secrets."""
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return []
    if path.name in SKIP_NAMES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (PermissionError, OSError):
        return []
    return _scan_text(text, str(path))


def scan_directory(base: Path) -> list[dict]:
    """Recursively scan all files in a directory."""
    findings = []
    for p in base.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            findings.extend(scan_file(p))
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan files or stdin for secrets and credentials.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="File to scan")
    group.add_argument("--dir", help="Directory to scan recursively")
    group.add_argument("--stdin", action="store_true", help="Scan text from stdin")
    parser.add_argument(
        "--output-format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--min-severity", choices=["medium", "high", "critical"], default="medium",
        help="Minimum severity to report (default: medium)"
    )
    parser.add_argument(
        "--fail-on", choices=["medium", "high", "critical"], default="high",
        help="Exit non-zero if any finding at or above this severity (default: high)"
    )
    args = parser.parse_args()

    # Run scan
    if args.stdin:
        text = sys.stdin.read()
        findings = scan_text(text, source="stdin")
    elif args.file:
        findings = scan_file(Path(args.file))
    else:
        findings = scan_directory(Path(args.dir))

    # Filter by severity
    severity_order = {"medium": 0, "high": 1, "critical": 2}
    min_level = severity_order[args.min_severity]
    findings = [f for f in findings if severity_order.get(f["severity"], 0) >= min_level]

    # Output
    if args.output_format == "json":
        print(json.dumps({
            "total": len(findings),
            "findings": findings,
            "clean": len(findings) == 0,
        }, indent=2))
    else:
        if not findings:
            print("CLEAN: No secrets detected.")
        else:
            print(f"SECRETS DETECTED: {len(findings)} finding(s)\n")
            for f in findings:
                print(f"  [{f['severity'].upper()}] {f['rule']}")
                print(f"    Source: {f['source']} (line {f['line']})")
                print(f"    Match:  {f['match_preview']}")
                print(f"    Desc:   {f['description']}")
                print()

    # Exit code
    fail_level = severity_order[args.fail_on]
    has_failures = any(severity_order.get(f["severity"], 0) >= fail_level for f in findings)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()