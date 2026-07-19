from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


def render_menu_items_tab(
    menu_items_by_day: pd.DataFrame,
    menu_items_by_month: pd.DataFrame,
) -> None:
    """Render daily and monthly top menu item reports."""
    st.subheader("أكثر 10 عناصر طلبا حسب اليوم")

    if menu_items_by_day.empty:
        st.info("لا توجد طلبات عناصر في الشهر الحالي.")
        return

    menu_items_by_day = menu_items_by_day.copy()
    menu_items_by_day["report_date"] = pd.to_datetime(menu_items_by_day["report_date"]).dt.date
    menu_items_by_day["label"] = (
        "رقم "
        + menu_items_by_day["item_rank"].astype(str)
        + " "
        + menu_items_by_day["menu_item_name"]
    )

    fig = px.bar(
        menu_items_by_day,
        x="report_date",
        y="total_quantity",
        color="menu_item_name",
        text="label",
        barmode="group",
        labels={
            "report_date": "التاريخ",
            "total_quantity": "الكمية المطلوبة",
            "menu_item_name": "عنصر القائمة",
        },
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        menu_items_by_day[[
            "report_date",
            "item_rank",
            "menu_item_name",
            "total_quantity",
        ]].rename(columns={
            "report_date": "التاريخ",
            "item_rank": "الترتيب",
            "menu_item_name": "عنصر القائمة",
            "total_quantity": "الكمية المطلوبة",
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("أفضل 10 عناصر في الشهر الحالي")

    if menu_items_by_month.empty:
        st.info("لا توجد طلبات عناصر مجمعة في الشهر الحالي.")
        return

    monthly_fig = px.bar(
        menu_items_by_month,
        x="menu_item_name",
        y="total_quantity",
        color="total_quantity",
        color_continuous_scale="Tealrose",
        labels={
            "menu_item_name": "عنصر القائمة",
            "total_quantity": "إجمالي الكمية المطلوبة",
        },
    )
    monthly_fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title=None,
        yaxis_title=None,
    )
    st.plotly_chart(monthly_fig, use_container_width=True)

    st.dataframe(
        menu_items_by_month.rename(columns={
            "menu_item_name": "عنصر القائمة",
            "total_quantity": "إجمالي الكمية المطلوبة",
        }),
        hide_index=True,
        use_container_width=True,
    )