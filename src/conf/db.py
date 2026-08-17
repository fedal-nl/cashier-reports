from __future__ import annotations

import os
from collections.abc import Mapping

import pandas as pd
import streamlit as st
from sqlalchemy import URL, Engine, create_engine, text


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


def get_database_url() -> URL:
    """Build a safely escaped SQLAlchemy URL from the reporting configuration."""
    config = get_database_config()
    return URL.create(
        drivername="postgresql+psycopg2",
        username=str(config["user"]),
        password=str(config["password"]),
        host=str(config["host"]),
        port=int(config["port"]),
        database=str(config["dbname"]),
    )


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    """Create one pooled SQLAlchemy Engine for the Streamlit process."""
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_size=int(os.getenv("REPORTS_DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("REPORTS_DB_MAX_OVERFLOW", "5")),
        pool_recycle=int(os.getenv("REPORTS_DB_POOL_RECYCLE", "1800")),
        connect_args={
            "application_name": "cashier-reports",
            "options": "-c default_transaction_read_only=on",
        },
    )


@st.cache_data(ttl=300)
def run_query(
    query: str,
    params: Mapping[str, object] | None = None,
) -> pd.DataFrame:
    """Execute parameterized SQL through a pooled connection."""
    with get_engine().connect() as connection:
        return pd.read_sql_query(text(query), connection, params=dict(params or {}))
