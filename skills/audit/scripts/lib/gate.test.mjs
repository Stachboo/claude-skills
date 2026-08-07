// scripts/lib/gate.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { decideExit, explainExit } from "./gate.mjs";

// A doc is only ever inspected through its `scores` map, so tests build the
// minimum shape: { <dim>: { value, color } } with color in green|yellow|red|gray.
const doc = (colors) => ({
  scores: Object.fromEntries(Object.entries(colors).map(([d, c]) => [d, { value: c === "gray" ? null : 50, color: c }])),
});

const RED = doc({ security: "red", performance: "green", overall: "red" });

test("no flags: a red score does not fail the run (gate is opt-in)", () => {
  assert.equal(decideExit({ docs: [RED], flags: {} }), 0);
});

test("--fail-on red: a red score fails the run", () => {
  assert.equal(decideExit({ docs: [RED], flags: { "fail-on": "red" } }), 1);
});

test("--json-only keeps gating on red (spec §138 back-compat)", () => {
  assert.equal(decideExit({ docs: [RED], flags: { "json-only": true } }), 1);
});

const YELLOW = doc({ security: "yellow", performance: "green", overall: "yellow" });
const GREEN = doc({ security: "green", performance: "green", overall: "green" });

test("--fail-on yellow fails on a yellow score", () => {
  assert.equal(decideExit({ docs: [YELLOW], flags: { "fail-on": "yellow" } }), 1);
});

test("--fail-on yellow passes when every score is green", () => {
  assert.equal(decideExit({ docs: [GREEN], flags: { "fail-on": "yellow" } }), 0);
});

test("--fail-on red ignores yellow", () => {
  assert.equal(decideExit({ docs: [YELLOW], flags: { "fail-on": "red" } }), 0);
});

test("--fail-on never overrides --json-only", () => {
  assert.equal(decideExit({ docs: [RED], flags: { "json-only": true, "fail-on": "never" } }), 0);
});

test("an unknown --fail-on level throws instead of silently gating", () => {
  // A typo must not be read as a stricter or looser policy: it must be loud.
  assert.throws(() => decideExit({ docs: [RED], flags: { "fail-on": "rd" } }), /fail-on/);
});

test("--fail-on with no value throws (flag given but empty)", () => {
  assert.throws(() => decideExit({ docs: [RED], flags: { "fail-on": true } }), /fail-on/);
});

test("an artifact that fails schema validation exits 3, gate or not", () => {
  // The tool produced something false: that is the tool's fault, not the
  // site's, and must not read as a clean run.
  assert.equal(decideExit({ docs: [GREEN], flags: {}, invalid: true }), 3);
});

test("invalid artifact outranks a failed gate", () => {
  assert.equal(decideExit({ docs: [RED], flags: { "fail-on": "red" }, invalid: true }), 3);
});

test("a valid artifact never exits 3", () => {
  assert.equal(decideExit({ docs: [GREEN], flags: {}, invalid: false }), 0);
});

// A dimension whose findings are all N/A scores gray, never red — so a color
// gate cannot see it. Deliberate: --local-only legitimately grays out the live
// dimensions. Incompleteness is therefore its own opt-in axis.
const GRAY = doc({ security: "gray", performance: "green", overall: "green" });

test("--fail-on red does not fail an unassessed (gray) dimension", () => {
  assert.equal(decideExit({ docs: [GRAY], flags: { "fail-on": "red" } }), 0);
});

test("--require-complete fails when a dimension was never assessed", () => {
  assert.equal(decideExit({ docs: [GRAY], flags: { "require-complete": true } }), 1);
});

test("--require-complete passes when every dimension was assessed", () => {
  assert.equal(decideExit({ docs: [GREEN], flags: { "require-complete": true } }), 0);
});

test("--require-complete is orthogonal to color: it alone ignores a red score", () => {
  assert.equal(decideExit({ docs: [RED], flags: { "require-complete": true } }), 0);
});

test("--all: one bad doc among several fails the run", () => {
  assert.equal(decideExit({ docs: [GREEN, GREEN, RED], flags: { "fail-on": "red" } }), 1);
});

test("--all: every doc green passes", () => {
  assert.equal(decideExit({ docs: [GREEN, GREEN], flags: { "fail-on": "red" } }), 0);
});

test("explainExit tells the caller which fault each code means", () => {
  // 1 blames the site, 3 blames the auditor: a CI log must not confuse them.
  assert.match(explainExit(1), /gate/i);
  assert.match(explainExit(3), /invalid|schema/i);
  assert.equal(explainExit(0), null);
});
