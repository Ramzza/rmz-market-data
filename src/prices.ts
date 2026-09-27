import YahooFinance from "yahoo-finance2";
import { formatDate, validateDateRange } from "./dates.js";
import { MarketDataError } from "./errors.js";

export interface PriceQuote {
  date: string;
  symbol: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  adjClose: number | null;
  volume: number | null;
}

const yahooFinance = new YahooFinance();

function finiteNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export async function fetchStockPrices(
  symbol: string,
  start: Date,
  end: Date,
): Promise<PriceQuote[]> {
  validateDateRange(start, end);
  const normalizedSymbol = symbol.trim().toUpperCase();
  if (!normalizedSymbol) throw new MarketDataError("symbol must not be empty");
  const startDate = formatDate(start);
  const endDate = formatDate(end);

  const result = await yahooFinance.chart(normalizedSymbol, {
    period1: startDate,
    period2: new Date(Date.parse(`${endDate}T00:00:00.000Z`) + 24 * 60 * 60 * 1000),
    interval: "1d",
  });

  return result.quotes
    .filter((quote) => {
      const quoteDate = formatDate(quote.date);
      return quoteDate >= startDate && quoteDate <= endDate;
    })
    .map((quote) => ({
      date: formatDate(quote.date),
      symbol: normalizedSymbol,
      open: finiteNumber(quote.open),
      high: finiteNumber(quote.high),
      low: finiteNumber(quote.low),
      close: finiteNumber(quote.close),
      adjClose: finiteNumber(quote.adjclose),
      volume: finiteNumber(quote.volume),
    }));
}
