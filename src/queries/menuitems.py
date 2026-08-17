from __future__ import annotations

from datetime import date

import pandas as pd

from src.conf.db import run_query


def fetch_menu_item_filter_options() -> pd.DataFrame:
    return run_query(
        """
        SELECT
            items.id,
            items.name_ar,
            items.category_id,
            categories.name_ar AS category_name,
            COALESCE(
                STRING_AGG(branches.name, '، ' ORDER BY branches.name),
                ''
            ) AS branch_names
        FROM menu_menuitem items
        JOIN menu_category categories ON categories.id = items.category_id
        LEFT JOIN menu_menuitem_branches links ON links.menuitem_id = items.id
        LEFT JOIN menu_branch branches ON branches.id = links.branch_id
        WHERE items.is_active = TRUE
        GROUP BY items.id, items.name_ar, items.category_id, categories.name_ar
        ORDER BY items.name_ar, categories.name_ar, items.id;
        """
    )


def fetch_active_categories() -> pd.DataFrame:
    return run_query(
        """
        SELECT id, name_ar
        FROM menu_category
        WHERE is_active = TRUE
        ORDER BY frontend_ranking, name_ar, id;
        """
    )


def fetch_menu_item_sales(
    date_from: date,
    date_to: date,
    *,
    menu_item_id: int | None = None,
    branch_id: int | None = None,
    category_id: int | None = None,
) -> pd.DataFrame:
    return run_query(
        """
        SELECT
            orders.created_at::date AS report_date,
            items.id AS menu_item_id,
            order_items.menu_item_name_ar AS menu_item_name,
            categories.name_ar AS category_name,
            COUNT(DISTINCT orders.id) AS total_orders,
            COALESCE(SUM(order_items.total_price), 0) AS total_revenue
        FROM orders_orderitem order_items
        JOIN orders_order orders ON orders.id = order_items.order_id
        JOIN menu_menuitem items ON items.id = order_items.menu_item_id
        JOIN menu_category categories ON categories.id = items.category_id
        WHERE orders.created_at::date BETWEEN :date_from AND :date_to
          AND (:menu_item_id IS NULL OR items.id = :menu_item_id)
          AND (:branch_id IS NULL OR orders.branch_id = :branch_id)
          AND (:category_id IS NULL OR items.category_id = :category_id)
        GROUP BY
            orders.created_at::date,
            items.id,
            order_items.menu_item_name_ar,
            categories.name_ar
        ORDER BY report_date DESC, total_orders DESC, total_revenue DESC, menu_item_name;
        """,
        {
            "date_from": date_from,
            "date_to": date_to,
            "menu_item_id": menu_item_id,
            "branch_id": branch_id,
            "category_id": category_id,
        },
    )


def fetch_top_menu_items_for_period(
    date_from: date,
    date_to: date,
) -> pd.DataFrame:
    """Load each day's top ten ordered menu items."""
    return run_query(
        """
        WITH daily_menu_items AS (
            SELECT
                orders.created_at::date AS report_date,
                order_items.menu_item_name_ar AS menu_item_name,
                SUM(order_items.quantity) AS total_quantity
            FROM orders_orderitem order_items
            JOIN orders_order orders ON orders.id = order_items.order_id
            WHERE orders.created_at::date BETWEEN :date_from AND :date_to
            GROUP BY orders.created_at::date, order_items.menu_item_name_ar
        ),
        ranked_menu_items AS (
            SELECT
                report_date,
                menu_item_name,
                total_quantity,
                ROW_NUMBER() OVER (
                    PARTITION BY report_date
                    ORDER BY total_quantity DESC, menu_item_name
                ) AS item_rank
            FROM daily_menu_items
        )
        SELECT report_date, menu_item_name, total_quantity, item_rank
        FROM ranked_menu_items
        WHERE item_rank <= 10
        ORDER BY report_date, item_rank;
        """,
        {"date_from": date_from, "date_to": date_to},
    )


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
            WHERE orders.created_at >= :month_start
              AND orders.created_at < :next_month
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
    return run_query(query, {"month_start": month_start, "next_month": next_month})


def fetch_top_menu_items_by_month(month_start: date, next_month: date) -> pd.DataFrame:
    """Load the month's top ten ordered menu items by total quantity."""
    query = """
        SELECT
            order_items.menu_item_name_ar AS menu_item_name,
            SUM(order_items.quantity) AS total_quantity
        FROM orders_orderitem AS order_items
        JOIN orders_order AS orders
          ON orders.id = order_items.order_id
        WHERE orders.created_at >= :month_start
          AND orders.created_at < :next_month
        GROUP BY menu_item_name
        ORDER BY total_quantity DESC, menu_item_name ASC
        LIMIT 10;
    """
    return run_query(query, {"month_start": month_start, "next_month": next_month})
