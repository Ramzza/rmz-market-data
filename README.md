# rmz-market-data

A small Python library and CLI for retrieving historical stock and ETF prices
from Yahoo Finance and RON exchange rates from the [CursBNR archive](https://www.cursbnr.ro/arhiva-curs-bnr).

## Install

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Dates are inclusive and use `YYYY-MM-DD`. Yahoo Finance requires internet
access and may not provide data for every ticker or date.

```sh
rmz-market-data prices AAPL --start 2024-01-02 --end 2024-01-05
rmz-market-data prices SPY --start 2024-01-02 --end 2024-01-05 --format csv

rmz-market-data exchange-rates --start 2024-01-02 --end 2024-01-05
rmz-market-data exchange-rates --start 2024-01-02 --end 2024-01-05 \
  --currencies EUR USD HUF --format csv
```

Price results contain daily open, high, low, close, adjusted close, and volume.
Exchange-rate results report RON per one unit of each currency. CursBNR lists
HUF per 100 forints, so the tool normalizes that quote to RON per one HUF.
Requests use the exact requested dates; missing archive data is reported rather
than replaced with another day's rate.

The same operations are available as Python functions:

```python
from datetime import date

from rmz_market_data import fetch_exchange_rates, fetch_stock_prices

prices = fetch_stock_prices("AAPL", date(2024, 1, 2), date(2024, 1, 5))
rates = fetch_exchange_rates(date(2024, 1, 2), date(2024, 1, 5))
```

## Development

Run the standard-library test suite with:

```sh
python -m unittest discover -s tests
```
