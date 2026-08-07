// scripts/run.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { parseArgs, resolveTarget, assemble } from "./run.mjs";

test("parseArgs splits positionals and flags", () => {
  const a = parseArgs(["https://x.com", "C:/repo", "--mobile-only", "--out", "r.md"]);
  assert.equal(a.positional[0], "https://x.com");
  assert.equal(a.positional[1], "C:/repo");
  assert.equal(a.flags["mobile-only"], true);
  assert.equal(a.flags.out, "r.md");
});

test("parseArgs reads --fail-on as a value flag, not a bare switch", () => {
  // Otherwise "red" is swallowed as a positional and becomes the audit target.
  const a = parseArgs(["https://x.com", "--fail-on", "red"]);
  assert.equal(a.flags["fail-on"], "red");
  assert.deepEqual(a.positional, ["https://x.com"]);
});

test("resolveTarget treats scheme as URL", () => {
  const r = resolveTarget("https://x.com", undefined, { sites: {} });
  assert.equal(r.url, "https://x.com");
  assert.equal(r.name, null);
});

test("resolveTarget expands a config key", () => {
  const cfg = { sites: { demo: { url: "https://demo.test", localPath: "C:/demo" } } };
  const r = resolveTarget("demo", undefined, cfg);
  assert.equal(r.url, "https://demo.test");
  assert.equal(r.localPath, "C:/demo");
  assert.equal(r.name, "demo");
});

test("assemble builds a valid audit doc", () => {
  const findings = [{ id: "headers.csp", category: "security.headers", metric: "CSP", value: null, unit: "", status: "FAIL", reason: "absent", evidence: "", source: "fetch", collectedAt: "2026-06-02T10:00:00.000Z" }];
  const doc = assemble({ target: { name: null, url: "https://x.com", localPath: null }, findings, startedAt: "2026-06-02T10:00:00.000Z", finishedAt: "2026-06-02T10:01:00.000Z", tools: { node: "v24.0.0", chrome: null, lighthouse: null, psi: null } });
  assert.equal(doc.schemaVersion, 1);
  assert.ok(doc.scores.overall);
});
