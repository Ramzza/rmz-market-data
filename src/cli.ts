#!/usr/bin/env node
import { Command, Option } from "commander";
import { pathToFileURL } from "node:url";
import { DEFAULT_CURRENCIES, fetchExchangeRates } from "./bnr.js";
import { formatDate, parseDate } from "./dates.js";
import { MarketDataError } from "./errors.js";
import { fetchStockPrices, type PriceQuote } from "./prices.js";

type OutputFormat = "json" | "csv";
type RecordRow = Record<string, string | number | null>;

function serializeRows(
  rows: readonly RecordRow[],
  format: OutputFormat,
  emptyColumns: readonly string[],
): string {
  if (format === "json") return JSON.stringify(rows, null, 2);

  const columns = rows.length === 0 ? emptyColumns : Object.keys(rows[0]);
  const escape = (value: string | number | null): string => {
    const text = value === null ? "" : String(value);
    return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  };
  return [
    columns.join(","),
    ...rows.map((row) => columns.map((key) => escape(row[key] as string | number | null)).join(",")),
  ].join("\n");
}

function writeRows(
  rows: readonly object[],
  format: OutputFormat,
  emptyColumns: readonly string[],
): void {
  const fieldNames: Record<string, string> = {
    adjClose: "adj_close",
    ronPerUnit: "ron_per_unit",
  };
  const records = rows.map((row) =>
    Object.fromEntries(
      Object.entries(row).map(([key, value]) => [fieldNames[key] ?? key, value]),
    ) as RecordRow,
  );
  process.stdout.write(`${serializeRows(records, format, emptyColumns)}\n`);
}

export async function main(argv = process.argv): Promise<void> {
  const program = new Command();
  program
    .name("rmz-market-data")
    .description("Fetch historical stock, ETF, and RON exchange-rate data.");

  program
    .command("prices")
    .description("Fetch daily stock or ETF prices from Yahoo Finance")
    .argument("<symbol>", "Yahoo Finance ticker symbol")
    .requiredOption("--start <date>", "Inclusive start date (YYYY-MM-DD)")
    .requiredOption("--end <date>", "Inclusive end date (YYYY-MM-DD)")
    .addOption(
      new Option("--format <format>", "Output format: json or csv")
        .choices(["json", "csv"])
        .default("json"),
    )
    .action(async (symbol: string, options: { start: string; end: string; format: string }) => {
      const results: PriceQuote[] = await fetchStockPrices(
        symbol,
        parseDate(options.start),
        parseDate(options.end),
      );
      writeRows(results, options.format as OutputFormat, [
        "date",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
      ]);
    });

  program
    .command("exchange-rates")
    .description("Fetch daily RON exchange rates from cursbnr.ro")
    .requiredOption("--start <date>", "Inclusive start date (YYYY-MM-DD)")
    .requiredOption("--end <date>", "Inclusive end date (YYYY-MM-DD)")
    .option("--currencies <codes...>", "Currency codes", [...DEFAULT_CURRENCIES])
    .addOption(
      new Option("--format <format>", "Output format: json or csv")
        .choices(["json", "csv"])
        .default("json"),
    )
    .action(async (options: { start: string; end: string; currencies: string[]; format: string }) => {
      const rates = await fetchExchangeRates(
        parseDate(options.start),
        parseDate(options.end),
        options.currencies,
      );
      writeRows(rates, options.format as OutputFormat, [
        "date",
        "currency",
        "ron_per_unit",
      ]);
    });

  try {
    await program.parseAsync(argv);
  } catch (error) {
    if (error instanceof MarketDataError) {
      process.stderr.write(`rmz-market-data: error: ${error.message}\n`);
      process.exitCode = 2;
      return;
    }
    throw error;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
