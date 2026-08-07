// scripts/collectors/lighthouse.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parsePsi } from "./lighthouse.mjs";

const AT = "2026-06-02T10:00:00.000Z";
const psi = JSON.parse(readFileSync(new URL("../../tests/fixtures/psi-sample.json", import.meta.url)));
const find = (fs, id) => fs.find((f) => f.id === id);

test("category scores become findings on 0-100 scale", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.equal(find(fs, "performance.score.mobile").value, 74);
  assert.equal(find(fs, "accessibility.score.mobile").value, 91);
  assert.equal(find(fs, "seo.score.mobile").value, 83);
  assert.equal(find(fs, "best-practices.score.mobile").value, 96);
});

test("LCP lab is rated; TBT 540 is WARN (ni)", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.equal(find(fs, "perf.lcp.lab.mobile").value, 3200);
  assert.equal(find(fs, "perf.lcp.lab.mobile").status, "WARN"); // 3200 => ni
  assert.equal(find(fs, "perf.tbt.lab.mobile").status, "WARN"); // 540 => ni (cutoffs [200,600])
});

test("INP is field-only", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.equal(find(fs, "perf.inp.field.mobile").value, 230);
  assert.equal(find(fs, "perf.inp.lab.mobile"), undefined);
});

test("failed a11y/seo audits become FAIL findings", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.ok(find(fs, "accessibility.color-contrast.mobile"));
  assert.equal(find(fs, "accessibility.color-contrast.mobile").status, "FAIL");
  assert.equal(find(fs, "seo.meta-description.mobile").status, "FAIL");
});

// Perf findings already namespace by form-factor (perf.lcp.lab.mobile). Audit
// findings did not, so mobile and desktop emitted the SAME id into one document.
test("audit finding ids stay unique across form-factors", () => {
  const both = [
    ...parsePsi(psi, { strategy: "mobile", collectedAt: AT }),
    ...parsePsi(psi, { strategy: "desktop", collectedAt: AT }),
  ];
  const ids = both.map((f) => f.id);
  assert.equal(new Set(ids).size, ids.length, "duplicate finding ids across form-factors");
});

// metric and reason were both set to the audit title, which made the report's
// "Critère" and "Détail" columns identical by construction.
test("reason carries the verdict, not a copy of the metric title", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  const f = find(fs, "accessibility.color-contrast.mobile");
  assert.notEqual(f.reason, f.metric);
});

test("audit description is kept as evidence", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.match(find(fs, "accessibility.color-contrast.mobile").evidence, /Low-contrast text/);
});

test("offending elements are captured from audit details", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.match(find(fs, "accessibility.color-contrast.mobile").elements, /adv-btn/);
});

test("elements is an empty string when the audit reports no nodes", () => {
  const fs = parsePsi(psi, { strategy: "mobile", collectedAt: AT });
  assert.equal(find(fs, "seo.meta-description.mobile").elements, "");
});
