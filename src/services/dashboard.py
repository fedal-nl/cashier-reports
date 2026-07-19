from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.services.customers import load_customer_trends, load_top_customers
from src.services.menuitems import load_top_menu_items_by_day, load_top_menu_items_by_month
from src.services.orders import load_order_trends


@dataclass(frozen=True)
class DashboardData:
    order_trends: pd.DataFrame
    customer_trends: pd.DataFrame
    top_customers: pd.DataFrame
    menu_items_by_day: pd.DataFrame
    menu_items_by_month: pd.DataFrame


def load_dashboard_data(month_start: date, next_month: date) -> DashboardData:
    """Load all dashboard datasets needed by the page."""
    return DashboardData(
        order_trends=load_order_trends(month_start, next_month),
        customer_trends=load_customer_trends(month_start, next_month),
        top_customers=load_top_customers(month_start, next_month),
        menu_items_by_day=load_top_menu_items_by_day(month_start, next_month),
        menu_items_by_month=load_top_menu_items_by_month(month_start, next_month),
    )