# Product requirements

## Outcome

Provide TypeScript library functions and a CLI for daily stock, ETF, and RON exchange-rate data.

## Requirements

- **PRD-001 - Historical prices:** Fetch daily Yahoo Finance quotes for a normalized ticker and inclusive date range; return only in-range quotes and represent non-finite quote values as `null`.
  **Verification:** `tests/prices.test.ts::PRD-001: normalizes the symbol and returns only daily quotes within the inclusive range`.
- **PRD-002 - RON exchange rates:** Fetch requested currencies for every inclusive date from the BNR archive and normalize rates to RON per unit, including the archive's HUF-per-100 quote; report missing rates and reversed ranges.
  **Verification:** `tests/bnr.test.ts` tests prefixed `PRD-002`.
- **PRD-003 - CLI output and dates:** Parse valid `YYYY-MM-DD` dates and emit exchange-rate results as JSON by default or CSV when requested.
  **Verification:** `tests/dates.test.ts::PRD-003: parses only valid YYYY-MM-DD dates`; `tests/cli.test.ts::PRD-003: CLI emits exchange rates as JSON and CSV`.
