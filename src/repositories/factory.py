from __future__ import annotations

import os
from functools import lru_cache

from src.repositories.base import ReportingRepository
from src.repositories.postgres import PostgresReportingRepository


@lru_cache(maxsize=1)
def get_reporting_repository() -> ReportingRepository:
    """Build the configured reporting data-source adapter."""
    repository_type = os.getenv("REPORTS_REPOSITORY", "postgres").lower()

    if repository_type == "postgres":
        return PostgresReportingRepository()

    raise ValueError(f"Unsupported reporting repository: {repository_type}")
