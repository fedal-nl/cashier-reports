from __future__ import annotations

from datetime import date

import pandas as pd

from src.queries.menuitems import fetch_top_menu_items_by_day, fetch_top_menu_items_by_month


def load_top_menu_items_by_day(month_start: date, next_month: date) -> pd.DataFrame:
    """Load top menu items without additional reshaping."""
    return fetch_top_menu_items_by_day(month_start, next_month)


def load_top_menu_items_by_month(month_start: date, next_month: date) -> pd.DataFrame:
    """Load monthly top menu items without additional reshaping."""
    return fetch_top_menu_items_by_month(month_start, next_month)