from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.conf.db import get_database_config, get_database_url, get_engine, run_query


class DatabaseConfigTests(unittest.TestCase):
    def test_get_database_config_uses_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = get_database_config()

        self.assertEqual(
            config,
            {
                "dbname": "cashier",
                "user": "postgres",
                "password": "postgres",
                "host": "db",
                "port": 5432,
            },
        )

    def test_get_database_config_prefers_reports_variables(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DB_NAME": "base-db",
                "DB_USER": "base-user",
                "DB_PASSWORD": "base-password",
                "DB_HOST": "base-host",
                "DB_PORT": "1111",
                "REPORTS_DB_NAME": "reports-db",
                "REPORTS_DB_USER": "reports-user",
                "REPORTS_DB_PASSWORD": "reports-password",
                "REPORTS_DB_HOST": "reports-host",
                "REPORTS_DB_PORT": "2222",
            },
            clear=True,
        ):
            config = get_database_config()

        self.assertEqual(
            config,
            {
                "dbname": "reports-db",
                "user": "reports-user",
                "password": "reports-password",
                "host": "reports-host",
                "port": 2222,
            },
        )

    def test_get_database_url_escapes_credentials(self) -> None:
        with patch("src.conf.db.get_database_config") as mock_config:
            mock_config.return_value = {
                "dbname": "reports-db",
                "user": "reports@user",
                "password": "password/with:symbols",
                "host": "reports-host",
                "port": 5432,
            }

            database_url = get_database_url()

        self.assertEqual(database_url.username, "reports@user")
        self.assertEqual(database_url.password, "password/with:symbols")
        self.assertEqual(database_url.database, "reports-db")

    @patch("src.conf.db.create_engine")
    def test_get_engine_configures_connection_pool(
        self, mock_create_engine: MagicMock
    ) -> None:
        get_engine.clear()
        with patch("src.conf.db.get_database_url") as mock_url:
            mock_url.return_value = "postgresql+psycopg2://database"

            engine = get_engine()

        self.assertIs(engine, mock_create_engine.return_value)
        mock_create_engine.assert_called_once_with(
            "postgresql+psycopg2://database",
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
            pool_recycle=1800,
            connect_args={
                "application_name": "cashier-reports",
                "options": "-c default_transaction_read_only=on",
            },
        )
        get_engine.clear()


class RunQueryTests(unittest.TestCase):
    def setUp(self) -> None:
        run_query.clear()

    @patch("src.conf.db.pd.read_sql_query")
    @patch("src.conf.db.get_engine")
    def test_run_query_executes_and_returns_dataframe(
        self,
        mock_get_engine: MagicMock,
        mock_read_sql_query: MagicMock,
    ) -> None:
        rows = [{"total_orders": 5, "total_revenue": 1000}]
        connection = MagicMock()
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        mock_get_engine.return_value.connect.return_value = connection_context
        mock_read_sql_query.return_value = pd.DataFrame(rows)

        result = run_query("SELECT :value", {"value": "param"})

        mock_get_engine.return_value.connect.assert_called_once_with()
        statement, passed_connection = mock_read_sql_query.call_args.args
        self.assertEqual(str(statement), "SELECT :value")
        self.assertIs(passed_connection, connection)
        self.assertEqual(
            mock_read_sql_query.call_args.kwargs["params"], {"value": "param"}
        )
        self.assertEqual(result.to_dict("records"), rows)
