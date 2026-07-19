from __future__ import annotations

from datetime import date

import pandas as pd

from src.conf.db import run_query


def fetch_customer_trends(month_start: date, next_month: date) -> pd.DataFrame:
    """Load daily new and existing customer totals for customers who ordered."""
    query = """
        WITH customer_order_days AS (
            SELECT
                created_at::date AS report_date,
                customer_id
            FROM orders_order
            WHERE created_at >= %s
              AND created_at < %s
            GROUP BY report_date, customer_id
        ),
        first_orders AS (
            SELECT
                customer_id,
                MIN(created_at)::date AS first_order_date
            FROM orders_order
            GROUP BY customer_id
        )
        SELECT
            customer_order_days.report_date,
            COUNT(*) FILTER (
                WHERE first_orders.first_order_date = customer_order_days.report_date
            ) AS new_customers,
            COUNT(*) FILTER (
                WHERE first_orders.first_order_date < customer_order_days.report_date
            ) AS existing_customers
        FROM customer_order_days
        JOIN first_orders
          ON first_orders.customer_id = customer_order_days.customer_id
        GROUP BY customer_order_days.report_date
        ORDER BY customer_order_days.report_date;
    """
    return run_query(query, (month_start, next_month))


def fetch_top_customers(month_start: date, next_month: date) -> pd.DataFrame:
    """Load the top ten customers by monthly revenue and order count."""
    query = """
        SELECT
            COALESCE(NULLIF(TRIM(customer.name), ''), 'عميل غير معروف') AS customer_name,
            COUNT(orders.id) AS total_orders,
            COALESCE(SUM(orders.total_price), 0) AS total_revenue
        FROM orders_order AS orders
        JOIN orders_customer AS customer
          ON customer.id = orders.customer_id
        WHERE orders.created_at >= %s
          AND orders.created_at < %s
        GROUP BY customer.id, customer.name
        ORDER BY total_revenue DESC, total_orders DESC, customer_name ASC
        LIMIT 10;
    """
    return run_query(query, (month_start, next_month))