// scripts/collectors/headers.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { parseHeaders } from "./headers.mjs";

const AT = "2026-06-02T10:00:00.000Z";
const ctx = { url: "https://x.com", collectedAt: AT };
const find = (fs, id) => fs.find((f) => f.id === id);

test("missing CSP and HSTS are FAIL", () => {
  const fs = parseHeaders({}, ctx);
  assert.equal(find(fs, "headers.csp").status, "FAIL");
  assert.equal(find(fs, "headers.hsts").status, "FAIL");
});

test("strong HSTS passes, short HSTS warns", () => {
  assert.equal(find(parseHeaders({ "strict-transport-security": "max-age=63072000; includeSubDomains" }, ctx), "headers.hsts").status, "PASS");
  assert.equal(find(parseHeaders({ "strict-transport-security": "max-age=600" }, ctx), "headers.hsts").status, "WARN");
});

test("CSP with unsafe-inline warns; restrictive passes", () => {
  assert.equal(find(parseHeaders({ "content-security-policy": "default-src 'self' 'unsafe-inline'" }, ctx), "headers.csp").status, "WARN");
  assert.equal(find(parseHeaders({ "content-security-policy": "default-src 'self'" }, ctx), "headers.csp").status, "PASS");
});

test("nosniff binary", () => {
  assert.equal(find(parseHeaders({ "x-content-type-options": "nosniff" }, ctx), "headers.nosniff").status, "PASS");
  assert.equal(find(parseHeaders({}, ctx), "headers.nosniff").status, "FAIL");
});

test("clickjacking satisfied by frame-ancestors in CSP", () => {
  const fs = parseHeaders({ "content-security-policy": "frame-ancestors 'none'" }, ctx);
  assert.equal(find(fs, "headers.clickjacking").status, "PASS");
});

test("server version leak warns", () => {
  assert.equal(find(parseHeaders({ "x-powered-by": "Express 4.18.2" }, ctx), "headers.leak").status, "WARN");
});
