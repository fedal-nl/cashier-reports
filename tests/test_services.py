from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd

from src.services.customers import load_customer_trends, load_top_customers
from src.services.daily_reports import load_active_branches, load_daily_reports
from src.services.dashboard import load_dashboard_data
from src.services.menuitems import (
    load_menu_item_sales,
    load_top_menu_items_by_day,
    load_top_menu_items_by_month,
    load_top_menu_items_for_period,
)
from src.services.orders import load_order_trends


class ReportServicesTests(unittest.TestCase):
    def test_load_menu_item_sales_passes_all_filters(self) -> None:
        repository = MagicMock()
        expected = pd.DataFrame({"total_orders": [4], "total_revenue": [100]})
        repository.get_menu_item_sales.return_value = expected

        result = load_menu_item_sales(
            date(2026, 8, 1),
            date(2026, 8, 7),
            menu_item_id=3,
            branch_id=2,
            category_id=1,
            repository=repository,
        )

        self.assertIs(result, expected)
        repository.get_menu_item_sales.assert_called_once_with(
            date(2026, 8, 1),
            date(2026, 8, 7),
            menu_item_id=3,
            branch_id=2,
            category_id=1,
        )

    def test_load_weekly_top_items_uses_repository(self) -> None:
        repository = MagicMock()
        expected = pd.DataFrame({"item_rank": [1]})
        repository.get_top_menu_items_for_period.return_value = expected

        result = load_top_menu_items_for_period(
            date(2026, 8, 10), date(2026, 8, 16), repository
        )

        self.assertIs(result, expected)

    def test_load_active_branches_returns_records(self) -> None:
        repository = MagicMock()
        repository.get_active_branches.return_value = pd.DataFrame(
            {"id": [1], "name": ["Main"], "location": ["Center"]}
        )

        result = load_active_branches(repository)

        self.assertEqual(
            result,
            [{"id": 1, "name": "Main", "location": "Center"}],
        )

    def test_load_daily_reports_passes_filters_to_repository(self) -> None:
        repository = MagicMock()
        expected = pd.DataFrame({"total_orders": [2]})
        repository.get_daily_reports.return_value = expected

        result = load_daily_reports(
            date(2026, 8, 1),
            date(2026, 8, 7),
            branch_id=2,
            status="paid",
            repository=repository,
        )

        self.assertIs(result, expected)
        repository.get_daily_reports.assert_called_once_with(
            date(2026, 8, 1),
            date(2026, 8, 7),
            branch_id=2,
            status="paid",
        )

    def test_load_daily_reports_rejects_reversed_dates(self) -> None:
        with self.assertRaisesRegex(ValueError, "date_from"):
            load_daily_reports(
                date(2026, 8, 7),
                date(2026, 8, 1),
                repository=MagicMock(),
            )

    def test_load_order_trends_fills_missing_days(self) -> None:
        repository = MagicMock()
        repository.get_order_trends.return_value = pd.DataFrame(
            {
                "report_date": [date(2026, 7, 2)],
                "total_orders": [3],
                "total_revenue": [15000],
            }
        )

        result = load_order_trends(date(2026, 7, 1), date(2026, 7, 4), repository)

        self.assertEqual(
            result["report_date"].tolist(),
            [
                date(2026, 7, 1),
                date(2026, 7, 2),
                date(2026, 7, 3),
            ],
        )
        self.assertEqual(result["total_orders"].tolist(), [0, 3, 0])
        self.assertEqual(result["total_revenue"].tolist(), [0.0, 15000.0, 0.0])

    def test_load_customer_trends_handles_empty_results(self) -> None:
        repository = MagicMock()
        repository.get_customer_trends.return_value = pd.DataFrame(
            columns=["report_date", "new_customers", "existing_customers"],
        )

        result = load_customer_trends(date(2026, 7, 1), date(2026, 7, 3), repository)

        self.assertEqual(
            result["report_date"].tolist(),
            [
                date(2026, 7, 1),
                date(2026, 7, 2),
            ],
        )
        self.assertEqual(result["new_customers"].tolist(), [0, 0])
        self.assertEqual(result["existing_customers"].tolist(), [0, 0])

    @patch("src.services.dashboard.load_top_customers")
    @patch("src.services.dashboard.load_customer_trends")
    @patch("src.services.dashboard.load_order_trends")
    def test_load_dashboard_data_collects_all_datasets(
        self,
        mock_orders: object,
        mock_customers: object,
        mock_top_customers: object,
    ) -> None:
        mock_orders.return_value = pd.DataFrame({"total_orders": [1]})
        mock_customers.return_value = pd.DataFrame({"new_customers": [2]})
        mock_top_customers.return_value = pd.DataFrame({"customer_name": ["A"]})

        result = load_dashboard_data(date(2026, 7, 1), date(2026, 8, 1))

        self.assertEqual(result.order_trends.iloc[0]["total_orders"], 1)
        self.assertEqual(result.customer_trends.iloc[0]["new_customers"], 2)
        self.assertEqual(result.top_customers.iloc[0]["customer_name"], "A")

    def test_load_top_menu_items_by_month_returns_query_data(self) -> None:
        repository = MagicMock()
        repository.get_top_menu_items_by_month.return_value = pd.DataFrame(
            {
                "menu_item_name": ["Meal"],
                "total_quantity": [20],
            }
        )

        result = load_top_menu_items_by_month(
            date(2026, 7, 1), date(2026, 8, 1), repository
        )

        self.assertEqual(result.iloc[0]["menu_item_name"], "Meal")
        self.assertEqual(result.iloc[0]["total_quantity"], 20)

    def test_load_top_customers_returns_query_data(self) -> None:
        repository = MagicMock()
        repository.get_top_customers.return_value = pd.DataFrame(
            {
                "customer_name": ["Customer"],
                "total_orders": [3],
            }
        )

        result = load_top_customers(date(2026, 7, 1), date(2026, 8, 1), repository)

        self.assertEqual(result.iloc[0]["customer_name"], "Customer")
        self.assertEqual(result.iloc[0]["total_orders"], 3)

    def test_load_top_menu_items_by_day_returns_query_data(self) -> None:
        repository = MagicMock()
        repository.get_top_menu_items_by_day.return_value = pd.DataFrame(
            {
                "menu_item_name": ["Meal"],
                "item_rank": [1],
            }
        )

        result = load_top_menu_items_by_day(
            date(2026, 7, 1), date(2026, 8, 1), repository
        )

        self.assertEqual(result.iloc[0]["menu_item_name"], "Meal")
        self.assertEqual(result.iloc[0]["item_rank"], 1)
