from __future__ import annotations

from datetime import date

import pandas as pd

from src.repositories import ReportingRepository, get_reporting_repository


def load_menu_item_filter_options(
    repository: ReportingRepository | None = None,
) -> list[dict[str, object]]:
    repository = repository or get_reporting_repository()
    return repository.get_menu_item_filter_options().to_dict("records")


def load_active_categories(
    repository: ReportingRepository | None = None,
) -> list[dict[str, object]]:
    repository = repository or get_reporting_repository()
    return repository.get_active_categories().to_dict("records")


def load_menu_item_sales(
    date_from: date,
    date_to: date,
    *,
    menu_item_id: int | None = None,
    branch_id: int | None = None,
    category_id: int | None = None,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    if date_from > date_to:
        raise ValueError("date_from must be before or equal to date_to")

    repository = repository or get_reporting_repository()
    return repository.get_menu_item_sales(
        date_from,
        date_to,
        menu_item_id=menu_item_id,
        branch_id=branch_id,
        category_id=category_id,
    )


def load_top_menu_items_for_period(
    date_from: date,
    date_to: date,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    repository = repository or get_reporting_repository()
    return repository.get_top_menu_items_for_period(date_from, date_to)


def load_top_menu_items_by_day(
    month_start: date,
    next_month: date,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    """Load top menu items without additional reshaping."""
    repository = repository or get_reporting_repository()
    return repository.get_top_menu_items_by_day(month_start, next_month)


def load_top_menu_items_by_month(
    month_start: date,
    next_month: date,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    """Load monthly top menu items without additional reshaping."""
    repository = repository or get_reporting_repository()
    return repository.get_top_menu_items_by_month(month_start, next_month)
