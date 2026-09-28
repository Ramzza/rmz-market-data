# rmz-market-data

A TypeScript library and CLI for retrieving historical stock and ETF prices
from Yahoo Finance and RON exchange rates from the [CursBNR archive](https://www.cursbnr.ro/arhiva-curs-bnr).

See [PRD.md](PRD.md) for the product requirements and their test mappings.

Licensed under the [MIT License](LICENSE).

## Requirements and installation

Requires Node.js 22 or later.

```sh
npm install
npm run build
```

Run the CLI locally with `npm start --`, or install it globally with
`npm install -g .`.

## Usage

Dates are inclusive and use `YYYY-MM-DD`. Yahoo Finance requires internet
access and may not provide data for every ticker or date.

```sh
npm start -- prices AAPL --start 2024-01-02 --end 2024-01-05
npm start -- prices SPY --start 2024-01-02 --end 2024-01-05 --format csv

npm start -- exchange-rates --start 2024-01-02 --end 2024-01-05
npm start -- exchange-rates --start 2024-01-02 --end 2024-01-05 \
  --currencies EUR USD HUF --format csv
```

Price results contain daily open, high, low, close, adjusted close, and volume.
Exchange-rate results report RON per one unit of each currency. CursBNR lists
HUF per 100 forints, so the tool normalizes that quote to RON per one HUF.
Requests use the exact requested dates; missing archive data is reported rather
than replaced with another day's rate.

The same operations are available as TypeScript functions:

```ts
import { fetchExchangeRates, fetchStockPrices } from "rmz-market-data";

const prices = await fetchStockPrices("AAPL", new Date("2024-01-02"), new Date("2024-01-05"));
const rates = await fetchExchangeRates(new Date("2024-01-02"), new Date("2024-01-05"));
```

## Development

```sh
npm test
npm run build
```
