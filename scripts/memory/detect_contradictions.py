#!/usr/bin/env python3
"""Detect contradictions between candidate retrieval context and semantic memory."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SEMANTIC = Path('.apotheon/memory/semantic.jsonl')


def _load_semantic() -> list[dict]:
    if not SEMANTIC.exists():
        return []
    return [json.loads(line) for line in SEMANTIC.read_text(encoding='utf-8').splitlines() if line.strip()]


def detect(candidates: list[dict]) -> dict:
    semantic = _load_semantic()
    by_entity: dict[tuple[str, str], str] = {}
    for fact in semantic:
        for ref in fact.get('entity_refs', []):
            by_entity[(ref.get('entity_type', ''), ref.get('entity_id', ''))] = fact.get('content', '')

    contradictions = []
    for item in candidates:
        content = item.get('content', '').lower()
        for ref in item.get('entity_refs', []):
            key = (ref.get('entity_type', ''), ref.get('entity_id', ''))
            fact_content = by_entity.get(key, '').lower()
            if fact_content and fact_content != content:
                contradictions.append({
                    'candidate_event_id': item.get('event_id', ''),
                    'entity': {'entity_type': key[0], 'entity_id': key[1]},
                    'semantic_fact': by_entity[key],
                    'candidate_fact': item.get('content', '')
                })

    return {'blocked': len(contradictions) > 0, 'contradictions': contradictions}


if __name__ == '__main__':
    candidates = json.load(sys.stdin)
    print(json.dumps(detect(candidates), indent=2))
