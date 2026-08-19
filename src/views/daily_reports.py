from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import streamlit as st

from src.services.daily_reports import load_active_branches, load_daily_reports
from src.utils.formatters import money
from src.utils.printing import render_print_button
from src.utils.tables import render_rtl_table

ORDER_STATUS_LABELS = {
    "created": "تم الإنشاء",
    "preparing": "قيد التحضير",
    "ready": "جاهز للاستلام",
    "completed": "مكتمل",
    "cancelled": "ملغي",
    "paid": "مدفوع",
    "picked_up": "تم الاستلام",
    "delivered": "تم التوصيل",
}


def _status_summary(row: pd.Series) -> str:
    return " | ".join(
        f"{label}: {int(row[f'status_{status}'])}"
        for status, label in ORDER_STATUS_LABELS.items()
    )


def render_daily_reports_tab() -> None:
    st.subheader("التقارير")
    st.caption("ملخص الطلبات والعملاء والإيرادات حسب اليوم")

    try:
        branches = load_active_branches()
    except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
        st.error("تعذر تحميل الفروع.")
        st.exception(exc)
        return

    branch_labels = {
        int(branch["id"]): (
            f"{branch['name']} - {branch['location']}"
            if branch.get("location")
            else str(branch["name"])
        )
        for branch in branches
    }

    today = datetime.now(UTC).date()
    with st.form("daily-report-filters"):
        date_from_col, date_to_col, branch_col, status_col, button_col = st.columns(
            [1, 1, 1.2, 1.2, 0.8]
        )
        date_from = date_from_col.date_input(
            "من تاريخ", value=today - timedelta(days=6)
        )
        date_to = date_to_col.date_input("إلى تاريخ", value=today)
        branch_id = branch_col.selectbox(
            "الفرع",
            [None, *branch_labels],
            format_func=lambda value: (
                "كل الفروع" if value is None else branch_labels[value]
            ),
        )
        status = status_col.selectbox(
            "الحالة",
            [None, *ORDER_STATUS_LABELS],
            format_func=lambda value: (
                "كل الحالات" if value is None else ORDER_STATUS_LABELS[value]
            ),
        )
        button_col.markdown(
            "<div style='height: 28px'></div>",
            unsafe_allow_html=True,
        )
        submitted = button_col.form_submit_button(
            "عرض التقرير", use_container_width=True
        )

    if not submitted and "daily_report_rows" not in st.session_state:
        st.info("حدد البحث ثم اضغط عرض التقرير.")
        return

    if submitted:
        if date_from > date_to:
            st.error("تاريخ البداية يجب أن يكون قبل تاريخ النهاية.")
            return

        try:
            rows = load_daily_reports(
                date_from,
                date_to,
                branch_id=branch_id,
                status=status,
            )
        except Exception as exc:  # noqa: BLE001 - surface database errors in the UI
            st.error("تعذر تحميل التقارير.")
            st.exception(exc)
            return
        st.session_state.daily_report_rows = rows
    else:
        rows = st.session_state.daily_report_rows

    total_orders = int(rows["total_orders"].sum()) if not rows.empty else 0
    total_revenue = rows["total_revenue"].sum() if not rows.empty else 0
    total_new = int(rows["total_new_customers_ordered"].sum()) if not rows.empty else 0
    total_existing = (
        int(rows["total_existing_customers_ordered"].sum()) if not rows.empty else 0
    )

    orders_col, revenue_col, new_col, existing_col = st.columns(4)
    orders_col.metric("إجمالي الطلبات", f"{total_orders:,}")
    revenue_col.metric("إجمالي الإيرادات", money(total_revenue))
    new_col.metric("عملاء جدد طلبوا", f"{total_new:,}")
    existing_col.metric("عملاء حاليون طلبوا", f"{total_existing:,}")

    if rows.empty:
        st.info("لا توجد فروع فعالة مطابقة للتقرير.")
        return

    table = rows.copy()
    table["statuses"] = table.apply(_status_summary, axis=1)
    table["total_revenue"] = table["total_revenue"].map(money)
    display_table = table[
        [
            "report_date",
            "total_orders",
            "total_revenue",
            "branch_name",
            "statuses",
            "total_new_customers_ordered",
            "total_existing_customers_ordered",
        ]
    ].rename(
        columns={
            "report_date": "التاريخ",
            "branch_name": "الفرع",
            "total_orders": "إجمالي الطلبات",
            "statuses": "الحالات",
            "total_new_customers_ordered": "عملاء جدد",
            "total_existing_customers_ordered": "عملاء حاليون",
            "total_revenue": "الإيرادات",
        }
    )
    render_print_button(
        display_table,
        title=f"التقرير اليومي من {date_from} إلى {date_to}",
        landscape=True,
    )
    render_rtl_table(display_table)
