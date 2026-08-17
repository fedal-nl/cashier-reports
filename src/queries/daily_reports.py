from __future__ import annotations

from datetime import date

import pandas as pd

from src.conf.db import run_query


def fetch_active_branches() -> pd.DataFrame:
    return run_query(
        """
        SELECT id, name, location
        FROM menu_branch
        WHERE is_active = TRUE
        ORDER BY id;
        """
    )


def fetch_daily_reports(
    date_from: date,
    date_to: date,
    *,
    branch_id: int | None = None,
    status: str | None = None,
) -> pd.DataFrame:
    """Return the React daily report equivalent, including empty branch/day rows."""
    return run_query(
        """
        WITH report_days AS (
            SELECT GENERATE_SERIES(
                CAST(:date_from AS date),
                CAST(:date_to AS date),
                INTERVAL '1 day'
            )::date AS report_date
        ),
        selected_branches AS (
            SELECT id, name
            FROM menu_branch
            WHERE is_active = TRUE
              AND (:branch_id IS NULL OR id = :branch_id)
        ),
        filtered_orders AS (
            SELECT orders.*
            FROM orders_order orders
            JOIN selected_branches branches ON branches.id = orders.branch_id
            WHERE orders.created_at::date BETWEEN :date_from AND :date_to
              AND (:status IS NULL OR orders.status = :status)
        ),
        daily_totals AS (
            SELECT
                orders.created_at::date AS report_date,
                orders.branch_id,
                COUNT(*) AS total_orders,
                COALESCE(SUM(orders.total_price), 0) AS total_revenue,
                COUNT(*) FILTER (WHERE orders.status = 'created') AS status_created,
                COUNT(*) FILTER (WHERE orders.status = 'preparing') AS status_preparing,
                COUNT(*) FILTER (WHERE orders.status = 'ready') AS status_ready,
                COUNT(*) FILTER (WHERE orders.status = 'completed') AS status_completed,
                COUNT(*) FILTER (WHERE orders.status = 'cancelled') AS status_cancelled,
                COUNT(*) FILTER (WHERE orders.status = 'paid') AS status_paid,
                COUNT(*) FILTER (WHERE orders.status = 'picked_up') AS status_picked_up,
                COUNT(*) FILTER (WHERE orders.status = 'delivered') AS status_delivered
            FROM filtered_orders orders
            GROUP BY orders.created_at::date, orders.branch_id
        ),
        daily_customers AS (
            SELECT
                orders.created_at::date AS report_date,
                orders.branch_id,
                COUNT(DISTINCT orders.customer_id) FILTER (
                    WHERE orders.customer_id IS NOT NULL
                      AND NOT EXISTS (
                          SELECT 1
                          FROM orders_order previous_orders
                          WHERE previous_orders.customer_id = orders.customer_id
                            AND previous_orders.created_at::date < orders.created_at::date
                      )
                ) + CASE
                    WHEN BOOL_OR(orders.customer_id IS NULL) THEN 1
                    ELSE 0
                END AS total_new_customers_ordered,
                COUNT(DISTINCT orders.customer_id) FILTER (
                    WHERE orders.customer_id IS NOT NULL
                      AND EXISTS (
                          SELECT 1
                          FROM orders_order previous_orders
                          WHERE previous_orders.customer_id = orders.customer_id
                            AND previous_orders.created_at::date < orders.created_at::date
                      )
                ) AS total_existing_customers_ordered
            FROM filtered_orders orders
            GROUP BY orders.created_at::date, orders.branch_id
        )
        SELECT
            days.report_date,
            branches.id AS branch_id,
            branches.name AS branch_name,
            COALESCE(totals.total_orders, 0) AS total_orders,
            COALESCE(totals.status_created, 0) AS status_created,
            COALESCE(totals.status_preparing, 0) AS status_preparing,
            COALESCE(totals.status_ready, 0) AS status_ready,
            COALESCE(totals.status_completed, 0) AS status_completed,
            COALESCE(totals.status_cancelled, 0) AS status_cancelled,
            COALESCE(totals.status_paid, 0) AS status_paid,
            COALESCE(totals.status_picked_up, 0) AS status_picked_up,
            COALESCE(totals.status_delivered, 0) AS status_delivered,
            COALESCE(customers.total_new_customers_ordered, 0)
                AS total_new_customers_ordered,
            COALESCE(customers.total_existing_customers_ordered, 0)
                AS total_existing_customers_ordered,
            COALESCE(totals.total_revenue, 0) AS total_revenue
        FROM report_days days
        CROSS JOIN selected_branches branches
        LEFT JOIN daily_totals totals
          ON totals.report_date = days.report_date
         AND totals.branch_id = branches.id
        LEFT JOIN daily_customers customers
          ON customers.report_date = days.report_date
         AND customers.branch_id = branches.id
        ORDER BY days.report_date, branches.id;
        """,
        {
            "date_from": date_from,
            "date_to": date_to,
            "branch_id": branch_id,
            "status": status,
        },
    )
