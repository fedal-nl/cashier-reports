from __future__ import annotations

from datetime import date

import pandas as pd

from src.queries.customers import fetch_customer_trends, fetch_top_customers
from src.services._daily_data import merge_daily_data


def load_customer_trends(month_start: date, next_month: date) -> pd.DataFrame:
    """Load customer trends and ensure all days in the month are represented."""
    data = fetch_customer_trends(month_start, next_month)
    merged = merge_daily_data(
        data,
        month_start,
        next_month,
        ["new_customers", "existing_customers"],
    )
    merged["new_customers"] = merged["new_customers"].astype(int)
    merged["existing_customers"] = merged["existing_customers"].astype(int)
    return merged


def load_top_customers(month_start: date, next_month: date) -> pd.DataFrame:
    """Load top customers without additional reshaping."""
    return fetch_top_customers(month_start, next_month)