from __future__ import annotations

from datetime import date

import pandas as pd

from src.conf.db import run_query


def fetch_order_trends(month_start: date, next_month: date) -> pd.DataFrame:
    """Load daily order count and revenue totals for the selected month."""
    query = """
        SELECT
            created_at::date AS report_date,
            COUNT(*) AS total_orders,
            COALESCE(SUM(total_price), 0) AS total_revenue
        FROM orders_order
        WHERE created_at >= %s
          AND created_at < %s
        GROUP BY report_date
        ORDER BY report_date;
    """
    return run_query(query, (month_start, next_month))