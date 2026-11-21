"""Simple e-commerce recommendation funnel arithmetic for lesson 1.1.3."""

from __future__ import annotations


def estimate_gmv(
    sessions: int,
    recommendation_click_rate: float,
    purchase_conversion_rate: float,
    average_order_value: float,
) -> float:
    """Estimate gross merchandise value under an explicitly simplified funnel."""
    if sessions < 0:
        raise ValueError("sessions must be non-negative")
    for name, rate in (
        ("recommendation_click_rate", recommendation_click_rate),
        ("purchase_conversion_rate", purchase_conversion_rate),
    ):
        if not 0.0 <= rate <= 1.0:
            raise ValueError(name + " must be in [0, 1]")
    if average_order_value < 0.0:
        raise ValueError("average_order_value must be non-negative")
    return sessions * recommendation_click_rate * purchase_conversion_rate * average_order_value


def apply_relative_lift(baseline: float, relative_lift: float) -> float:
    """Apply a relative change, not a percentage-point change."""
    if baseline < 0.0:
        raise ValueError("baseline must be non-negative")
    if relative_lift < -1.0:
        raise ValueError("relative_lift cannot reduce the result below zero")
    return baseline * (1.0 + relative_lift)


if __name__ == "__main__":
    print(estimate_gmv(1_000_000, 0.12, 0.04, 260.0))
