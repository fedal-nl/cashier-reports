from __future__ import annotations

from datetime import date

import pandas as pd

from src.conf.db import run_query


def fetch_campaign_menu_items() -> pd.DataFrame:
    return run_query(
        """
        SELECT id, name_ar
        FROM menu_menuitem
        WHERE is_active = TRUE
        ORDER BY name_ar, id;
        """,
        {},
    )


def fetch_campaigns(
    *,
    campaign: str = "",
    menu_item_id: int | None = None,
    start_date: date | None = None,
) -> pd.DataFrame:
    filters = []
    params: dict[str, object] = {}

    if campaign:
        if campaign.isdigit():
            filters.append("campaigns.id = :campaign_id")
            params["campaign_id"] = int(campaign)
        else:
            filters.append("campaigns.campaign_name ILIKE :campaign_name")
            params["campaign_name"] = f"%{campaign}%"

    if menu_item_id is not None:
        filters.append(
            "EXISTS (SELECT 1 FROM orders_campaign_menu_items filter_items "
            "WHERE filter_items.campaign_id = campaigns.id "
            "AND filter_items.menuitem_id = :menu_item_id)"
        )
        params["menu_item_id"] = menu_item_id

    if start_date is not None:
        filters.append("campaigns.start_date = :start_date")
        params["start_date"] = start_date

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    return run_query(
        f"""
        SELECT
            campaigns.id AS campaign_id,
            campaigns.campaign_name,
            campaigns.channel,
            campaigns.start_date,
            campaigns.end_date,
            campaigns.amount_spent,
            COALESCE(menu_items.names, '') AS menu_items,
            COALESCE(metrics.current_revenue, 0) AS current_revenue,
            COALESCE(metrics.total_orders, 0) AS total_orders,
            COALESCE(metrics.current_revenue, 0) - campaigns.amount_spent AS profit
        FROM orders_campaign campaigns
        LEFT JOIN LATERAL (
            SELECT STRING_AGG(items.name_ar, '، ' ORDER BY items.name_ar) AS names
            FROM orders_campaign_menu_items links
            JOIN menu_menuitem items ON items.id = links.menuitem_id
            WHERE links.campaign_id = campaigns.id
        ) menu_items ON TRUE
        LEFT JOIN LATERAL (
            SELECT
                SUM(order_items.total_price) AS current_revenue,
                COUNT(DISTINCT orders.id) AS total_orders
            FROM orders_orderitem order_items
            JOIN orders_order orders ON orders.id = order_items.order_id
            JOIN orders_campaign_menu_items links
              ON links.menuitem_id = order_items.menu_item_id
             AND links.campaign_id = campaigns.id
            WHERE orders.created_at::date BETWEEN campaigns.start_date AND campaigns.end_date
              AND orders.status <> 'cancelled'
        ) metrics ON TRUE
        {where_clause}
        ORDER BY campaigns.start_date DESC, campaigns.id DESC;
        """,
        params,
    )
