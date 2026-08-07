// scripts/collectors/secrets.mjs
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { makeFinding, na, STATUS } from "../lib/finding.mjs";
import { runCmd } from "../lib/run-cmd.mjs";

const CAT = "security.secrets";

function shannon(s) {
  if (!s) return 0;
  const freq = {};
  for (const ch of s) freq[ch] = (freq[ch] || 0) + 1;
  let h = 0;
  for (const c of Object.values(freq)) { const p = c / s.length; h -= p * Math.log2(p); }
  return h;
}

function redact(match) {
  if (match.length <= 8) return match.slice(0, 2) + "***";
  return match.slice(0, 4) + "*".repeat(Math.min(8, match.length - 8)) + match.slice(-2);
}

export function scanText(text, cfg, ctx) {
  const out = [];
  const lines = text.split(/\r?\n/);
  for (const p of cfg.patterns) {
    // JS RegExp has no inline (?i) flag — translate a leading (?i) into the `i` flag.
    let src = p.rx, flags = "g";
    if (src.startsWith("(?i)")) { src = src.slice(4); flags += "i"; }
    const rx = new RegExp(src, flags);
    lines.forEach((line, i) => {
      let m;
      rx.lastIndex = 0;
      while ((m = rx.exec(line)) !== null) {
        const hit = m[0];
        if (p.entropy && shannon(hit) < (cfg.minEntropy ?? 3.5)) continue;
        out.push(makeFinding({
          id: `secrets.${ctx.file}:${i + 1}:${p.id}`, category: CAT,
          metric: `${p.id} in ${ctx.file}`, value: `${ctx.file}:${i + 1}`, unit: "",
          status: STATUS.FAIL, reason: `possible ${p.id}${ctx.inHistory ? " (git history)" : ""}`,
          evidence: redact(hit), source: "scanner", collectedAt: ctx.collectedAt,
        }));
        if (!rx.global) break;
      }
    });
  }
  return out;
}

function allowlisted(file, globs) {
  return globs.some((g) => {
    const rx = new RegExp("^" + g.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*\*/g, "::").replace(/\*/g, "[^/]*").replace(/::/g, ".*") + "$");
    return rx.test(file.replace(/\\/g, "/"));
  });
}

export async function collect(ctx) {
  const at = ctx.collectedAt;
  const dir = ctx.localPath;
  if (!dir) return [na({ id: "secrets.all", category: CAT, metric: "Exposed secrets", reason: "no local path provided", collectedAt: at })];
  const cfg = ctx.secretsConfig;
  // Use cwd rather than `-C <dir>`: on Windows with shell:true a path containing
  // spaces passed as an arg gets word-split by the shell and breaks git.
  const ls = await runCmd("git", ["ls-files"], { cwd: dir });
  if (ls.error || ls.code !== 0) return [na({ id: "secrets.all", category: CAT, metric: "Exposed secrets", reason: "not a git repo / git unavailable", collectedAt: at })];
  const files = ls.stdout.split("\n").map((s) => s.trim()).filter(Boolean).filter((f) => !allowlisted(f, cfg.allowlistGlobs));
  const out = [];
  for (const f of files) {
    let text;
    try { text = readFileSync(join(dir, f), "utf8"); } catch { continue; }
    if (text.length > 2 * 1024 * 1024) continue; // skip huge/binary
    out.push(...scanText(text, cfg, { file: f, collectedAt: at }));
  }
  // git history pass (best-effort)
  const log = await runCmd("git", ["log", "-p", "--all", "-S", "AKIA", "--max-count=50"], { cwd: dir, timeout: 60000 });
  if (!log.error && log.stdout) out.push(...scanText(log.stdout, cfg, { file: "<git-history>", inHistory: true, collectedAt: at }));
  if (out.length === 0) out.push(makeFinding({ id: "secrets.summary", category: CAT, metric: "Exposed secrets", value: "0", unit: "count", status: STATUS.PASS, reason: "no secrets detected in tracked files", evidence: `${files.length} files scanned`, source: "scanner", collectedAt: at }));
  return out;
}
