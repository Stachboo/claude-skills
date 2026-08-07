// scripts/lib/run-cmd.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { quoteArg, buildCommand, isShellSafe } from "./run-cmd.mjs";

test("quoteArg leaves simple args untouched", () => {
  assert.equal(quoteArg("audit"), "audit");
  assert.equal(quoteArg("--json"), "--json");
  assert.equal(quoteArg("https://example.com"), "https://example.com");
});

test("quoteArg double-quotes args with spaces or metachars", () => {
  assert.equal(quoteArg("--chrome-flags=--headless=new --no-sandbox"), '"--chrome-flags=--headless=new --no-sandbox"');
  assert.match(quoteArg("a;b"), /^".*"$/);
});

test("buildCommand joins safely", () => {
  assert.equal(buildCommand("npm", ["audit", "--json"]), "npm audit --json");
});

test("isShellSafe accepts clean URLs, rejects metachars", () => {
  assert.equal(isShellSafe("https://example.com/path?a=1"), true);
  assert.equal(isShellSafe("https://x.com; rm -rf /"), false);
  assert.equal(isShellSafe("https://x.com/`whoami`"), false);
  assert.equal(isShellSafe("https://x.com/$(id)"), false);
});
