// scripts/collectors/deps.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { parseNpmAudit } from "./deps.mjs";

const AT = "2026-06-02T10:00:00.000Z";
const ctx = { collectedAt: AT };

test("npm audit v2 severities → counts + status", () => {
  const json = { metadata: { vulnerabilities: { info: 0, low: 2, moderate: 1, high: 1, critical: 0, total: 4 } },
    vulnerabilities: { lodash: { name: "lodash", severity: "high", via: [{ title: "Prototype Pollution", url: "x" }], range: "<4.17.21", fixAvailable: { name: "lodash", version: "4.17.21" } } } };
  const fs = parseNpmAudit(json, ctx);
  const summary = fs.find((f) => f.id === "deps.summary");
  assert.equal(summary.status, "FAIL"); // any high/critical => FAIL
  assert.ok(summary.value.includes("1 high"));
  assert.ok(fs.some((f) => f.id === "deps.cve.lodash"));
});

test("clean audit → PASS", () => {
  const json = { metadata: { vulnerabilities: { info: 0, low: 0, moderate: 0, high: 0, critical: 0, total: 0 } }, vulnerabilities: {} };
  assert.equal(parseNpmAudit(json, ctx).find((f) => f.id === "deps.summary").status, "PASS");
});
