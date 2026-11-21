"""Expected watch-time calculations for lesson 1.1.2."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def expected_watch_time(
    click_probability: float,
    conditional_watch_seconds: float,
) -> float:
    """Expected watch seconds per impression in a simple two-part model."""
    if not 0.0 <= click_probability <= 1.0:
        raise ValueError("click_probability must be in [0, 1]")
    if conditional_watch_seconds < 0.0:
        raise ValueError("conditional_watch_seconds must be non-negative")
    return click_probability * conditional_watch_seconds


def rank_impressions(
    impressions: Iterable[Mapping[str, object]],
) -> list[str]:
    """Rank toy impressions by expected watch time, not by click probability."""
    scored = []
    for item in impressions:
        score = expected_watch_time(
            float(item["click_probability"]),
            float(item["conditional_watch_seconds"]),
        )
        scored.append((score, str(item["video_id"])))
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [video_id for _, video_id in scored]


if __name__ == "__main__":
    print(expected_watch_time(0.20, 180.0))
