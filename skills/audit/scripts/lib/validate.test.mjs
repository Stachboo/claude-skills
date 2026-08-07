// scripts/lib/validate.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { validateFinding, validateAudit } from "./validate.mjs";

const goodFinding = {
  id: "headers.hsts", category: "security.headers", metric: "HSTS",
  value: "max-age=63072000", unit: "", status: "PASS", reason: "present and strong",
  evidence: "strict-transport-security: max-age=63072000", source: "fetch",
  collectedAt: "2026-06-02T10:00:00.000Z",
};

test("valid finding passes", () => {
  assert.deepEqual(validateFinding(goodFinding), { ok: true, errors: [] });
});

test("missing status fails", () => {
  const bad = { ...goodFinding };
  delete bad.status;
  const r = validateFinding(bad);
  assert.equal(r.ok, false);
  assert.ok(r.errors.some((e) => e.includes("status")));
});

test("invalid status enum fails", () => {
  const r = validateFinding({ ...goodFinding, status: "MAYBE" });
  assert.equal(r.ok, false);
});

test("valid audit doc passes", () => {
  const doc = {
    schemaVersion: 1,
    target: { name: null, url: "https://x.com", localPath: null },
    startedAt: "2026-06-02T10:00:00.000Z", finishedAt: "2026-06-02T10:01:00.000Z",
    tools: { node: "v24.0.0", chrome: null, lighthouse: null, psi: "key" },
    findings: [goodFinding],
    scores: { overall: { value: 80, color: "green" } },
  };
  assert.equal(validateAudit(doc).ok, true);
});
