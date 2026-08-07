// scripts/lib/thresholds.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { rateMetric, rateScore } from "./thresholds.mjs";

test("LCP rating", () => {
  assert.equal(rateMetric("lcp", 2000), "good");
  assert.equal(rateMetric("lcp", 3000), "ni");
  assert.equal(rateMetric("lcp", 5000), "poor");
});

test("CLS rating (lower is better, unitless)", () => {
  assert.equal(rateMetric("cls", 0.05), "good");
  assert.equal(rateMetric("cls", 0.3), "poor");
});

test("category score rating", () => {
  assert.equal(rateScore(95), "good");
  assert.equal(rateScore(60), "ni");
  assert.equal(rateScore(30), "poor");
});

test("unknown metric returns null", () => {
  assert.equal(rateMetric("nope", 1), null);
});
