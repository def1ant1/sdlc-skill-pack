#!/usr/bin/env python3
"""Naive relevance scorer for Phase 0 validation."""
import argparse, json

def score(query: str, text: str) -> float:
    terms = set(query.lower().split())
    words = set(text.lower().split())
    if not terms:
        return 0.0
    return round(len(terms & words) / len(terms), 3)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("text")
    a = p.parse_args()
    print(json.dumps({"score": score(a.query, a.text)}, indent=2))
