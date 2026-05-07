#!/usr/bin/env python3
"""
Validate AI discoverability for a URL or local HTML/Markdown file.

Checks:
  1. llms.txt present and valid
  2. Semantic structure (H1/H2/H3 hierarchy)
  3. Chunk-friendly formatting (no walls of text)
  4. robots.txt AI policy (no AI-blocking directives)
  5. Structured data (schema.org markup present)
  6. Capability manifest (/.well-known/ai-manifest.json)

Usage:
    python validate_ai_discovery.py --url https://example.com
    python validate_ai_discovery.py --file ./index.html
    python validate_ai_discovery.py --url https://example.com --output-format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse


def _fetch_url(url: str) -> Optional[str]:
    """Fetch URL content. Returns text or None on failure."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "ApotheonAIDiscoveryAuditor/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def _read_file(path: str) -> Optional[str]:
    """Read local file content."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def check_llms_txt(base_url: str) -> dict:
    """Check 1: llms.txt exists at domain root."""
    parsed = urlparse(base_url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"
    content = _fetch_url(llms_url)

    if content is None:
        return {"check": "llms.txt", "status": "FAIL", "detail": f"Not found at {llms_url}",
                "recommendation": f"Create and deploy llms.txt at {llms_url}"}

    issues = []
    if not re.search(r"^#\s+\S", content, re.MULTILINE):
        issues.append("missing '# Site Name' heading")
    if not re.search(r"^>", content, re.MULTILINE):
        issues.append("missing '> Description' blockquote")
    if content.find("Content Policy") == -1:
        issues.append("missing '## Content Policy' section")

    if issues:
        return {"check": "llms.txt", "status": "WARN",
                "detail": f"Found at {llms_url} but incomplete: {', '.join(issues)}",
                "recommendation": "Add missing required sections per llms-txt-patterns.md"}

    return {"check": "llms.txt", "status": "PASS",
            "detail": f"Found at {llms_url} with required sections"}


def check_semantic_structure(content: str) -> dict:
    """Check 2: H1/H2/H3 hierarchy is present and logical."""
    # Works for both HTML and Markdown
    if "<html" in content.lower() or "<body" in content.lower():
        h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
        h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.IGNORECASE | re.DOTALL)
        h3s = re.findall(r"<h3[^>]*>(.*?)</h3>", content, re.IGNORECASE | re.DOTALL)
    else:
        # Markdown
        h1s = re.findall(r"^#\s+.+", content, re.MULTILINE)
        h2s = re.findall(r"^##\s+.+", content, re.MULTILINE)
        h3s = re.findall(r"^###\s+.+", content, re.MULTILINE)

    issues = []
    if len(h1s) == 0:
        issues.append("no H1 found — every page needs exactly one H1")
    elif len(h1s) > 1:
        issues.append(f"multiple H1s found ({len(h1s)}) — use only one H1 per page")
    if len(h2s) == 0:
        issues.append("no H2 sections found — add H2 headings to create chunk boundaries")

    if issues:
        status = "FAIL" if len(h1s) == 0 else "WARN"
        return {"check": "semantic-structure", "status": status,
                "detail": "; ".join(issues),
                "recommendation": "Add H1/H2/H3 hierarchy to define natural chunk boundaries for AI retrieval"}

    return {"check": "semantic-structure", "status": "PASS",
            "detail": f"H1: {len(h1s)}, H2: {len(h2s)}, H3: {len(h3s)} — structure looks good"}


def check_chunk_friendliness(content: str) -> dict:
    """Check 3: No walls of text; paragraphs are chunk-sized."""
    # Strip HTML tags for text analysis
    text = re.sub(r"<[^>]+>", " ", content)
    text = re.sub(r"\s+", " ", text).strip()

    # Split on paragraph breaks
    if "<html" in content.lower():
        paragraphs = re.split(r"</p>|<br\s*/?>", content, flags=re.IGNORECASE)
    else:
        paragraphs = re.split(r"\n\n+", content)

    long_paragraphs = [p for p in paragraphs if len(p.split()) > 200]
    js_rendered = "document.getElementById" in content or "React.createElement" in content

    issues = []
    if long_paragraphs:
        issues.append(f"{len(long_paragraphs)} paragraph(s) exceed 200 words — may be split poorly by AI chunkers")
    if js_rendered:
        issues.append("JavaScript-rendered content detected — may not be indexed by AI crawlers")

    if issues:
        return {"check": "chunk-friendliness", "status": "WARN",
                "detail": "; ".join(issues),
                "recommendation": "Break long paragraphs into shorter sections; use SSR for JS content"}

    return {"check": "chunk-friendliness", "status": "PASS",
            "detail": "Paragraphs are within recommended length; no JS rendering issues detected"}


def check_robots_txt(base_url: str) -> dict:
    """Check 4: robots.txt does not block AI crawlers."""
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    content = _fetch_url(robots_url)

    if content is None:
        return {"check": "robots-txt", "status": "WARN",
                "detail": "robots.txt not found — this is acceptable but not ideal",
                "recommendation": "Add robots.txt to explicitly allow AI crawlers"}

    ai_crawlers = ["GPTBot", "Claude-Web", "PerplexityBot", "GoogleOther", "meta-externalagent",
                   "anthropic-ai", "Applebot-Extended"]
    blocked = []
    lines = content.splitlines()
    current_agent = None
    disallowed = set()
    for line in lines:
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            current_agent = line.split(":", 1)[1].strip()
            disallowed = set()
        elif line.lower().startswith("disallow:") and current_agent:
            path = line.split(":", 1)[1].strip()
            disallowed.add(path)
            if current_agent in ai_crawlers and path in ("/", "/*"):
                blocked.append(current_agent)

    if blocked:
        return {"check": "robots-txt", "status": "WARN",
                "detail": f"AI crawlers blocked: {', '.join(blocked)}",
                "recommendation": "Remove Disallow rules for AI crawlers to enable AI search discovery"}

    return {"check": "robots-txt", "status": "PASS",
            "detail": "No AI crawlers blocked in robots.txt"}


def check_structured_data(content: str) -> dict:
    """Check 5: schema.org structured data present."""
    has_json_ld = '"@context"' in content and "schema.org" in content
    has_microdata = 'itemtype="http://schema.org' in content or "itemtype='http://schema.org" in content
    has_rdfa = 'vocab="http://schema.org' in content

    if has_json_ld or has_microdata or has_rdfa:
        schema_type = "JSON-LD" if has_json_ld else ("Microdata" if has_microdata else "RDFa")
        return {"check": "structured-data", "status": "PASS",
                "detail": f"schema.org markup found ({schema_type})"}

    return {"check": "structured-data", "status": "WARN",
            "detail": "No schema.org structured data detected",
            "recommendation": "Add JSON-LD structured data (Organization, WebSite, FAQPage, or Article)"}


def check_capability_manifest(base_url: str) -> dict:
    """Check 6: AI capability manifest present at /.well-known/ai-manifest.json."""
    parsed = urlparse(base_url)
    manifest_url = f"{parsed.scheme}://{parsed.netloc}/.well-known/ai-manifest.json"
    content = _fetch_url(manifest_url)

    if content is None:
        return {"check": "capability-manifest", "status": "WARN",
                "detail": f"Not found at {manifest_url}",
                "recommendation": "Create ai-manifest.json per shared/frameworks/ai-discovery/capability-manifest.md"}

    try:
        manifest = json.loads(content)
        missing = [f for f in ["name", "capabilities", "limitations"] if f not in manifest]
        if missing:
            return {"check": "capability-manifest", "status": "WARN",
                    "detail": f"Found but missing required fields: {', '.join(missing)}",
                    "recommendation": "Add missing fields to ai-manifest.json"}
        return {"check": "capability-manifest", "status": "PASS",
                "detail": f"Found at {manifest_url} with required fields"}
    except json.JSONDecodeError:
        return {"check": "capability-manifest", "status": "FAIL",
                "detail": "Found but not valid JSON",
                "recommendation": "Fix JSON syntax in ai-manifest.json"}


def audit(url: Optional[str] = None, file: Optional[str] = None) -> dict:
    """Run all AI discoverability checks and return a structured report."""
    findings = []

    # Load content
    content = ""
    if file:
        content = _read_file(file) or ""
        base_url = "https://example.com"  # placeholder for file-based checks
    elif url:
        content = _fetch_url(url) or ""
        base_url = url
    else:
        raise ValueError("Either url or file must be provided")

    # Run checks
    if url:
        findings.append(check_llms_txt(base_url))
        findings.append(check_robots_txt(base_url))
        findings.append(check_capability_manifest(base_url))

    if content:
        findings.append(check_semantic_structure(content))
        findings.append(check_chunk_friendliness(content))
        if url:
            findings.append(check_structured_data(content))
    else:
        findings.append({"check": "content-fetch", "status": "FAIL",
                         "detail": "Could not fetch content for analysis",
                         "recommendation": "Check that the URL is accessible"})

    # Score: PASS=100, WARN=50, FAIL=0 per check
    status_scores = {"PASS": 100, "WARN": 50, "FAIL": 0}
    score = round(sum(status_scores.get(f["status"], 0) for f in findings) / max(len(findings), 1))

    recommendations = [
        f.get("recommendation", "")
        for f in findings
        if f["status"] != "PASS" and f.get("recommendation")
    ]

    return {
        "target": url or file,
        "score": score,
        "findings": findings,
        "recommendations": recommendations,
        "summary": (
            f"{sum(1 for f in findings if f['status'] == 'PASS')} PASS, "
            f"{sum(1 for f in findings if f['status'] == 'WARN')} WARN, "
            f"{sum(1 for f in findings if f['status'] == 'FAIL')} FAIL"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit a URL or file for AI search discoverability.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL to audit")
    group.add_argument("--file", help="Local HTML or Markdown file to audit")
    parser.add_argument(
        "--output-format", choices=["json", "text"], default="text",
        help="Output format (default: text)"
    )
    args = parser.parse_args()

    result = audit(url=args.url, file=args.file)

    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\nAI Discoverability Audit")
        print(f"{'─' * 40}")
        print(f"Target: {result['target']}")
        print(f"Score:  {result['score']}/100")
        print(f"Result: {result['summary']}")
        print()
        print("Findings:")
        for f in result["findings"]:
            icon = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}.get(f["status"], "?")
            print(f"  [{f['status']}] {icon} {f['check']}: {f['detail']}")
        if result["recommendations"]:
            print()
            print("Recommendations:")
            for i, rec in enumerate(result["recommendations"], 1):
                print(f"  {i}. {rec}")
        print()

    sys.exit(0 if result["score"] >= 70 else 1)


if __name__ == "__main__":
    main()