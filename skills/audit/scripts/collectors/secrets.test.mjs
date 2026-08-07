// scripts/collectors/secrets.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { scanText } from "./secrets.mjs";

const AT = "2026-06-02T10:00:00.000Z";
const cfg = JSON.parse(readFileSync(new URL("../../config/secrets-patterns.json", import.meta.url)));
const ctx = { collectedAt: AT, file: "src/config.js" };

test("detects an AWS access key and redacts the value", () => {
  const fs = scanText('const k = "AKIA1234567890ABCDEF";', cfg, ctx);
  assert.equal(fs.length, 1);
  assert.equal(fs[0].category, "security.secrets");
  assert.equal(fs[0].status, "FAIL");
  assert.ok(!fs[0].evidence.includes("AKIA1234567890ABCDEF"));   // never leak the value
  assert.match(fs[0].evidence, /AKIA.*\*{3,}/);                  // partial mask
  assert.equal(fs[0].id, "secrets.src/config.js:1:aws-access-key");
});

test("clean text yields no findings", () => {
  assert.equal(scanText("const sum = a + b;\nreturn sum;", cfg, ctx).length, 0);
});

test("entropy gate suppresses low-entropy generic matches", () => {
  const fs = scanText('password = "aaaaaaaaaaaaaaaa";', cfg, ctx);  // low entropy → suppressed
  assert.equal(fs.length, 0);
});
