from __future__ import annotations

import os
from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor


st.set_page_config(
    page_title="تقارير الكاشير",
    layout="wide",
)


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


def get_database_config() -> dict[str, str | int]:
    """Build the Postgres connection settings from Streamlit/reporting env vars."""
    return {
        "dbname": os.getenv("REPORTS_DB_NAME", os.getenv("DB_NAME", "cashier")),
        "user": os.getenv("REPORTS_DB_USER", os.getenv("DB_USER", "postgres")),
        "password": os.getenv(
            "REPORTS_DB_PASSWORD",
            os.getenv("DB_PASSWORD", "postgres"),
        ),
        "host": os.getenv("REPORTS_DB_HOST", os.getenv("DB_HOST", "db")),
        "port": int(os.getenv("REPORTS_DB_PORT", os.getenv("DB_PORT", "5432"))),
    }


def get_current_month_bounds() -> tuple[date, date]:
    """Return the first day of the current month and the first day of next month."""
    month_start = date.today().replace(day=1)

    if month_start.month == 12:
        next_month = month_start.replace(
            year=month_start.year + 1,
            month=1,
        )
    else:
        next_month = month_start.replace(
            month=month_start.month + 1,
        )

    return month_start, next_month


def get_month_days(month_start: date, next_month: date) -> pd.DataFrame:
    """Create one row per day in the selected month range for complete trend charts."""
    days = pd.date_range(
        start=month_start,
        end=next_month - timedelta(days=1),
        freq="D",
    )

    return pd.DataFrame({
        "report_date": days.date,
    })


@st.cache_data(ttl=300)
def run_query(query: str, params: tuple[date, ...]) -> pd.DataFrame:
    """Run a read-only report query and return the result as a DataFrame."""
    with psycopg2.connect(**get_database_config()) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    return pd.DataFrame(rows)


def money(value: Decimal | float | int | str) -> str:
    """Format revenue values as Iraqi dinar style whole-number currency."""
    amount = float(value or 0)
    return f"{amount:,.0f} د.ع"


def load_order_trends(month_start: date, next_month: date) -> pd.DataFrame:
    """Load daily order count and revenue totals for the current month."""
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

    data = run_query(query, (month_start, next_month))
    days = get_month_days(month_start, next_month)

    if data.empty:
        data = pd.DataFrame(columns=[
            "report_date",
            "total_orders",
            "total_revenue",
        ])

    data["report_date"] = pd.to_datetime(
        data["report_date"],
    ).dt.date

    merged = days.merge(
        data,
        on="report_date",
        how="left",
    )
    merged["total_orders"] = merged["total_orders"].fillna(0).astype(int)
    merged["total_revenue"] = merged["total_revenue"].fillna(0).astype(float)

    return merged


def load_customer_trends(month_start: date, next_month: date) -> pd.DataFrame:
    """Load daily new and existing customer totals for customers who ordered."""
    query = """
        WITH customer_order_days AS (
            SELECT
                created_at::date AS report_date,
                customer_id
            FROM orders_order
            WHERE created_at >= %s
              AND created_at < %s
            GROUP BY report_date, customer_id
        ),
        first_orders AS (
            SELECT
                customer_id,
                MIN(created_at)::date AS first_order_date
            FROM orders_order
            GROUP BY customer_id
        )
        SELECT
            customer_order_days.report_date,
            COUNT(*) FILTER (
                WHERE first_orders.first_order_date = customer_order_days.report_date
            ) AS new_customers,
            COUNT(*) FILTER (
                WHERE first_orders.first_order_date < customer_order_days.report_date
            ) AS existing_customers
        FROM customer_order_days
        JOIN first_orders
          ON first_orders.customer_id = customer_order_days.customer_id
        GROUP BY customer_order_days.report_date
        ORDER BY customer_order_days.report_date;
    """

    data = run_query(query, (month_start, next_month))
    days = get_month_days(month_start, next_month)

    if data.empty:
        data = pd.DataFrame(columns=[
            "report_date",
            "new_customers",
            "existing_customers",
        ])

    data["report_date"] = pd.to_datetime(
        data["report_date"],
    ).dt.date

    merged = days.merge(
        data,
        on="report_date",
        how="left",
    )
    merged["new_customers"] = merged["new_customers"].fillna(0).astype(int)
    merged["existing_customers"] = merged["existing_customers"].fillna(0).astype(int)

    return merged


