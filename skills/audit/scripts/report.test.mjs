// scripts/report.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { renderReport } from "./report.mjs";

const audit = JSON.parse(readFileSync(new URL("../tests/fixtures/audit-sample.json", import.meta.url)));

test("renders header with url and tool provenance", () => {
  const md = renderReport(audit);
  assert.match(md, /# Audit/);
  assert.match(md, /https:\/\/demo\.test/);
  assert.match(md, /node v24/i);
});

test("overall red badge appears", () => {
  assert.match(renderReport(audit), /🔴/);
});

test("N_A deps render with reason, never a silent pass", () => {
  const md = renderReport(audit);
  assert.match(md, /N\/A/);
  assert.match(md, /no local path provided/);
});

test("failed a11y audit is listed", () => {
  assert.match(renderReport(audit), /sufficient contrast ratio/);
});

const clone = () => JSON.parse(JSON.stringify(audit));
const rowFor = (md, label) => md.split("\n").find((l) => l.startsWith(`| ${label} |`));
const desktopLcp = (source) => ({
  id: "perf.lcp.lab.desktop", category: "performance", metric: "LCP (desktop, lab)",
  value: 1700, unit: "ms", status: "PASS", reason: "LCP good", evidence: "1700",
  source, collectedAt: "2026-06-02T10:00:30.000Z",
});

// Spec §7.3: "chaque cellule = valeur+couleur+source". Without it, a PSI number
// and a local-Lighthouse number sit side by side looking comparable.
test("CWV cells name the source they came from", () => {
  assert.match(rowFor(renderReport(audit), "LCP"), /psi-lab/);
});

test("N/A cells keep their reason instead of a source", () => {
  const a = clone();
  a.findings.push({
    id: "perf.tbt.lab.mobile", category: "performance", metric: "TBT (mobile, lab)",
    value: null, unit: "ms", status: "N_A", reason: "audit missing", evidence: "",
    source: "N_A", collectedAt: "2026-06-02T10:00:30.000Z",
  });
  assert.match(rowFor(renderReport(a), "TBT"), /N\/A — audit missing/);
});

test("lab numbers from two different engines raise a comparability warning", () => {
  const a = clone();
  a.findings.push(desktopLcp("lighthouse-local"));
  assert.match(renderReport(a), /moteurs différents/i);
});

test("no comparability warning when both form-factors share one engine", () => {
  const a = clone();
  a.findings.push(desktopLcp("psi-lab"));
  assert.doesNotMatch(renderReport(a), /moteurs différents/i);
});

// Spec §7.4 wants the audit description ("comment corriger"), not the title again.
test("a11y row shows the description rather than repeating the criterion", () => {
  const a = clone();
  const f = a.findings.find((x) => x.id === "accessibility.color-contrast");
  f.reason = "score 0/1";
  f.evidence = "Low-contrast text is difficult or impossible for many users to read.";
  assert.match(renderReport(a), /Low-contrast text is difficult/);
});

test("a11y row lists the offending elements when the collector captured them", () => {
  const a = clone();
  a.findings.find((x) => x.id === "accessibility.color-contrast").elements = "<a class=\"adv-btn\">";
  assert.match(renderReport(a), /adv-btn/);
});

// Capturing DOM snippets means arbitrary markup now reaches a markdown table.
test("a pipe inside a captured DOM snippet cannot shear the table", () => {
  const a = clone();
  a.findings.find((x) => x.id === "accessibility.color-contrast").elements = '<div data-x="a|b">';
  const row = renderReport(a).split("\n").find((l) => l.includes("data-x"));
  const unescapedPipes = (row.match(/(?<!\\)\|/g) ?? []).length;
  assert.equal(unescapedPipes, 6, "a 5-column row must have exactly 6 delimiting pipes");
});

test("an audit failing on both form-factors renders one row, not two", () => {
  const a = clone();
  const base = a.findings.find((x) => x.id === "accessibility.color-contrast");
  base.id = "accessibility.color-contrast.mobile";
  a.findings.push({ ...base, id: "accessibility.color-contrast.desktop", source: "lighthouse-local" });
  const rows = renderReport(a).split("\n").filter((l) => l.includes("Contrast insufficient"));
  assert.equal(rows.length, 1, "one audit must not produce two rows");
  assert.match(rows[0], /mobile.*desktop/);
});

test("deterministic: same input → same output", () => {
  assert.equal(renderReport(audit), renderReport(audit));
});
