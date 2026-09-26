from datetime import date
from unittest import TestCase
from unittest.mock import patch

from rmz_market_data.bnr import _parse_rates, fetch_exchange_rates
from rmz_market_data.errors import MarketDataError


RATE_PAGE = """
<table>
  <tr><td>EUR</td><td><span>Euro</span></td><td>4.9746</td><td>0</td></tr>
  <tr><td>USD</td><td>Dolarul SUA</td><td>4.4958</td><td>0</td></tr>
  <tr><td>100HUF</td><td>100 Forinți maghiari</td><td>1.2995</td><td>0</td></tr>
</table>
"""


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return RATE_PAGE.encode("utf-8")


class BnrTests(TestCase):
    def test_parses_currencies_and_normalizes_huf(self):
        rates = _parse_rates(
            RATE_PAGE,
            ("EUR", "USD", "HUF"),
            date(2024, 1, 2),
        )

        self.assertEqual(
            [(rate.currency, rate.ron_per_unit) for rate in rates],
            [("EUR", 4.9746), ("USD", 4.4958), ("HUF", 0.012995)],
        )

    @patch("rmz_market_data.bnr.urlopen", return_value=FakeResponse())
    def test_fetches_each_inclusive_date(self, urlopen):
        rates = fetch_exchange_rates(date(2024, 1, 2), date(2024, 1, 3))

        self.assertEqual(len(rates), 6)
        self.assertEqual(
            [call.args[0].full_url for call in urlopen.call_args_list],
            [
                "https://www.cursbnr.ro/arhiva-curs-bnr-2024-01-02",
                "https://www.cursbnr.ro/arhiva-curs-bnr-2024-01-03",
            ],
        )

    def test_reports_missing_currency_data(self):
        with self.assertRaisesRegex(MarketDataError, "has no HUF rate"):
            _parse_rates(
                "<table><tr><td>EUR</td><td>Euro</td><td>4.9</td></tr></table>",
                ("HUF",),
                date(2024, 1, 2),
            )

    def test_rejects_reversed_range(self):
        with self.assertRaisesRegex(MarketDataError, "on or before"):
            fetch_exchange_rates(date(2024, 1, 3), date(2024, 1, 2))