def load_top_customers(month_start: date, next_month: date) -> pd.DataFrame:
    """Load the top ten customers by monthly revenue and include their order counts."""
    query = """
        SELECT
            COALESCE(NULLIF(TRIM(customer.name), ''), 'عميل غير معروف') AS customer_name,
            COUNT(orders.id) AS total_orders,
            COALESCE(SUM(orders.total_price), 0) AS total_revenue
        FROM orders_order AS orders
        JOIN orders_customer AS customer
          ON customer.id = orders.customer_id
        WHERE orders.created_at >= %s
          AND orders.created_at < %s
        GROUP BY customer.id, customer.name
        ORDER BY total_revenue DESC, total_orders DESC, customer_name ASC
        LIMIT 10;
    """

    return run_query(query, (month_start, next_month))


def load_top_menu_items_by_day(month_start: date, next_month: date) -> pd.DataFrame:
    """Load each day's top three ordered menu items using aggregated order-item rows."""
    query = """
        WITH daily_menu_items AS (
            SELECT
                orders.created_at::date AS report_date,
                order_items.menu_item_name_ar AS menu_item_name,
                SUM(order_items.quantity) AS total_quantity
            FROM orders_orderitem AS order_items
            JOIN orders_order AS orders
              ON orders.id = order_items.order_id
            WHERE orders.created_at >= %s
              AND orders.created_at < %s
            GROUP BY report_date, menu_item_name
        ),
        ranked_menu_items AS (
            SELECT
                report_date,
                menu_item_name,
                total_quantity,
                ROW_NUMBER() OVER (
                    PARTITION BY report_date
                    ORDER BY total_quantity DESC, menu_item_name ASC
                ) AS item_rank
            FROM daily_menu_items
        )
        SELECT
            report_date,
            menu_item_name,
            total_quantity,
            item_rank
        FROM ranked_menu_items
        WHERE item_rank <= 3
        ORDER BY report_date, item_rank;
    """

    return run_query(query, (month_start, next_month))


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


def render_orders_tab(order_trends: pd.DataFrame) -> None:
    """Render the monthly order and revenue trend chart."""
    st.subheader("الطلبات والإيرادات حسب التاريخ")

    fig = px.bar(
        order_trends,
        x="report_date",
        y="total_orders",
        color="total_orders",
        color_continuous_scale="Tealrose",
        labels={
            "report_date": "التاريخ",
            "total_orders": "الطلبات",
            "total_revenue": "الإيرادات",
        },
        hover_data={
            "total_revenue": ":,.0f",
        },
    )
    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

    table = order_trends.copy()
    table["total_revenue"] = table["total_revenue"].map(money)
    st.dataframe(
        table.rename(columns={
            "report_date": "التاريخ",
            "total_orders": "الطلبات",
            "total_revenue": "الإيرادات",
        }),
        hide_index=True,
        use_container_width=True,
    )


def render_customers_tab(
    customer_trends: pd.DataFrame,
    top_customers: pd.DataFrame,
) -> None:
    """Render customer acquisition trends and the monthly top customer table."""
    st.subheader("العملاء الجدد والحاليون حسب التاريخ")

    long_data = customer_trends.melt(
        id_vars="report_date",
        value_vars=[
            "new_customers",
            "existing_customers",
        ],
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


def render_menu_items_tab(menu_items: pd.DataFrame) -> None:
    """Render each day's top three menu items by ordered quantity."""
    st.subheader("أكثر 3 عناصر طلبا حسب اليوم")

    if menu_items.empty:
        st.info("لا توجد طلبات عناصر في الشهر الحالي.")
        return

    menu_items["report_date"] = pd.to_datetime(
        menu_items["report_date"],
    ).dt.date
    menu_items["label"] = (
        "رقم "
        + menu_items["item_rank"].astype(str)
        + " "
        + menu_items["menu_item_name"]
    )

    fig = px.bar(
        menu_items,
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
        menu_items[[
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


def main() -> None:
    """Render the Streamlit dashboard with monthly cashier report tabs."""
    apply_rtl_styles()
    month_start, next_month = get_current_month_bounds()

    st.title("تقارير الكاشير")
    st.caption(
        f"الشهر الحالي: {month_start:%Y-%m-%d} إلى "
        f"{next_month - timedelta(days=1):%Y-%m-%d}"
    )

    try:
        order_trends = load_order_trends(month_start, next_month)
        customer_trends = load_customer_trends(month_start, next_month)
        top_customers = load_top_customers(month_start, next_month)
        menu_items = load_top_menu_items_by_day(month_start, next_month)
    except Exception as exc:
        st.error("تعذر تحميل بيانات التقارير من قاعدة البيانات.")
        st.exception(exc)
        return

    render_metric_row(order_trends, customer_trends)

    orders_tab, customers_tab, menu_items_tab = st.tabs([
        "الطلبات",
        "العملاء",
        "أكثر الوجبات طلب",
    ])

    with orders_tab:
        render_orders_tab(order_trends)

    with customers_tab:
        render_customers_tab(customer_trends, top_customers)

    with menu_items_tab:
        render_menu_items_tab(menu_items)


if __name__ == "__main__":
    main()
