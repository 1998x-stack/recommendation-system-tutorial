"""A small candidate scoring and list re-ranking example for lesson 1.2.1."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("user and item vectors must have the same dimension")
    return sum(float(a) * float(b) for a, b in zip(left, right))


def rank_items(
    user_vector: Sequence[float],
    items: Iterable[Mapping[str, object]],
    blocked_ids: set[str] | None = None,
    max_per_category: int | None = None,
) -> list[str]:
    """Rank by dot product, then apply a simple per-category list constraint."""
    if max_per_category is not None and max_per_category < 1:
        raise ValueError("max_per_category must be positive")
    blocked_ids = blocked_ids or set()
    scored = []
    for item in items:
        item_id = str(item["id"])
        if item_id in blocked_ids:
            continue
        score = dot(user_vector, item["vector"])
        scored.append((score, item_id, str(item["category"])))
    scored.sort(key=lambda row: -row[0])

    counts: dict[str, int] = defaultdict(int)
    result = []
    for _, item_id, category in scored:
        if max_per_category is not None and counts[category] >= max_per_category:
            continue
        result.append(item_id)
        counts[category] += 1
    return result


if __name__ == "__main__":
    user = [0.8, 0.1, 0.7]
    items = [
        {"id": "video-a", "category": "video", "vector": [0.9, 0.0, 0.6]},
        {"id": "video-b", "category": "video", "vector": [0.8, 0.1, 0.6]},
        {"id": "article-c", "category": "article", "vector": [0.7, 0.2, 0.8]},
    ]
    print(rank_items(user, items, max_per_category=1))
