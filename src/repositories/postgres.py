from __future__ import annotations

from datetime import date

import pandas as pd

from src.queries.campaigns import fetch_campaign_menu_items, fetch_campaigns
from src.queries.customers import fetch_customer_trends, fetch_top_customers
from src.queries.daily_reports import fetch_active_branches, fetch_daily_reports
from src.queries.menuitems import (
    fetch_active_categories,
    fetch_menu_item_filter_options,
    fetch_menu_item_sales,
    fetch_top_menu_items_by_day,
    fetch_top_menu_items_by_month,
    fetch_top_menu_items_for_period,
)
from src.queries.orders import fetch_order_trends


class PostgresReportingRepository:
    """Reporting repository backed by the current Cashier PostgreSQL schema."""

    def get_order_trends(self, month_start: date, next_month: date) -> pd.DataFrame:
        return fetch_order_trends(month_start, next_month)

    def get_customer_trends(self, month_start: date, next_month: date) -> pd.DataFrame:
        return fetch_customer_trends(month_start, next_month)

    def get_top_customers(self, month_start: date, next_month: date) -> pd.DataFrame:
        return fetch_top_customers(month_start, next_month)

    def get_top_menu_items_by_day(
        self, month_start: date, next_month: date
    ) -> pd.DataFrame:
        return fetch_top_menu_items_by_day(month_start, next_month)

    def get_top_menu_items_by_month(
        self, month_start: date, next_month: date
    ) -> pd.DataFrame:
        return fetch_top_menu_items_by_month(month_start, next_month)

    def get_menu_item_filter_options(self) -> pd.DataFrame:
        return fetch_menu_item_filter_options()

    def get_active_categories(self) -> pd.DataFrame:
        return fetch_active_categories()

    def get_menu_item_sales(
        self,
        date_from: date,
        date_to: date,
        *,
        menu_item_id: int | None = None,
        branch_id: int | None = None,
        category_id: int | None = None,
    ) -> pd.DataFrame:
        return fetch_menu_item_sales(
            date_from,
            date_to,
            menu_item_id=menu_item_id,
            branch_id=branch_id,
            category_id=category_id,
        )

    def get_top_menu_items_for_period(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame:
        return fetch_top_menu_items_for_period(date_from, date_to)

    def get_campaign_menu_items(self) -> pd.DataFrame:
        return fetch_campaign_menu_items()

    def get_campaigns(
        self,
        *,
        campaign: str = "",
        menu_item_id: int | None = None,
        start_date: date | None = None,
    ) -> pd.DataFrame:
        return fetch_campaigns(
            campaign=campaign,
            menu_item_id=menu_item_id,
            start_date=start_date,
        )

    def get_active_branches(self) -> pd.DataFrame:
        return fetch_active_branches()

    def get_daily_reports(
        self,
        date_from: date,
        date_to: date,
        *,
        branch_id: int | None = None,
        status: str | None = None,
    ) -> pd.DataFrame:
        return fetch_daily_reports(
            date_from,
            date_to,
            branch_id=branch_id,
            status=status,
        )
