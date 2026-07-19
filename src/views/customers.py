from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.formatters import money


def render_customers_tab(
    customer_trends: pd.DataFrame,
    top_customers: pd.DataFrame,
) -> None:
    """Render customer acquisition trends and the monthly top customer table."""
    st.subheader("العملاء الجدد والحاليون حسب التاريخ")

    long_data = customer_trends.melt(
        id_vars="report_date",
        value_vars=["new_customers", "existing_customers"],
        var_name="customer_type",
        value_name="customers",
    )
    long_data["customer_type"] = long_data["customer_type"].replace({
        "new_customers": "عملاء جدد",
        "existing_customers": "عملاء حاليون",
    })

    fig = px.area(
        long_data,
        x="report_date",
        y="customers",
        color="customer_type",
        labels={
            "report_date": "التاريخ",
            "customers": "العملاء",
            "customer_type": "نوع العميل",
        },
        color_discrete_map={
            "عملاء جدد": "#17a2b8",
            "عملاء حاليون": "#6f42c1",
        },
    )
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("أفضل 10 عملاء هذا الشهر")

    if top_customers.empty:
        st.info("لا توجد طلبات عملاء في الشهر الحالي.")
        return

    table = top_customers.copy()
    table["total_revenue"] = table["total_revenue"].map(money)
    st.dataframe(
        table.rename(columns={
            "customer_name": "العميل",
            "total_orders": "الطلبات",
            "total_revenue": "الإيرادات",
        }),
        hide_index=True,
        use_container_width=True,
    )