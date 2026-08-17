from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import DEFAULT, patch

from src.repositories.factory import get_reporting_repository
from src.repositories.postgres import PostgresReportingRepository


class RepositoryFactoryTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_reporting_repository.cache_clear()

    def test_postgres_is_the_default_repository(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            repository = get_reporting_repository()

        self.assertIsInstance(repository, PostgresReportingRepository)

    def test_unknown_repository_is_rejected(self) -> None:
        with (
            patch.dict(os.environ, {"REPORTS_REPOSITORY": "unknown"}),
            self.assertRaisesRegex(ValueError, "Unsupported reporting repository"),
        ):
            get_reporting_repository()


class PostgresRepositoryTests(unittest.TestCase):
    def test_methods_forward_to_postgres_queries(self) -> None:
        repository = PostgresReportingRepository()
        start = date(2026, 8, 1)
        end = date(2026, 8, 7)

        with patch.multiple(
            "src.repositories.postgres",
            fetch_order_trends=DEFAULT,
            fetch_customer_trends=DEFAULT,
            fetch_top_customers=DEFAULT,
            fetch_top_menu_items_by_day=DEFAULT,
            fetch_top_menu_items_by_month=DEFAULT,
            fetch_menu_item_filter_options=DEFAULT,
            fetch_active_categories=DEFAULT,
            fetch_menu_item_sales=DEFAULT,
            fetch_top_menu_items_for_period=DEFAULT,
            fetch_campaign_menu_items=DEFAULT,
            fetch_campaigns=DEFAULT,
            fetch_active_branches=DEFAULT,
            fetch_daily_reports=DEFAULT,
        ) as queries:
            repository.get_order_trends(start, end)
            repository.get_customer_trends(start, end)
            repository.get_top_customers(start, end)
            repository.get_top_menu_items_by_day(start, end)
            repository.get_top_menu_items_by_month(start, end)
            repository.get_menu_item_filter_options()
            repository.get_active_categories()
            repository.get_menu_item_sales(
                start,
                end,
                menu_item_id=1,
                branch_id=2,
                category_id=3,
            )
            repository.get_top_menu_items_for_period(start, end)
            repository.get_campaign_menu_items()
            repository.get_campaigns(
                campaign="summer",
                menu_item_id=1,
                start_date=start,
            )
            repository.get_active_branches()
            repository.get_daily_reports(
                start,
                end,
                branch_id=2,
                status="paid",
            )

        queries["fetch_menu_item_sales"].assert_called_once_with(
            start,
            end,
            menu_item_id=1,
            branch_id=2,
            category_id=3,
        )
        queries["fetch_campaigns"].assert_called_once_with(
            campaign="summer",
            menu_item_id=1,
            start_date=start,
        )
        queries["fetch_daily_reports"].assert_called_once_with(
            start,
            end,
            branch_id=2,
            status="paid",
        )
