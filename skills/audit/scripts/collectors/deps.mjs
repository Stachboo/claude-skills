// scripts/collectors/deps.mjs
import { existsSync } from "node:fs";
import { join } from "node:path";
import { makeFinding, na, STATUS } from "../lib/finding.mjs";
import { runCmd } from "../lib/run-cmd.mjs";

const CAT = "security.deps";

function summarize(counts, source, at) {
  const { low = 0, moderate = 0, high = 0, critical = 0 } = counts;
  const status = critical > 0 || high > 0 ? STATUS.FAIL : moderate > 0 ? STATUS.WARN : STATUS.PASS;
  const parts = [critical && `${critical} critical`, high && `${high} high`, moderate && `${moderate} moderate`, low && `${low} low`].filter(Boolean);
  return makeFinding({ id: "deps.summary", category: CAT, metric: "Dependency CVEs", value: parts.join(", ") || "0", unit: "count", status, reason: parts.length ? `vulnerabilities found` : "no known vulnerabilities", evidence: JSON.stringify(counts), source, collectedAt: at });
}

export function parseNpmAudit(json, ctx) {
  const at = ctx.collectedAt;
  const v = json?.metadata?.vulnerabilities ?? {};
  const out = [summarize(v, "npm-audit", at)];
  for (const [name, info] of Object.entries(json?.vulnerabilities ?? {})) {
    if (!["high", "critical"].includes(info.severity)) continue;
    const title = Array.isArray(info.via) ? (info.via.find((x) => typeof x === "object")?.title ?? name) : name;
    const fix = info.fixAvailable && typeof info.fixAvailable === "object" ? `${info.fixAvailable.name}@${info.fixAvailable.version}` : (info.fixAvailable ? "available" : "none");
    out.push(makeFinding({ id: `deps.cve.${name}`, category: CAT, metric: `${name} (${info.severity})`, value: info.range ?? "", unit: "", status: STATUS.FAIL, reason: title, evidence: `fix: ${fix}`, source: "npm-audit", collectedAt: at }));
  }
  return out;
}

export function parsePnpmAudit(json, ctx) {
  const at = ctx.collectedAt;
  const adv = json?.advisories ?? {};
  const counts = { low: 0, moderate: 0, high: 0, critical: 0 };
  const out = [];
  for (const a of Object.values(adv)) {
    if (counts[a.severity] !== undefined) counts[a.severity]++;
    if (["high", "critical"].includes(a.severity)) {
      const name = a.module_name ?? "pkg";
      out.push(makeFinding({ id: `deps.cve.${name}`, category: CAT, metric: `${name} (${a.severity})`, value: a.vulnerable_versions ?? "", unit: "", status: STATUS.FAIL, reason: a.title ?? name, evidence: `patched: ${a.patched_versions ?? "?"}`, source: "pnpm-audit", collectedAt: at }));
    }
  }
  return [summarize(counts, "pnpm-audit", at), ...out];
}

export async function collect(ctx) {
  const at = ctx.collectedAt;
  const dir = ctx.localPath;
  if (!dir) return [na({ id: "deps.all", category: CAT, metric: "Dependency CVEs", reason: "no local path provided", collectedAt: at })];
  try {
    if (existsSync(join(dir, "pnpm-lock.yaml"))) {
      const r = await runCmd("pnpm", ["audit", "--json"], { cwd: dir });
      const json = JSON.parse(r.stdout || "{}");
      return parsePnpmAudit(json, ctx);
    }
    if (existsSync(join(dir, "package-lock.json"))) {
      const r = await runCmd("npm", ["audit", "--json"], { cwd: dir });
      return parseNpmAudit(JSON.parse(r.stdout || "{}"), ctx);
    }
    if (existsSync(join(dir, "yarn.lock"))) {
      const r = await runCmd("yarn", ["npm", "audit", "--json"], { cwd: dir });
      // yarn berry emits NDJSON; take last metadata-bearing line
      const lines = r.stdout.trim().split("\n").map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
      const meta = lines.find((l) => l.metadata) ?? { metadata: { vulnerabilities: {} }, vulnerabilities: {} };
      return parseNpmAudit(meta, ctx);
    }
    if (existsSync(join(dir, "requirements.txt"))) {
      const r = await runCmd("pip-audit", ["-r", join(dir, "requirements.txt"), "-f", "json"], { cwd: dir });
      if (r.error) return [na({ id: "deps.all", category: CAT, metric: "Dependency CVEs", reason: "pip-audit not installed", collectedAt: at })];
      const json = JSON.parse(r.stdout || "{}");
      const vulns = (json.dependencies ?? []).flatMap((d) => (d.vulns ?? []).map((vv) => ({ name: d.name, ...vv })));
      const counts = { high: vulns.length, low: 0, moderate: 0, critical: 0 };
      return [summarize(counts, "pip-audit", at), ...vulns.map((vv) => makeFinding({ id: `deps.cve.${vv.name}`, category: CAT, metric: `${vv.name}`, value: vv.id ?? "", unit: "", status: STATUS.FAIL, reason: (vv.description ?? "").slice(0, 120), evidence: `fix: ${(vv.fix_versions ?? []).join(",")}`, source: "pip-audit", collectedAt: at }))];
    }
    return [na({ id: "deps.all", category: CAT, metric: "Dependency CVEs", reason: "no recognized lockfile", collectedAt: at })];
  } catch (e) {
    return [na({ id: "deps.all", category: CAT, metric: "Dependency CVEs", reason: `audit failed: ${e.message}`, collectedAt: at })];
  }
}
