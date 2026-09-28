import assert from "node:assert/strict";
import test from "node:test";
import YahooFinance from "yahoo-finance2";
import { fetchStockPrices } from "../src/prices.js";

test("PRD-001: normalizes the symbol and returns only daily quotes within the inclusive range", async (t) => {
  const calls: Array<{ symbol: string; options: unknown }> = [];
  const quotes = [
    { date: new Date("2024-01-01T12:00:00Z"), open: 8, high: 9, low: 7, close: 8, adjclose: 8, volume: 80 },
    { date: new Date("2024-01-02T12:00:00Z"), open: 10, high: 12, low: 9, close: 11, adjclose: 11, volume: 100 },
    { date: new Date("2024-01-03T12:00:00Z"), open: Number.NaN, high: Number.POSITIVE_INFINITY, low: null, close: 0, adjclose: undefined, volume: 30 },
    { date: new Date("2024-01-05T12:00:00Z"), open: 14, high: 15, low: 13, close: 14, adjclose: 14, volume: 140 },
    { date: new Date("2024-01-06T12:00:00Z"), open: 15, high: 16, low: 14, close: 15, adjclose: 15, volume: 150 },
  ];
  t.mock.method(YahooFinance.prototype, "chart", async (symbol, options) => {
    calls.push({ symbol, options });
    return { quotes } as never;
  });

  const result = await fetchStockPrices(
    " aapl ",
    new Date("2024-01-02T00:00:00Z"),
    new Date("2024-01-05T00:00:00Z"),
  );

  assert.deepEqual(result, [
    { date: "2024-01-02", symbol: "AAPL", open: 10, high: 12, low: 9, close: 11, adjClose: 11, volume: 100 },
    { date: "2024-01-03", symbol: "AAPL", open: null, high: null, low: null, close: 0, adjClose: null, volume: 30 },
    { date: "2024-01-05", symbol: "AAPL", open: 14, high: 15, low: 13, close: 14, adjClose: 14, volume: 140 },
  ]);
  assert.deepEqual(calls, [{
    symbol: "AAPL",
    options: {
      period1: "2024-01-02",
      period2: new Date("2024-01-06T00:00:00.000Z"),
      interval: "1d",
    },
  }]);
});
