from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.services.daily_reports import load_active_branches
from src.services.menuitems import (
    load_active_categories,
    load_menu_item_filter_options,
    load_menu_item_sales,
    load_top_menu_items_for_period,
)
from src.utils.formatters import money


def _render_sales_table(data: pd.DataFrame, *, show_date: bool = False) -> None:
    if data.empty:
        st.info("لا توجد وجبات مطابقة.")
        return

    table = data.copy()
    table["total_revenue"] = table["total_revenue"].map(money)
    columns = ["menu_item_name", "category_name", "total_orders", "total_revenue"]
    if show_date:
        columns.insert(0, "report_date")
    st.dataframe(
        table[columns].rename(
            columns={
                "report_date": "التاريخ",
                "menu_item_name": "الوجبة",
                "category_name": "الفئة",
                "total_orders": "عدد الطلبات",
                "total_revenue": "الإيرادات",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


def _render_today_report(today: date) -> None:
    st.subheader("وجبات اليوم المطلوبة")
    try:
        data = load_menu_item_sales(today, today)
    except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
        st.error("تعذر تحميل وجبات اليوم.")
        st.exception(exc)
        return

    _render_sales_table(data)


def _render_menu_item_search(today: date) -> None:
    st.subheader("البحث في مبيعات الوجبات")

    try:
        menu_items = load_menu_item_filter_options()
        categories = load_active_categories()
        branches = load_active_branches()
    except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
        st.error("تعذر تحميل خيارات البحث.")
        st.exception(exc)
        return

    item_labels = {
        int(item["id"]): (
            f"{item['name_ar']} — {item['category_name']}"
            + (f" — {item['branch_names']}" if item.get("branch_names") else "")
        )
        for item in menu_items
    }
    category_labels = {
        int(category["id"]): str(category["name_ar"]) for category in categories
    }
    branch_labels = {int(branch["id"]): str(branch["name"]) for branch in branches}

    with st.form("menu-item-sales-filters"):
        item_col, branch_col, category_col = st.columns(3)
        menu_item_id = item_col.selectbox(
            "الوجبة",
            [None, *item_labels],
            format_func=lambda value: (
                "كل الوجبات" if value is None else item_labels[value]
            ),
        )
        branch_id = branch_col.selectbox(
            "الفرع",
            [None, *branch_labels],
            format_func=lambda value: (
                "كل الفروع" if value is None else branch_labels[value]
            ),
        )
        category_id = category_col.selectbox(
            "الفئة",
            [None, *category_labels],
            format_func=lambda value: (
                "كل الفئات" if value is None else category_labels[value]
            ),
        )
        from_col, to_col, button_col = st.columns([1, 1, 0.8])
        date_from = from_col.date_input("من تاريخ", value=today - timedelta(days=6))
        date_to = to_col.date_input("إلى تاريخ", value=today)
        button_col.markdown(
            "<div style='height: 28px'></div>",
            unsafe_allow_html=True,
        )
        submitted = button_col.form_submit_button("بحث", use_container_width=True)

    if submitted:
        if date_from > date_to:
            st.error("تاريخ البداية يجب أن يكون قبل تاريخ النهاية.")
            return
        try:
            rows = load_menu_item_sales(
                date_from,
                date_to,
                menu_item_id=menu_item_id,
                branch_id=branch_id,
                category_id=category_id,
            )
        except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
            st.error("تعذر تحميل مبيعات الوجبات.")
            st.exception(exc)
            return
        st.session_state.menu_item_sales_rows_with_date = rows

    if "menu_item_sales_rows_with_date" not in st.session_state:
        st.info("اختر معايير البحث ثم اضغط بحث.")
        return

    rows = st.session_state.menu_item_sales_rows_with_date
    total_orders = int(rows["total_orders"].sum()) if not rows.empty else 0
    total_revenue = rows["total_revenue"].sum() if not rows.empty else 0
    orders_col, revenue_col = st.columns(2)
    orders_col.metric("عدد الطلبات", f"{total_orders:,}")
    revenue_col.metric("الإيرادات", money(total_revenue))
    _render_sales_table(rows, show_date=True)


def _render_weekly_top_ten(today: date) -> None:
    date_from = today - timedelta(days=6)
    st.subheader("أفضل 10 وجبات يومياً خلال آخر أسبوع")
    st.caption(f"من {date_from:%Y-%m-%d} إلى {today:%Y-%m-%d}")

    try:
        data = load_top_menu_items_for_period(date_from, today)
    except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
        st.error("تعذر تحميل ترتيب الوجبات.")
        st.exception(exc)
        return

    if data.empty:
        st.info("لا توجد طلبات وجبات خلال آخر أسبوع.")
        return

    data = data.copy()
    data["report_date"] = pd.to_datetime(data["report_date"]).dt.date
    chart = px.bar(
        data,
        x="report_date",
        y="total_quantity",
        color="menu_item_name",
        barmode="group",
        labels={
            "report_date": "التاريخ",
            "total_quantity": "الكمية المطلوبة",
            "menu_item_name": "الوجبة",
        },
    )
    chart.update_layout(xaxis_title=None)
    st.plotly_chart(chart, use_container_width=True)
    st.dataframe(
        data.rename(
            columns={
                "report_date": "التاريخ",
                "item_rank": "الترتيب",
                "menu_item_name": "الوجبة",
                "total_quantity": "الكمية المطلوبة",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


def render_menu_items_tab() -> None:
    """Render the food reporting workspace."""
    today = datetime.now(UTC).date()
    selected_food_report = st.radio(
        "نوع تقرير الطعام",
        ["طلبات اليوم", "البحث عن وجبة", "أفضل 10 خلال أسبوع"],
        horizontal=True,
        key="selected_food_report",
        label_visibility="collapsed",
    )

    if selected_food_report == "طلبات اليوم":
        _render_today_report(today)
    elif selected_food_report == "البحث عن وجبة":
        _render_menu_item_search(today)
    else:
        _render_weekly_top_ten(today)
