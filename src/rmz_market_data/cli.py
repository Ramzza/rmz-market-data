import argparse
from dataclasses import asdict
from datetime import date, datetime
import csv
import json
import sys
from typing import Any

from .bnr import DEFAULT_CURRENCIES, fetch_exchange_rates
from .errors import MarketDataError
from .prices import fetch_stock_prices


def _date(value: str) -> date:
    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format") from error


def _add_date_range(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start", required=True, type=_date, help="Inclusive start date")
    parser.add_argument("--end", required=True, type=_date, help="Inclusive end date")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rmz-market-data",
        description="Fetch historical stock, ETF, and RON exchange-rate data.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    prices = commands.add_parser("prices", help="Fetch daily stock or ETF prices")
    prices.add_argument("symbol", help="Yahoo Finance ticker symbol")
    _add_date_range(prices)
    prices.add_argument("--format", choices=("json", "csv"), default="json")

    rates = commands.add_parser("exchange-rates", help="Fetch daily RON exchange rates")
    _add_date_range(rates)
    rates.add_argument(
        "--currencies",
        nargs="+",
        default=list(DEFAULT_CURRENCIES),
        metavar="CODE",
        help="Currency codes (default: EUR USD HUF)",
    )
    rates.add_argument("--format", choices=("json", "csv"), default="json")
    return parser


def _write_results(
    results: list[Any],
    output_format: str,
    empty_fields: list[str],
) -> None:
    records = [asdict(result) for result in results]
    for record in records:
        record["date"] = record["date"].isoformat()
    if output_format == "json":
        print(json.dumps(records, indent=2))
        return
    fields = list(records[0]) if records else empty_fields
    writer = csv.DictWriter(sys.stdout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    try:
        if args.command == "prices":
            results = fetch_stock_prices(args.symbol, args.start, args.end)
        else:
            results = fetch_exchange_rates(
                args.start,
                args.end,
                tuple(args.currencies),
            )
    except MarketDataError as error:
        parser.exit(2, f"{parser.prog}: error: {error}\n")
    empty_fields = (
        ["date", "symbol", "open", "high", "low", "close", "adj_close", "volume"]
        if args.command == "prices"
        else ["date", "currency", "ron_per_unit"]
    )
    _write_results(results, args.format, empty_fields)
