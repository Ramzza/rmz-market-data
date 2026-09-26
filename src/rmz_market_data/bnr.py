from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from .dates import validate_date_range
from .errors import MarketDataError


DEFAULT_CURRENCIES = ("EUR", "USD", "HUF")
_ARCHIVE_URL = "https://www.cursbnr.ro/arhiva-curs-bnr-{date}"


@dataclass(frozen=True)
class ExchangeRate:
    date: date
    currency: str
    ron_per_unit: float


class _RateTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None


def _parse_rates(page: str, requested: tuple[str, ...], rate_date: date) -> list[ExchangeRate]:
    parser = _RateTableParser()
    parser.feed(page)
    parsed: dict[str, float] = {}
    for row in parser.rows:
        if len(row) < 3:
            continue
        match = re.fullmatch(r"(100)?([A-Z]{3})", row[0])
        if match is None:
            continue
        unit = int(match.group(1) or "1")
        currency = match.group(2)
        try:
            value = Decimal(row[2].replace(",", "."))
        except InvalidOperation:
            continue
        if value.is_finite():
            parsed[currency] = float(value / unit)

    missing = [currency for currency in requested if currency not in parsed]
    if missing:
        raise MarketDataError(
            f"cursbnr.ro has no {', '.join(missing)} rate for {rate_date.isoformat()}"
        )
    return [
        ExchangeRate(date=rate_date, currency=currency, ron_per_unit=parsed[currency])
        for currency in requested
    ]


def _fetch_day(rate_date: date, currencies: tuple[str, ...]) -> list[ExchangeRate]:
    url = _ARCHIVE_URL.format(date=rate_date.isoformat())
    request = Request(url, headers={"User-Agent": "rmz-market-data/0.1"})
    try:
        with urlopen(request, timeout=20) as response:
            page = response.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError) as error:
        raise MarketDataError(
            f"could not retrieve cursbnr.ro rates for {rate_date.isoformat()}: {error}"
        ) from error
    return _parse_rates(page, currencies, rate_date)


def fetch_exchange_rates(
    start: date,
    end: date,
    currencies: tuple[str, ...] = DEFAULT_CURRENCIES,
) -> list[ExchangeRate]:
    """Fetch exact-date RON rates from the CursBNR archive, inclusive."""
    validate_date_range(start, end)
    normalized_currencies = tuple(currency.strip().upper() for currency in currencies)
    if not normalized_currencies or any(not currency for currency in normalized_currencies):
        raise MarketDataError("at least one non-empty currency code is required")
    if len(set(normalized_currencies)) != len(normalized_currencies):
        raise MarketDataError("currency codes must not contain duplicates")

    results = []
    rate_date = start
    while rate_date <= end:
        results.extend(_fetch_day(rate_date, normalized_currencies))
        rate_date += timedelta(days=1)
    return results
