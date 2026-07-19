from __future__ import annotations

from datetime import date

import pandas as pd

from src.conf.db import run_query


def fetch_top_menu_items_by_day(month_start: date, next_month: date) -> pd.DataFrame:
    """Load each day's top ten ordered menu items."""
    query = """
        WITH daily_menu_items AS (
            SELECT
                orders.created_at::date AS report_date,
                order_items.menu_item_name_ar AS menu_item_name,
                SUM(order_items.quantity) AS total_quantity
            FROM orders_orderitem AS order_items
            JOIN orders_order AS orders
              ON orders.id = order_items.order_id
            WHERE orders.created_at >= %s
              AND orders.created_at < %s
            GROUP BY report_date, menu_item_name
        ),
        ranked_menu_items AS (
            SELECT
                report_date,
                menu_item_name,
                total_quantity,
                ROW_NUMBER() OVER (
                    PARTITION BY report_date
                    ORDER BY total_quantity DESC, menu_item_name ASC
                ) AS item_rank
            FROM daily_menu_items
        )
        SELECT
            report_date,
            menu_item_name,
            total_quantity,
            item_rank
        FROM ranked_menu_items
        WHERE item_rank <= 10
        ORDER BY report_date, item_rank;
    """
    return run_query(query, (month_start, next_month))


def fetch_top_menu_items_by_month(month_start: date, next_month: date) -> pd.DataFrame:
    """Load the month's top ten ordered menu items by total quantity."""
    query = """
        SELECT
            order_items.menu_item_name_ar AS menu_item_name,
            SUM(order_items.quantity) AS total_quantity
        FROM orders_orderitem AS order_items
        JOIN orders_order AS orders
          ON orders.id = order_items.order_id
        WHERE orders.created_at >= %s
          AND orders.created_at < %s
        GROUP BY menu_item_name
        ORDER BY total_quantity DESC, menu_item_name ASC
        LIMIT 10;
    """
    return run_query(query, (month_start, next_month))