// scripts/lib/score.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { computeScores } from "./score.mjs";

const AT = "2026-06-02T10:00:00.000Z";
const f = (o) => ({ unit: "", evidence: "", source: "x", collectedAt: AT, value: null, reason: "", ...o });

test("category score finding is used directly", () => {
  const findings = [f({ id: "accessibility.score", category: "accessibility", metric: "a11y", value: 95, status: "PASS" })];
  const s = computeScores(findings);
  assert.equal(s.accessibility.value, 95);
  assert.equal(s.accessibility.color, "green");
});

test("averages mobile+desktop category scores (real lighthouse ids)", () => {
  const findings = [
    f({ id: "performance.score.mobile", category: "performance", value: 70, status: "WARN" }),
    f({ id: "performance.score.desktop", category: "performance", value: 90, status: "PASS" }),
    // a failed audit in the same dimension must NOT double-count when a score exists
    f({ id: "performance.render-blocking", category: "performance", value: 0, status: "FAIL" }),
  ];
  const s = computeScores(findings);
  assert.equal(s.performance.value, 80); // (70+90)/2
  assert.equal(s.performance.color, "yellow");
});

test("security penalties subtract from 100", () => {
  const findings = [
    f({ id: "headers.csp", category: "security.headers", status: "FAIL" }),   // -25
    f({ id: "headers.hsts", category: "security.headers", status: "WARN" }),  // -8
  ];
  const s = computeScores(findings);
  assert.equal(s.security.value, 67);
  assert.equal(s.security.color, "ni" === "ni" ? "yellow" : "yellow"); // 67 => yellow
});

test("overall is red if any dimension red", () => {
  const findings = [
    f({ id: "performance.score", category: "performance", value: 95, status: "PASS" }),
    f({ id: "security.tls.expiry", category: "security.tls", status: "FAIL" }),
    f({ id: "security.tls.proto", category: "security.tls", status: "FAIL" }),
    f({ id: "security.tls.cipher", category: "security.tls", status: "FAIL" }),
    f({ id: "security.tls.chain", category: "security.tls", status: "FAIL" }),
  ];
  const s = computeScores(findings);
  assert.equal(s.overall.color, "red");
});

test("N_A findings do not penalize (mixed dimension)", () => {
  const findings = [
    f({ id: "security.deps.cve", category: "security.deps", status: "N_A" }),
    f({ id: "headers.csp", category: "security.headers", status: "PASS" }),
  ];
  const s = computeScores(findings);
  assert.equal(s.security.value, 100);
});

test("a .summary roll-up is not double-counted with its .cve finding", () => {
  const findings = [
    f({ id: "deps.summary", category: "security.deps", status: "FAIL" }),     // roll-up, excluded
    f({ id: "deps.cve.vitest", category: "security.deps", status: "FAIL" }),  // the real issue, -25
  ];
  const s = computeScores(findings);
  assert.equal(s.security.value, 75); // only one -25, not -50
});

test("a fully-N/A dimension is null/gray, never a green 100", () => {
  const findings = [
    f({ id: "performance.score.mobile", category: "performance", status: "N_A" }),
    f({ id: "performance.score.desktop", category: "performance", status: "N_A" }),
  ];
  const s = computeScores(findings);
  assert.equal(s.performance.value, null);
  assert.equal(s.performance.color, "gray");
});
