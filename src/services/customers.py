from __future__ import annotations

from datetime import date

import pandas as pd

from src.repositories import ReportingRepository, get_reporting_repository
from src.services._daily_data import merge_daily_data


def load_customer_trends(
    month_start: date,
    next_month: date,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    """Load customer trends and ensure all days in the month are represented."""
    repository = repository or get_reporting_repository()
    data = repository.get_customer_trends(month_start, next_month)
    merged = merge_daily_data(
        data,
        month_start,
        next_month,
        ["new_customers", "existing_customers"],
    )
    merged["new_customers"] = merged["new_customers"].astype(int)
    merged["existing_customers"] = merged["existing_customers"].astype(int)
    return merged


def load_top_customers(
    month_start: date,
    next_month: date,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    """Load top customers without additional reshaping."""
    repository = repository or get_reporting_repository()
    return repository.get_top_customers(month_start, next_month)
