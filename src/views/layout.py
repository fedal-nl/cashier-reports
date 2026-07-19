from __future__ import annotations

import pandas as pd
import streamlit as st

from src.utils.formatters import money


def apply_rtl_styles() -> None:
    """Apply RTL styling and hide Streamlit chrome that is not useful for users."""
    st.markdown(
        """
        <style>
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stMetric"] {
            direction: rtl;
            text-align: right;
        }
        .stTabs [data-baseweb="tab-list"] {
            direction: rtl;
        }
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(order_trends: pd.DataFrame, customer_trends: pd.DataFrame) -> None:
    """Render high-level monthly totals above the report tabs."""
    total_orders = int(order_trends["total_orders"].sum())
    total_revenue = order_trends["total_revenue"].sum()
    total_new_customers = int(customer_trends["new_customers"].sum())
    total_existing_customers = int(customer_trends["existing_customers"].sum())

    col_orders, col_revenue, col_new, col_existing = st.columns(4)
    col_orders.metric("طلبات هذا الشهر", f"{total_orders:,}")
    col_revenue.metric("إيرادات هذا الشهر", money(total_revenue))
    col_new.metric("عملاء جدد", f"{total_new_customers:,}")
    col_existing.metric("عملاء حاليون", f"{total_existing_customers:,}")