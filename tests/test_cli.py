from contextlib import redirect_stdout
from datetime import date
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from rmz_market_data.cli import main


class CliTests(TestCase):
    @patch("rmz_market_data.cli.fetch_stock_prices", return_value=[])
    def test_empty_csv_still_has_price_columns(self, _fetch):
        output = StringIO()
        with patch(
            "sys.argv",
            [
                "rmz-market-data",
                "prices",
                "SPY",
                "--start",
                "2024-01-06",
                "--end",
                "2024-01-07",
                "--format",
                "csv",
            ],
        ), redirect_stdout(output):
            main()

        self.assertEqual(
            output.getvalue().strip(),
            "date,symbol,open,high,low,close,adj_close,volume",
        )
