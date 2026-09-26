from datetime import date, datetime
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from rmz_market_data.prices import fetch_stock_prices


class FakeHistory:
    empty = False

    def iterrows(self):
        return [
            (
                datetime(2024, 1, 2),
                {
                    "Open": 100,
                    "High": 110,
                    "Low": 90,
                    "Close": 105,
                    "Adj Close": 104,
                    "Volume": 1234,
                },
            )
        ]


class PricesTests(TestCase):
    def test_fetches_inclusive_range_and_normalizes_symbol(self):
        requested = {}

        def history(**kwargs):
            requested["history"] = kwargs
            return FakeHistory()

        def ticker(symbol):
            requested["symbol"] = symbol
            return SimpleNamespace(history=history)

        module = SimpleNamespace(Ticker=ticker)
        with patch.dict("sys.modules", {"yfinance": module}):
            prices = fetch_stock_prices(" aapl ", date(2024, 1, 2), date(2024, 1, 2))

        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0].symbol, "AAPL")
        self.assertEqual(prices[0].adj_close, 104)
        self.assertEqual(prices[0].volume, 1234)
        self.assertEqual(requested["symbol"], "AAPL")
        self.assertEqual(
            requested["history"],
            {
                "start": "2024-01-02",
                "end": "2024-01-03",
                "auto_adjust": False,
                "actions": False,
            },
        )

    def test_returns_empty_for_no_trading_days(self):
        module = SimpleNamespace(
            Ticker=lambda _symbol: SimpleNamespace(
                history=lambda **_kwargs: SimpleNamespace(empty=True)
            )
        )
        with patch.dict("sys.modules", {"yfinance": module}):
            prices = fetch_stock_prices("SPY", date(2024, 1, 6), date(2024, 1, 7))

        self.assertEqual(prices, [])
