from __future__ import annotations

from datetime import date
from typing import Protocol

import pandas as pd


class ReportingRepository(Protocol):
    """Data-access contract used by the reporting services."""

    def get_order_trends(self, month_start: date, next_month: date) -> pd.DataFrame: ...

    def get_customer_trends(
        self, month_start: date, next_month: date
    ) -> pd.DataFrame: ...

    def get_top_customers(
        self, month_start: date, next_month: date
    ) -> pd.DataFrame: ...

    def get_top_menu_items_by_day(
        self, month_start: date, next_month: date
    ) -> pd.DataFrame: ...

    def get_top_menu_items_by_month(
        self, month_start: date, next_month: date
    ) -> pd.DataFrame: ...

    def get_menu_item_filter_options(self) -> pd.DataFrame: ...

    def get_active_categories(self) -> pd.DataFrame: ...

    def get_menu_item_sales(
        self,
        date_from: date,
        date_to: date,
        *,
        menu_item_id: int | None = None,
        branch_id: int | None = None,
        category_id: int | None = None,
    ) -> pd.DataFrame: ...

    def get_top_menu_items_for_period(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame: ...

    def get_campaign_menu_items(self) -> pd.DataFrame: ...

    def get_campaigns(
        self,
        *,
        campaign: str = "",
        menu_item_id: int | None = None,
        start_date: date | None = None,
    ) -> pd.DataFrame: ...

    def get_active_branches(self) -> pd.DataFrame: ...

    def get_daily_reports(
        self,
        date_from: date,
        date_to: date,
        *,
        branch_id: int | None = None,
        status: str | None = None,
    ) -> pd.DataFrame: ...
