"""Transparent toy ranking example for lesson 1.1.1."""

from __future__ import annotations

from math import isfinite
from typing import Iterable, Mapping


def score_candidate(
    user_interests: set[str],
    item_tags: set[str],
    quality: float,
    freshness: float = 0.0,
    blocked: bool = False,
) -> float:
    """Return a transparent heuristic score; this is not a trained model."""
    if not 0.0 <= quality <= 1.0:
        raise ValueError("quality must be in [0, 1]")
    if not 0.0 <= freshness <= 1.0:
        raise ValueError("freshness must be in [0, 1]")
    if blocked:
        return float("-inf")
    overlap = len(user_interests & item_tags) / max(len(user_interests), 1)
    return 0.65 * overlap + 0.25 * quality + 0.10 * freshness


def rank_candidates(
    user_interests: set[str],
    items: Iterable[Mapping[str, object]],
    blocked_ids: set[str] | None = None,
) -> list[str]:
    """Rank item dictionaries and return their IDs in descending score order."""
    blocked_ids = blocked_ids or set()
    scored: list[tuple[float, str]] = []
    for item in items:
        item_id = str(item["id"])
        score = score_candidate(
            user_interests=user_interests,
            item_tags=set(item["tags"]),
            quality=float(item["quality"]),
            freshness=float(item.get("freshness", 0.0)),
            blocked=item_id in blocked_ids,
        )
        if isfinite(score):
            scored.append((score, item_id))
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [item_id for _, item_id in scored]


if __name__ == "__main__":
    sample_items = [
        {"id": "a", "tags": {"science"}, "quality": 0.9, "freshness": 0.8},
        {"id": "b", "tags": {"fashion"}, "quality": 1.0, "freshness": 1.0},
        {"id": "c", "tags": {"history", "science"}, "quality": 0.8, "freshness": 0.3},
    ]
    print(rank_candidates({"science", "history"}, sample_items, {"b"}))
