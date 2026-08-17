from __future__ import annotations

from datetime import date

import pandas as pd

from src.repositories import ReportingRepository, get_reporting_repository


def load_campaign_menu_items(
    repository: ReportingRepository | None = None,
) -> list[dict[str, object]]:
    repository = repository or get_reporting_repository()
    return repository.get_campaign_menu_items().to_dict("records")


def load_campaigns(
    *,
    campaign: str = "",
    menu_item_id: int | None = None,
    start_date: date | None = None,
    repository: ReportingRepository | None = None,
) -> pd.DataFrame:
    repository = repository or get_reporting_repository()
    return repository.get_campaigns(
        campaign=campaign,
        menu_item_id=menu_item_id,
        start_date=start_date,
    )
