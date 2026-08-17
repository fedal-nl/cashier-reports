from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.formatters import money


def render_orders_tab(order_trends: pd.DataFrame) -> None:
    """Render the monthly order and revenue trend chart."""
    st.subheader("الطلبات والإيرادات حسب التاريخ")

    metric_option = st.radio(
        "عرض الرسم حسب",
        options=["الطلبات", "الإيرادات"],
        horizontal=True,
    )

    y_axis = "total_orders" if metric_option == "الطلبات" else "total_revenue"
    color_axis = y_axis
    hover_data = {
        "total_orders": ":,",
        "total_revenue": ":,.0f",
    }

    fig = px.bar(
        order_trends,
        x="report_date",
        y=y_axis,
        color=color_axis,
        color_continuous_scale="Tealrose",
        labels={
            "report_date": "التاريخ",
            "total_orders": "الطلبات",
            "total_revenue": "الإيرادات",
        },
        hover_data=hover_data,
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    table = order_trends.copy()
    table["report_date"] = pd.to_datetime(table["report_date"]).dt.strftime("%Y-%m-%d")
    table["total_revenue"] = table["total_revenue"].map(money)
    styled_table = (
        table.rename(
            columns={
                "report_date": "التاريخ",
                "total_orders": "الطلبات",
                "total_revenue": "الإيرادات",
            }
        )
        .style.set_properties(**{"text-align": "right"})
        .set_table_styles(
            [
                {"selector": "th", "props": [("text-align", "right")]},
            ]
        )
    )
    st.table(
        styled_table,
    )
