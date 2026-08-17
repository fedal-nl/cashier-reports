from __future__ import annotations

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from src.queries.campaigns import fetch_campaigns
from src.queries.customers import fetch_customer_trends, fetch_top_customers
from src.queries.daily_reports import fetch_active_branches, fetch_daily_reports
from src.queries.menuitems import (
    fetch_menu_item_sales,
    fetch_top_menu_items_by_day,
    fetch_top_menu_items_by_month,
    fetch_top_menu_items_for_period,
)
from src.queries.orders import fetch_order_trends


class QueryTests(unittest.TestCase):
    @patch("src.queries.menuitems.run_query")
    def test_fetch_menu_item_sales_applies_search_filters(
        self, mock_run_query: MagicMock
    ) -> None:
        date_from = date(2026, 8, 1)
        date_to = date(2026, 8, 7)

        fetch_menu_item_sales(
            date_from,
            date_to,
            menu_item_id=12,
            branch_id=2,
            category_id=4,
        )

        query, params = mock_run_query.call_args.args
        self.assertIn("orders.created_at::date AS report_date", query)
        self.assertIn("COUNT(DISTINCT orders.id)", query)
        self.assertIn("SUM(order_items.total_price)", query)
        self.assertEqual(
            params,
            {
                "date_from": date_from,
                "date_to": date_to,
                "menu_item_id": 12,
                "branch_id": 2,
                "category_id": 4,
            },
        )

    @patch("src.queries.menuitems.run_query")
    def test_weekly_top_items_ranks_ten_items_per_day(
        self, mock_run_query: MagicMock
    ) -> None:
        date_from = date(2026, 8, 10)
        date_to = date(2026, 8, 16)

        fetch_top_menu_items_for_period(date_from, date_to)

        query, params = mock_run_query.call_args.args
        self.assertIn("item_rank <= 10", query)
        self.assertEqual(params, {"date_from": date_from, "date_to": date_to})

    @patch("src.queries.daily_reports.run_query")
    def test_fetch_active_branches_uses_active_filter(
        self, mock_run_query: MagicMock
    ) -> None:
        fetch_active_branches()

        query = mock_run_query.call_args.args[0]
        self.assertIn("FROM menu_branch", query)
        self.assertIn("is_active = TRUE", query)

    @patch("src.queries.daily_reports.run_query")
    def test_fetch_daily_reports_applies_all_filters(
        self, mock_run_query: MagicMock
    ) -> None:
        date_from = date(2026, 8, 1)
        date_to = date(2026, 8, 7)

        fetch_daily_reports(
            date_from,
            date_to,
            branch_id=3,
            status="completed",
        )

        query, params = mock_run_query.call_args.args
        self.assertIn("GENERATE_SERIES", query)
        self.assertIn("CROSS JOIN selected_branches", query)
        self.assertIn("total_new_customers_ordered", query)
        self.assertIn("status_completed", query)
        self.assertEqual(
            params,
            {
                "date_from": date_from,
                "date_to": date_to,
                "branch_id": 3,
                "status": "completed",
            },
        )

    @patch("src.queries.campaigns.run_query")
    def test_fetch_campaigns_applies_read_only_filters(
        self, mock_run_query: MagicMock
    ) -> None:
        start_date = date(2026, 7, 1)

        fetch_campaigns(campaign="TikTok", menu_item_id=4, start_date=start_date)

        query, params = mock_run_query.call_args.args
        self.assertIn("FROM orders_campaign campaigns", query)
        self.assertIn("orders_campaign_menu_items", query)
        self.assertIn("orders.status <> 'cancelled'", query)
        self.assertEqual(
            params,
            {
                "campaign_name": "%TikTok%",
                "menu_item_id": 4,
                "start_date": start_date,
            },
        )

    @patch("src.queries.orders.run_query")
    def test_fetch_order_trends_calls_run_query(
        self, mock_run_query: MagicMock
    ) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_order_trends(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("FROM orders_order", query)
        self.assertIn("COUNT(*) AS total_orders", query)
        self.assertEqual(params, {"month_start": month_start, "next_month": next_month})

    @patch("src.queries.customers.run_query")
    def test_fetch_customer_trends_calls_run_query(
        self, mock_run_query: MagicMock
    ) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_customer_trends(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("WITH customer_order_days", query)
        self.assertIn("AS new_customers", query)
        self.assertEqual(params, {"month_start": month_start, "next_month": next_month})

    @patch("src.queries.customers.run_query")
    def test_fetch_top_customers_calls_run_query(
        self, mock_run_query: MagicMock
    ) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_top_customers(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("JOIN orders_customer", query)
        self.assertIn("LIMIT 10", query)
        self.assertEqual(params, {"month_start": month_start, "next_month": next_month})

    @patch("src.queries.menuitems.run_query")
    def test_fetch_top_menu_items_by_day_calls_run_query(
        self, mock_run_query: MagicMock
    ) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_top_menu_items_by_day(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("ROW_NUMBER() OVER", query)
        self.assertIn("WHERE item_rank <= 10", query)
        self.assertEqual(params, {"month_start": month_start, "next_month": next_month})

    @patch("src.queries.menuitems.run_query")
    def test_fetch_top_menu_items_by_month_calls_run_query(
        self, mock_run_query: MagicMock
    ) -> None:
        month_start = date(2026, 7, 1)
        next_month = date(2026, 8, 1)

        fetch_top_menu_items_by_month(month_start, next_month)

        query, params = mock_run_query.call_args.args
        self.assertIn("SUM(order_items.quantity)", query)
        self.assertIn("LIMIT 10", query)
        self.assertEqual(params, {"month_start": month_start, "next_month": next_month})
