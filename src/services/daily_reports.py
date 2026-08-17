from __future__ import annotations

from datetime import date

import pandas as pd

from src.repositories import ReportingRepository, get_reporting_repository


def load_active_branches(
    repository: ReportingRepository | None = None,
) -> list[dict[str, object]]:
    repository = repository or get_reporting_repository()
    return repository.get_active_branches().to_dict("records")


def load_daily_reports(
    date_from: date,
    date_to: date,
    *,
    branch_id: int | None = None,
    status: str | None = None,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    if date_from > date_to:
        raise ValueError("date_from must be before or equal to date_to")

    repository = repository or get_reporting_repository()
    return repository.get_daily_reports(
        date_from,
        date_to,
        branch_id=branch_id,
        status=status,
    )
