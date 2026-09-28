import assert from "node:assert/strict";
import test from "node:test";
import { main } from "../src/cli.js";

const ratePage = `
<table>
  <tr><td>EUR</td><td>Euro</td><td>4.9746</td><td>0</td></tr>
</table>
`;

test("PRD-003: CLI emits exchange rates as JSON and CSV", async (t) => {
  let output = "";
  t.mock.method(process.stdout, "write", (chunk: string | Uint8Array) => {
    output += String(chunk);
    return true;
  });
  t.mock.method(globalThis, "fetch", async () => new Response(ratePage, { status: 200 }));

  const args = [
    "node",
    "rmz-market-data",
    "exchange-rates",
    "--start",
    "2024-01-02",
    "--end",
    "2024-01-02",
    "--currencies",
    "EUR",
  ];
  await main(args);
  assert.deepEqual(JSON.parse(output), [
    { date: "2024-01-02", currency: "EUR", ron_per_unit: 4.9746 },
  ]);

  output = "";
  await main([...args, "--format", "csv"]);
  assert.equal(output, "date,currency,ron_per_unit\n2024-01-02,EUR,4.9746\n");
});
