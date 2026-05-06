#!/usr/bin/env python3
"""Simple extractive summarizer placeholder for Phase 0."""
import sys
text = sys.stdin.read().strip()
sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
print('. '.join(sentences[:5]) + ('.' if sentences else ''))
