from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

from src.conf.db import get_database_config, run_query


class DatabaseConfigTests(unittest.TestCase):
    def test_get_database_config_uses_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = get_database_config()

        self.assertEqual(config, {
            "dbname": "cashier",
            "user": "postgres",
            "password": "postgres",
            "host": "db",
            "port": 5432,
        })

    def test_get_database_config_prefers_reports_variables(self) -> None:
        with patch.dict(os.environ, {
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
        }, clear=True):
            config = get_database_config()

        self.assertEqual(config, {
            "dbname": "reports-db",
            "user": "reports-user",
            "password": "reports-password",
            "host": "reports-host",
            "port": 2222,
        })


class RunQueryTests(unittest.TestCase):
    @patch("src.conf.db.get_database_config")
    @patch("src.conf.db.psycopg2.connect")
    def test_run_query_executes_and_returns_dataframe(
        self,
        mock_connect: MagicMock,
        mock_config: MagicMock,
    ) -> None:
        mock_config.return_value = {"dbname": "cashier"}
        rows = [{"total_orders": 5, "total_revenue": 1000}]

        cursor = MagicMock()
        cursor.fetchall.return_value = rows
        cursor_context = MagicMock()
        cursor_context.__enter__.return_value = cursor

        connection = MagicMock()
        connection.cursor.return_value = cursor_context
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        mock_connect.return_value = connection_context

        result = run_query("SELECT 1", ("param",))

        mock_connect.assert_called_once_with(dbname="cashier")
        connection.cursor.assert_called_once()
        cursor.execute.assert_called_once_with("SELECT 1", ("param",))
        self.assertEqual(result.to_dict("records"), rows)