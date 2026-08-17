from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.repositories import ReportingRepository, get_reporting_repository
from src.services.customers import load_customer_trends, load_top_customers
from src.services.orders import load_order_trends


@dataclass(frozen=True)
class DashboardData:
    order_trends: pd.DataFrame
    customer_trends: pd.DataFrame
    top_customers: pd.DataFrame


def load_dashboard_data(
    month_start: date,
    next_month: date,
    repository: ReportingRepository | None = None,
) -> DashboardData:
    """Load all dashboard datasets needed by the page."""
    repository = repository or get_reporting_repository()
    return DashboardData(
        order_trends=load_order_trends(month_start, next_month, repository),
        customer_trends=load_customer_trends(month_start, next_month, repository),
        top_customers=load_top_customers(month_start, next_month, repository),
    )
