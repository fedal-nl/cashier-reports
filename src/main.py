from __future__ import annotations

from datetime import timedelta

import streamlit as st

from src.services.dashboard import load_dashboard_data
from src.utils.dates import get_current_month_bounds
from src.views.campaigns import render_campaigns_tab
from src.views.customers import render_customers_tab
from src.views.daily_reports import render_daily_reports_tab
from src.views.layout import apply_rtl_styles, render_metric_row
from src.views.menu_items import render_menu_items_tab
from src.views.orders import render_orders_tab


def main() -> None:
    """Render the Streamlit dashboard with monthly cashier report tabs."""
    st.set_page_config(
        page_title="تقارير الكاشير",
        layout="wide",
    )
    apply_rtl_styles()
    month_start, next_month = get_current_month_bounds()

    st.title("تقارير الكاشير")
    st.caption(
        f"الشهر الحالي: {month_start:%Y-%m-%d} إلى "
        f"{next_month - timedelta(days=1):%Y-%m-%d}"
    )

    try:
        dashboard_data = load_dashboard_data(month_start, next_month)
    except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
        st.error("تعذر تحميل بيانات التقارير من قاعدة البيانات.")
        st.exception(exc)
        return

    render_metric_row(
        dashboard_data.order_trends,
        dashboard_data.customer_trends,
    )

    selected_section = st.radio(
        "قسم التقارير",
        [
            "التقارير اليومية",
            "الطلبات",
            "العملاء",
            "تقارير الطعام",
            "الحملات الإعلانية",
        ],
        horizontal=True,
        key="selected_report_section",
        label_visibility="collapsed",
    )

    if selected_section == "التقارير اليومية":
        render_daily_reports_tab()
    elif selected_section == "الطلبات":
        render_orders_tab(dashboard_data.order_trends)
    elif selected_section == "العملاء":
        render_customers_tab(
            dashboard_data.customer_trends,
            dashboard_data.top_customers,
        )
    elif selected_section == "تقارير الطعام":
        render_menu_items_tab()
    else:
        render_campaigns_tab()
