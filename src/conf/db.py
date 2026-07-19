from __future__ import annotations

import os

import pandas as pd
import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor


def get_database_config() -> dict[str, str | int]:
    """Build the Postgres connection settings from reporting env vars."""
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


@st.cache_data(ttl=300)
def run_query(query: str, params: tuple[object, ...]) -> pd.DataFrame:
    """Run a read-only report query and return the result as a DataFrame."""
    with psycopg2.connect(**get_database_config()) as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    return pd.DataFrame(rows)