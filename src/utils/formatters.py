from __future__ import annotations

from decimal import Decimal


def money(value: Decimal | float | int | str) -> str:
    """Format revenue values as Iraqi dinar style whole-number currency."""
    amount = float(value or 0)
    return f"{amount:,.0f} د.ع"