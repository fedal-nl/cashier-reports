from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from src.repositories.factory import get_reporting_repository
from src.repositories.postgres import PostgresReportingRepository


class RepositoryFactoryTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_reporting_repository.cache_clear()

    def test_postgres_is_the_default_repository(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            repository = get_reporting_repository()

        self.assertIsInstance(repository, PostgresReportingRepository)

    def test_unknown_repository_is_rejected(self) -> None:
        with (
            patch.dict(os.environ, {"REPORTS_REPOSITORY": "unknown"}),
            self.assertRaisesRegex(ValueError, "Unsupported reporting repository"),
        ):
            get_reporting_repository()
