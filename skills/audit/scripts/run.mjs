// scripts/run.mjs
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { computeScores } from "./lib/score.mjs";
import { validateAudit } from "./lib/validate.mjs";
import { decideExit, explainExit } from "./lib/gate.mjs";
import { renderReport } from "./report.mjs";
import * as headers from "./collectors/headers.mjs";
import * as tls from "./collectors/tls.mjs";
import * as lighthouse from "./collectors/lighthouse.mjs";
import * as deps from "./collectors/deps.mjs";
import * as secrets from "./collectors/secrets.mjs";

export function parseArgs(argv) {
  const flags = {}; const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--") && ["out", "runs", "fail-on"].includes(key)) { flags[key] = next; i++; }
      else flags[key] = true;
    } else positional.push(a);
  }
  return { positional, flags };
}

export function resolveTarget(arg1, arg2, cfg) {
  if (!arg1) return { name: null, url: null, localPath: arg2 ?? null };
  if (/^https?:\/\//i.test(arg1)) return { name: null, url: arg1, localPath: arg2 ?? null };
  const site = cfg.sites?.[arg1];
  if (site) return { name: arg1, url: site.url ?? null, localPath: arg2 ?? site.localPath ?? null };
  return { name: arg1, url: null, localPath: arg2 ?? null };
}

export function assemble({ target, findings, startedAt, finishedAt, tools }) {
  return { schemaVersion: 1, target, startedAt, finishedAt, tools, findings, scores: computeScores(findings) };
}

async function withTimeout(promise, ms, onTimeout) {
  let to;
  const guard = new Promise((res) => { to = setTimeout(() => res(onTimeout()), ms); });
  try { return await Promise.race([promise, guard]); } finally { clearTimeout(to); }
}

function detectChrome() {
  const p = "C:/Program Files/Google/Chrome/Application/chrome.exe";
  return existsSync(p) ? p : (process.env.CHROME_PATH ?? null);
}

function naBlock(name, nowIso, reason) {
  const category = name === "lighthouse" ? "performance" : `security.${name}`;
  return [{ id: `${name}.all`, category, metric: name, value: null, unit: "", status: "N_A", reason, evidence: "", source: "N_A", collectedAt: nowIso }];
}

async function auditOne(target, flags, cfg, nowIso, nowMs) {
  const host = target.url ? new URL(target.url).hostname : null;
  const log = (m) => process.stderr.write(`[audit] ${m}\n`);
  const base = { url: target.url, host, localPath: target.localPath, collectedAt: nowIso, now: nowMs, log };
  const strategies = flags["mobile-only"] ? ["mobile"] : flags["desktop-only"] ? ["desktop"] : ["mobile", "desktop"];
  const lhCtx = { ...base, strategies, psiKey: cfg.psiApiKey || process.env.AUDIT_PSI_KEY || null, noLab: !!flags["no-lab"], chromePath: detectChrome() };
  const secretsCtx = { ...base, secretsConfig: JSON.parse(readFileSync(new URL("../config/secrets-patterns.json", import.meta.url))) };
  const tlsCtx = { ...base, fast: !!flags.fast };

  const jobs = [];
  if (!flags["local-only"]) {
    jobs.push(["lighthouse", lighthouse.collect(lhCtx)]);
    jobs.push(["headers", headers.collect(base)]);
    jobs.push(["tls", tls.collect(tlsCtx)]);
  }
  if (!flags["live-only"]) {
    jobs.push(["deps", deps.collect(base)]);
    jobs.push(["secrets", secrets.collect(secretsCtx)]);
  }
  const results = await Promise.all(jobs.map(([name, p]) =>
    withTimeout(p.catch((e) => naBlock(name, nowIso, `collector error: ${e.message}`)),
      200000, () => naBlock(name, nowIso, "collector timeout"))
  ));
  const findings = results.flat();
  const tools = { node: process.version, chrome: detectChrome() ? "installed" : null, lighthouse: lhCtx.noLab ? null : "npx", psi: lhCtx.psiKey ? "key" : "keyless" };
  return assemble({ target, findings, startedAt: nowIso, finishedAt: new Date().toISOString(), tools });
}

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));
  const cfgPath = new URL("../audit.config.json", import.meta.url);
  const cfg = existsSync(cfgPath) ? JSON.parse(readFileSync(cfgPath)) : { sites: {} };
  const nowIso = new Date().toISOString();
  const nowMs = Date.now();

  const targets = flags.all
    ? Object.keys(cfg.sites ?? {}).map((k) => resolveTarget(k, undefined, cfg))
    : [resolveTarget(positional[0], positional[1], cfg)];

  const docs = [];
  let invalid = false;
  for (const t of targets) {
    process.stderr.write(`[audit] auditing ${t.name ?? t.url ?? "(none)"}\n`);
    const doc = await auditOne(t, flags, cfg, nowIso, nowMs);
    const v = validateAudit(doc);
    if (!v.ok) { invalid = true; process.stderr.write(`[audit] schema errors: ${v.errors.join("; ")}\n`); }
    docs.push(doc);
  }

  const outMd = typeof flags.out === "string" ? flags.out : "audit-report.md";
  const payload = docs.length === 1 ? docs[0] : docs;
  writeFileSync("audit.json", JSON.stringify(payload, null, 2));
  if (!flags["json-only"]) {
    const md = docs.map(renderReport).join("\n\n---\n\n");
    writeFileSync(outMd, md);
    process.stderr.write(`[audit] wrote ${outMd} + audit.json\n`);
  }
  // Exit contract: 0 ok · 1 gate failed (the site) · 2 crash (see catch below)
  // · 3 invalid artifact (the tool). The gate is opt-in: see scripts/lib/gate.mjs.
  const code = decideExit({ docs, flags, invalid });
  const why = explainExit(code);
  if (why) process.stderr.write(`[audit] exit ${code}: ${why}\n`);
  process.exit(code);
}

// Only run main when executed directly (not when imported by tests)
if (process.argv[1]?.replace(/\\/g, "/").endsWith("scripts/run.mjs")) {
  main().catch((e) => { process.stderr.write(`[audit] fatal: ${e.stack}\n`); process.exit(2); });
}
