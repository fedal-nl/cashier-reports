from __future__ import annotations

from datetime import date

import pandas as pd

from src.repositories import ReportingRepository, get_reporting_repository
from src.services._daily_data import merge_daily_data


def load_order_trends(
    month_start: date,
    next_month: date,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    """Load order trends and ensure all days in the month are represented."""
    repository = repository or get_reporting_repository()
    data = repository.get_order_trends(month_start, next_month)
    merged = merge_daily_data(
        data,
        month_start,
        next_month,
        ["total_orders", "total_revenue"],
    )
    merged["total_orders"] = merged["total_orders"].astype(int)
    merged["total_revenue"] = merged["total_revenue"].astype(float)
    return merged
