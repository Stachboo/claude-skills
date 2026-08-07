// scripts/collectors/tls.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { gradeCert, parseSslLabs } from "./tls.mjs";

const AT = "2026-06-02T10:00:00.000Z";
const ctx = { url: "https://x.com", host: "x.com", collectedAt: AT };
const find = (fs, id) => fs.find((f) => f.id === id);

test("expiry < 14d is FAIL, 20d is WARN, 90d is PASS", () => {
  assert.equal(find(gradeCert({ daysLeft: 5, protocol: "TLSv1.3", hostnameMatch: true, selfSigned: false }, ctx), "tls.expiry").status, "FAIL");
  assert.equal(find(gradeCert({ daysLeft: 20, protocol: "TLSv1.3", hostnameMatch: true, selfSigned: false }, ctx), "tls.expiry").status, "WARN");
  assert.equal(find(gradeCert({ daysLeft: 90, protocol: "TLSv1.3", hostnameMatch: true, selfSigned: false }, ctx), "tls.expiry").status, "PASS");
});

test("legacy protocol is FAIL", () => {
  assert.equal(find(gradeCert({ daysLeft: 90, protocol: "TLSv1", hostnameMatch: true, selfSigned: false }, ctx), "tls.protocol").status, "FAIL");
  assert.equal(find(gradeCert({ daysLeft: 90, protocol: "TLSv1.3", hostnameMatch: true, selfSigned: false }, ctx), "tls.protocol").status, "PASS");
});

test("self-signed and hostname mismatch are FAIL", () => {
  const fs = gradeCert({ daysLeft: 90, protocol: "TLSv1.3", hostnameMatch: false, selfSigned: true }, ctx);
  assert.equal(find(fs, "tls.trust").status, "FAIL");
});

test("parseSslLabs maps grade", () => {
  const f = parseSslLabs({ endpoints: [{ grade: "A+" }] }, ctx);
  assert.equal(f.value, "A+");
  assert.equal(f.status, "PASS");
  const b = parseSslLabs({ endpoints: [{ grade: "F" }] }, ctx);
  assert.equal(b.status, "FAIL");
});
