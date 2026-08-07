// scripts/lib/fixes-map.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { inferHeaderTarget } from "./fixes-map.mjs";

test("vercel project → vercel.json", () => {
  assert.equal(inferHeaderTarget(["vercel.json", "package.json"]), "vercel.json (headers[])");
});
test("astro project → astro.config", () => {
  assert.equal(inferHeaderTarget(["astro.config.mjs"]), "astro.config.mjs / public/_headers");
});
test("next project → next.config", () => {
  assert.equal(inferHeaderTarget(["next.config.js"]), "next.config.js (headers())");
});
test("unknown → generic _headers", () => {
  assert.equal(inferHeaderTarget(["index.html"]), "public/_headers or server config");
});
