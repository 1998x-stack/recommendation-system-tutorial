"""Event validation and idempotent de-duplication for lesson 1.2.2."""

from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Iterable, Mapping

ALLOWED_EVENT_TYPES = {
    "impression", "click", "watch", "add_to_cart",
    "purchase", "hide", "dislike",
}
REQUIRED_FIELDS = ("event_id", "user_id", "item_id", "event_type", "event_time")


def normalize_event(event: Mapping[str, object]) -> dict[str, str]:
    """Validate required fields and normalize an offset-aware timestamp to UTC."""
    missing = [field for field in REQUIRED_FIELDS if not event.get(field)]
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))
    event_type = str(event["event_type"])
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError("unsupported event_type: " + event_type)
    timestamp = str(event["event_time"]).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        raise ValueError("event_time must include a timezone")
    normalized = parsed.astimezone(timezone.utc).isoformat()
    return {
        "event_id": str(event["event_id"]),
        "user_id": str(event["user_id"]),
        "item_id": str(event["item_id"]),
        "event_type": event_type,
        "event_time": normalized,
    }


def deduplicate_events(events: Iterable[Mapping[str, object]]) -> list[dict[str, str]]:
    """Keep the earliest normalized record for each event_id."""
    normalized = [normalize_event(event) for event in events]
    normalized.sort(key=lambda event: (event["event_time"], event["event_id"]))
    unique: dict[str, dict[str, str]] = {}
    for event in normalized:
        unique.setdefault(event["event_id"], event)
    return list(unique.values())


if __name__ == "__main__":
    sample = {
        "event_id": "e1", "user_id": "u1", "item_id": "i1",
        "event_type": "click", "event_time": "2026-11-20T10:00:00+08:00",
    }
    print(deduplicate_events([sample]))
