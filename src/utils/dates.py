from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


def get_current_month_bounds() -> tuple[date, date]:
    """Return the first day of the current month and the first day of next month."""
    month_start = date.today().replace(day=1)

    if month_start.month == 12:
        next_month = month_start.replace(
            year=month_start.year + 1,
            month=1,
        )
    else:
        next_month = month_start.replace(month=month_start.month + 1)

    return month_start, next_month


def get_month_days(month_start: date, next_month: date) -> pd.DataFrame:
    """Create one row per day in the selected month range for complete trend charts."""
    days = pd.date_range(
        start=month_start,
        end=next_month - timedelta(days=1),
        freq="D",
    )
    return pd.DataFrame({"report_date": days.date})
