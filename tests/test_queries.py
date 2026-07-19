from __future__ import annotations

from datetime import date
import unittest
from unittest.mock import MagicMock, patch

from src.queries.customers import fetch_customer_trends, fetch_top_customers
from src.queries.menuitems import fetch_top_menu_items_by_day, fetch_top_menu_items_by_month
from src.queries.orders import fetch_order_trends


class QueryTests(unittest.TestCase):
    @patch("src.queries.orders.run_query")
    def test_fetch_order_trends_calls_run_query(self, mock_run_query: MagicMock) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_order_trends(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("FROM orders_order", query)
        self.assertIn("COUNT(*) AS total_orders", query)
        self.assertEqual(params, (month_start, next_month))

    @patch("src.queries.customers.run_query")
    def test_fetch_customer_trends_calls_run_query(self, mock_run_query: MagicMock) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_customer_trends(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("WITH customer_order_days", query)
        self.assertIn("AS new_customers", query)
        self.assertEqual(params, (month_start, next_month))

    @patch("src.queries.customers.run_query")
    def test_fetch_top_customers_calls_run_query(self, mock_run_query: MagicMock) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_top_customers(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("JOIN orders_customer", query)
        self.assertIn("LIMIT 10", query)
        self.assertEqual(params, (month_start, next_month))

    @patch("src.queries.menuitems.run_query")
    def test_fetch_top_menu_items_by_day_calls_run_query(self, mock_run_query: MagicMock) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_top_menu_items_by_day(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("ROW_NUMBER() OVER", query)
        self.assertIn("WHERE item_rank <= 10", query)
        self.assertEqual(params, (month_start, next_month))

    @patch("src.queries.menuitems.run_query")
    def test_fetch_top_menu_items_by_month_calls_run_query(self, mock_run_query: MagicMock) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_top_menu_items_by_month(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("SUM(order_items.quantity)", query)
        self.assertIn("LIMIT 10", query)
        self.assertEqual(params, (month_start, next_month))