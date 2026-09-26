from datetime import date

from .errors import MarketDataError


def validate_date_range(start: date, end: date) -> None:
    if not isinstance(start, date) or not isinstance(end, date):
        raise MarketDataError("start and end must be datetime.date values")
    if start > end:
        raise MarketDataError("start date must be on or before end date")
