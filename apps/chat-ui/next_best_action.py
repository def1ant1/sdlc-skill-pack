"""Next best action surfaces for chat UI."""

from dataclasses import dataclass
from typing import List


@dataclass
class NextBestAction:
    title: str
    expected_impact: str
    effort: str
    urgency: str
    confidence: float
    provenance: list[str]
    linked_artifacts: list[str]


def rank_next_actions(actions: List[NextBestAction]) -> List[NextBestAction]:
    """Rank by urgency/impact with confidence as tie-breaker."""
    urgency_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(actions, key=lambda a: (urgency_rank.get(a.urgency, 9), -a.confidence))
