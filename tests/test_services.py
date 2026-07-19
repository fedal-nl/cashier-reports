from __future__ import annotations

from datetime import date
import unittest
from unittest.mock import patch

import pandas as pd

from src.services.customers import load_customer_trends
from src.services.dashboard import load_dashboard_data
from src.services.customers import load_top_customers
from src.services.menuitems import load_top_menu_items_by_day
from src.services.menuitems import load_top_menu_items_by_month
from src.services.orders import load_order_trends


class ReportServicesTests(unittest.TestCase):
    @patch("src.services.orders.fetch_order_trends")
    def test_load_order_trends_fills_missing_days(self, mock_fetch: object) -> None:
        mock_fetch.return_value = pd.DataFrame({
            "report_date": [date(2026, 7, 2)],
            "total_orders": [3],
            "total_revenue": [15000],
        })

        result = load_order_trends(date(2026, 7, 1), date(2026, 7, 4))

        self.assertEqual(result["report_date"].tolist(), [
            date(2026, 7, 1),
            date(2026, 7, 2),
            date(2026, 7, 3),
        ])
        self.assertEqual(result["total_orders"].tolist(), [0, 3, 0])
        self.assertEqual(result["total_revenue"].tolist(), [0.0, 15000.0, 0.0])

    @patch("src.services.customers.fetch_customer_trends")
    def test_load_customer_trends_handles_empty_results(self, mock_fetch: object) -> None:
        mock_fetch.return_value = pd.DataFrame(
            columns=["report_date", "new_customers", "existing_customers"],
        )

        result = load_customer_trends(date(2026, 7, 1), date(2026, 7, 3))

        self.assertEqual(result["report_date"].tolist(), [
            date(2026, 7, 1),
            date(2026, 7, 2),
        ])
        self.assertEqual(result["new_customers"].tolist(), [0, 0])
        self.assertEqual(result["existing_customers"].tolist(), [0, 0])

    @patch("src.services.dashboard.load_top_menu_items_by_day")
    @patch("src.services.dashboard.load_top_menu_items_by_month")
    @patch("src.services.dashboard.load_top_customers")
    @patch("src.services.dashboard.load_customer_trends")
    @patch("src.services.dashboard.load_order_trends")
    def test_load_dashboard_data_collects_all_datasets(
        self,
        mock_orders: object,
        mock_customers: object,
        mock_top_customers: object,
        mock_menu_items_month: object,
        mock_menu_items: object,
    ) -> None:
        mock_orders.return_value = pd.DataFrame({"total_orders": [1]})
        mock_customers.return_value = pd.DataFrame({"new_customers": [2]})
        mock_top_customers.return_value = pd.DataFrame({"customer_name": ["A"]})
        mock_menu_items_month.return_value = pd.DataFrame({"menu_item_name": ["M"]})
        mock_menu_items.return_value = pd.DataFrame({"menu_item_name": ["B"]})

        result = load_dashboard_data(date(2026, 7, 1), date(2026, 8, 1))

        self.assertEqual(result.order_trends.iloc[0]["total_orders"], 1)
        self.assertEqual(result.customer_trends.iloc[0]["new_customers"], 2)
        self.assertEqual(result.top_customers.iloc[0]["customer_name"], "A")
        self.assertEqual(result.menu_items_by_day.iloc[0]["menu_item_name"], "B")
        self.assertEqual(result.menu_items_by_month.iloc[0]["menu_item_name"], "M")

    @patch("src.services.menuitems.fetch_top_menu_items_by_month")
    def test_load_top_menu_items_by_month_returns_query_data(self, mock_fetch: object) -> None:
        mock_fetch.return_value = pd.DataFrame({
            "menu_item_name": ["Meal"],
            "total_quantity": [20],
        })

        result = load_top_menu_items_by_month(date(2026, 7, 1), date(2026, 8, 1))

        self.assertEqual(result.iloc[0]["menu_item_name"], "Meal")
        self.assertEqual(result.iloc[0]["total_quantity"], 20)

    @patch("src.services.customers.fetch_top_customers")
    def test_load_top_customers_returns_query_data(self, mock_fetch: object) -> None:
        mock_fetch.return_value = pd.DataFrame({
            "customer_name": ["Customer"],
            "total_orders": [3],
        })

        result = load_top_customers(date(2026, 7, 1), date(2026, 8, 1))

        self.assertEqual(result.iloc[0]["customer_name"], "Customer")
        self.assertEqual(result.iloc[0]["total_orders"], 3)

    @patch("src.services.menuitems.fetch_top_menu_items_by_day")
    def test_load_top_menu_items_by_day_returns_query_data(self, mock_fetch: object) -> None:
        mock_fetch.return_value = pd.DataFrame({
            "menu_item_name": ["Meal"],
            "item_rank": [1],
        })

        result = load_top_menu_items_by_day(date(2026, 7, 1), date(2026, 8, 1))

        self.assertEqual(result.iloc[0]["menu_item_name"], "Meal")
        self.assertEqual(result.iloc[0]["item_rank"], 1)