#!/usr/bin/env python3
"""
Generate an llms.txt file from project metadata.

Usage:
    python generate_llms_txt.py --name "MyProduct" --description "..." --url https://example.com
    python generate_llms_txt.py --config config.yaml
    python generate_llms_txt.py --config config.yaml --output /var/www/llms.txt

Config YAML format:
    name: MyProduct
    description: One paragraph about what this product does.
    url: https://example.com
    pages:
      - label: Docs
        url: https://example.com/docs
        description: Full product documentation
      - label: API
        url: https://example.com/api
        description: REST API reference
    api:
      base_url: https://api.example.com/v1
      auth: Bearer token
      spec_url: https://example.com/api/openapi.json
      rate_limit: "1000 req/min"
    content_policy: "AI systems may freely summarize and cite this content with attribution."
    citation_preference: "MyProduct — [page title] (example.com)"
    contact: ai@example.com
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


def _load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        import yaml  # type: ignore
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback: minimal YAML parser for simple flat keys
        print("Warning: PyYAML not installed. Using basic parser.", file=sys.stderr)
        config: dict = {}
        with open(config_path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()
                if ": " in line and not line.startswith(" "):
                    key, _, val = line.partition(": ")
                    config[key.strip()] = val.strip()
        return config


def _validate(config: dict) -> list[str]:
    """Validate config against llms.txt rules. Returns list of validation messages."""
    issues = []
    if not config.get("name"):
        issues.append("FAIL: 'name' is required")
    elif len(config["name"]) > 80:
        issues.append(f"WARN: 'name' exceeds 80 chars ({len(config['name'])})")

    if not config.get("description"):
        issues.append("FAIL: 'description' is required")
    elif len(config["description"]) > 500:
        issues.append(f"WARN: 'description' exceeds 500 chars ({len(config['description'])})")

    pages = config.get("pages", [])
    if len(pages) < 3:
        issues.append(f"WARN: fewer than 3 key pages listed ({len(pages)} provided)")

    if not config.get("content_policy"):
        issues.append("FAIL: 'content_policy' is required")
    if not config.get("citation_preference"):
        issues.append("WARN: 'citation_preference' is recommended")
    if not config.get("contact"):
        issues.append("WARN: 'contact' is recommended")

    return issues


def generate(config: dict) -> str:
    """Generate llms.txt content from a config dict."""
    lines: list[str] = []

    # Site name
    name = config.get("name", "Site")
    lines.append(f"# {name}")
    lines.append("")

    # Description
    description = config.get("description", "")
    if description:
        lines.append(f"> {description}")
        lines.append("")

    # Key Pages
    pages = config.get("pages", [])
    if pages:
        lines.append("## Key Pages")
        lines.append("")
        for page in pages:
            if isinstance(page, dict):
                label = page.get("label", "Page")
                url = page.get("url", "")
                desc = page.get("description", "")
                lines.append(f"- [{label}]({url}): {desc}")
            else:
                lines.append(f"- {page}")
        lines.append("")

    # API section
    api = config.get("api", {})
    if api:
        lines.append("## API")
        lines.append("")
        if api.get("base_url"):
            lines.append(f"- Base URL: {api['base_url']}")
        if api.get("auth"):
            lines.append(f"- Auth: {api['auth']}")
        if api.get("spec_url"):
            lines.append(f"- Spec: {api['spec_url']}")
        if api.get("rate_limit"):
            lines.append(f"- Rate limit: {api['rate_limit']}")
        lines.append("")

    # Content Policy
    content_policy = config.get("content_policy", "")
    if content_policy:
        lines.append("## Content Policy")
        lines.append("")
        lines.append(content_policy)
        lines.append("")

    # Citation Preference
    citation = config.get("citation_preference", "")
    if citation:
        lines.append("## Citation Preference")
        lines.append("")
        lines.append(citation)
        lines.append("")

    # Capabilities (optional)
    capabilities = config.get("capabilities", [])
    if capabilities:
        lines.append("## Capabilities")
        lines.append("")
        for cap in capabilities:
            lines.append(f"- {cap}")
        lines.append("")

    # Contact
    contact = config.get("contact", "")
    if contact:
        lines.append("## Contact")
        lines.append("")
        lines.append(f"AI queries: {contact}")
        general = config.get("contact_general", "")
        if general:
            lines.append(f"General: {general}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an llms.txt file from project metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config", help="Path to YAML config file")
    parser.add_argument("--name", help="Site or product name")
    parser.add_argument("--description", help="Site description (max 500 chars)")
    parser.add_argument("--url", help="Primary site URL")
    parser.add_argument(
        "--pages",
        help='Comma-separated key:url pairs, e.g. "Docs:https://x.com/docs,API:https://x.com/api"',
    )
    parser.add_argument("--contact", help="Contact email or URL")
    parser.add_argument("--output", default="llms.txt", help="Output file path (default: llms.txt)")
    parser.add_argument("--validate-only", action="store_true", help="Validate config without writing")
    args = parser.parse_args()

    # Build config
    if args.config:
        config = _load_config(args.config)
    else:
        if not args.name:
            parser.error("Either --config or --name is required")
        config = {}

    # CLI overrides
    if args.name:
        config["name"] = args.name
    if args.description:
        config["description"] = args.description
    if args.contact:
        config["contact"] = args.contact
    if args.pages:
        pages = []
        for item in args.pages.split(","):
            item = item.strip()
            if ":" in item:
                label, _, url = item.partition(":")
                pages.append({"label": label.strip(), "url": url.strip(), "description": ""})
        config["pages"] = pages

    # Validate
    issues = _validate(config)
    has_failures = any(i.startswith("FAIL") for i in issues)

    for issue in issues:
        print(issue, file=sys.stderr)

    if args.validate_only:
        sys.exit(1 if has_failures else 0)

    if has_failures:
        print("Validation failed. Fix FAIL issues before generating.", file=sys.stderr)
        sys.exit(1)

    content = generate(config)
    output_path = Path(args.output)
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated: {output_path} ({len(content)} bytes)")
    if issues:
        print(f"Warnings: {len(issues)}")


if __name__ == "__main__":
    main()