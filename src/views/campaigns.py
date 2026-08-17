from __future__ import annotations

import streamlit as st

from src.services.campaigns import load_campaign_menu_items, load_campaigns


CHANNEL_LABELS = {
    "tiktok": "TikTok",
    "instagram": "Instagram",
    "online": "Online",
}


def render_campaigns_tab() -> None:
    st.subheader("الحملات الإعلانية")
    st.caption("إنشاء الحملات وتعديلها يتم من خلال لوحة إدارة Django.")

    try:
        menu_items = load_campaign_menu_items()
    except Exception as exc:
        st.error("تعذر تحميل الوجبات المتاحة.")
        st.exception(exc)
        return

    item_labels = {int(item["id"]): str(item["name_ar"]) for item in menu_items}
    item_ids = list(item_labels)

    search_col, item_col, date_col = st.columns(3)
    campaign_search = search_col.text_input("اسم أو رقم الحملة")
    menu_item_search = item_col.selectbox(
        "الوجبة",
        [None, *item_ids],
        format_func=lambda value: "كل الوجبات" if value is None else item_labels[value],
    )
    start_date_search = date_col.date_input("تاريخ البداية", value=None)

    try:
        campaigns = load_campaigns(
            campaign=campaign_search.strip(),
            menu_item_id=menu_item_search,
            start_date=start_date_search,
        )
    except Exception as exc:
        st.error("تعذر تحميل الحملات.")
        st.exception(exc)
        return

    if campaigns.empty:
        st.info("لا توجد حملات مطابقة.")
        return

    table = campaigns.copy()
    table["channel"] = table["channel"].map(
        lambda value: CHANNEL_LABELS.get(value, value)
    )
    table = table.rename(
        columns={
            "campaign_id": "رقم الحملة",
            "campaign_name": "الحملة",
            "channel": "القناة",
            "start_date": "البداية",
            "end_date": "النهاية",
            "amount_spent": "المصروف",
            "current_revenue": "الإيراد",
            "profit": "الربح",
            "total_orders": "الطلبات",
            "menu_items": "الوجبات",
        }
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "المصروف": st.column_config.NumberColumn(format="%.2f"),
            "الإيراد": st.column_config.NumberColumn(format="%.2f"),
            "الربح": st.column_config.NumberColumn(format="%.2f"),
        },
    )
