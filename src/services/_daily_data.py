from __future__ import annotations

from datetime import date

import pandas as pd

from src.utils.dates import get_month_days


def merge_daily_data(
    data: pd.DataFrame,
    month_start: date,
    next_month: date,
    value_columns: list[str],
) -> pd.DataFrame:
    """Fill missing dates with zero values so chart timelines stay complete."""
    days = get_month_days(month_start, next_month)

    if data.empty:
        data = pd.DataFrame(columns=["report_date", *value_columns])

    data = data.copy()
    data["report_date"] = pd.to_datetime(data["report_date"]).dt.date

    merged = days.merge(data, on="report_date", how="left")
    for column in value_columns:
        merged[column] = pd.to_numeric(merged[column], errors="coerce").fillna(0)

    return merged