from __future__ import annotations

from datetime import date
from decimal import Decimal
import unittest
from unittest.mock import patch

from src.utils.dates import get_current_month_bounds, get_month_days
from src.utils.formatters import money


class DateUtilsTests(unittest.TestCase):
    @patch("src.utils.dates.date")
    def test_get_current_month_bounds_rolls_to_next_year(self, mock_date: object) -> None:
        mock_date.today.return_value = date(2026, 12, 15)

        month_start, next_month = get_current_month_bounds()

        self.assertEqual(month_start, date(2026, 12, 1))
        self.assertEqual(next_month, date(2027, 1, 1))

    @patch("src.utils.dates.date")
    def test_get_current_month_bounds_rolls_to_next_month(self, mock_date: object) -> None:
        mock_date.today.return_value = date(2026, 7, 15)

        month_start, next_month = get_current_month_bounds()

        self.assertEqual(month_start, date(2026, 7, 1))
        self.assertEqual(next_month, date(2026, 8, 1))

    def test_get_month_days_returns_all_dates_in_range(self) -> None:
        result = get_month_days(date(2026, 7, 1), date(2026, 7, 4))

        self.assertEqual(result["report_date"].tolist(), [
            date(2026, 7, 1),
            date(2026, 7, 2),
            date(2026, 7, 3),
        ])


class FormatterTests(unittest.TestCase):
    def test_money_formats_whole_number_currency(self) -> None:
        self.assertEqual(money(Decimal("12345.67")), "12,346 د.ع")
        self.assertEqual(money(0), "0 د.ع")