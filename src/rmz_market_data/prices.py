from dataclasses import dataclass
from datetime import date, timedelta
import math

from .dates import validate_date_range
from .errors import MarketDataError


@dataclass(frozen=True)
class PriceQuote:
    date: date
    symbol: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    adj_close: float | None
    volume: int | None


def _number(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _volume(value: object) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


def fetch_stock_prices(symbol: str, start: date, end: date) -> list[PriceQuote]:
    """Fetch daily Yahoo Finance prices for the inclusive date range."""
    validate_date_range(start, end)
    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        raise MarketDataError("symbol must not be empty")

    import yfinance

    history = yfinance.Ticker(normalized_symbol).history(
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),
        auto_adjust=False,
        actions=False,
    )
    if history.empty:
        return []

    quotes = []
    for timestamp, row in history.iterrows():
        quote_date = timestamp.date()
        if not start <= quote_date <= end:
            continue
        quotes.append(
            PriceQuote(
                date=quote_date,
                symbol=normalized_symbol,
                open=_number(row.get("Open")),
                high=_number(row.get("High")),
                low=_number(row.get("Low")),
                close=_number(row.get("Close")),
                adj_close=_number(row.get("Adj Close")),
                volume=_volume(row.get("Volume")),
            )
        )
    return quotes
