// scripts/lib/finding.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { makeFinding, na, STATUS } from "./finding.mjs";
import { validateFinding } from "./validate.mjs";

const AT = "2026-06-02T10:00:00.000Z";

test("makeFinding fills defaults and validates", () => {
  const f = makeFinding({
    id: "headers.csp", category: "security.headers", metric: "CSP",
    value: null, status: STATUS.FAIL, reason: "absent", source: "fetch", collectedAt: AT,
  });
  assert.equal(f.unit, "");
  assert.equal(f.evidence, "");
  assert.equal(validateFinding(f).ok, true);
});

test("na() builds an N_A finding with reason", () => {
  const f = na({ id: "perf.lcp", category: "performance", metric: "LCP", reason: "PSI 429", collectedAt: AT });
  assert.equal(f.status, "N_A");
  assert.equal(f.value, null);
  assert.equal(f.source, "N_A");
  assert.equal(f.reason, "PSI 429");
  assert.equal(validateFinding(f).ok, true);
});
