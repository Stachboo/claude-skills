// scripts/collectors/lighthouse.mjs
import { makeFinding, na, STATUS } from "../lib/finding.mjs";
import { rateMetric, RATING_TO_STATUS } from "../lib/thresholds.mjs";
import { fetchTimeout } from "../lib/fetch-timeout.mjs";
import { runCmd, isShellSafe } from "../lib/run-cmd.mjs";

const CATS = ["performance", "accessibility", "seo", "best-practices"];
const LAB = [
  ["largest-contentful-paint", "lcp", "LCP"],
  ["cumulative-layout-shift", "cls", "CLS"],
  ["total-blocking-time", "tbt", "TBT"],
  ["server-response-time", "ttfb", "TTFB"],
];

function scoreFinding(cat, strategy, score01, at, source) {
  const v = score01 == null ? null : Math.round(score01 * 100);
  return makeFinding({ id: `${cat}.score.${strategy}`, category: cat, metric: `${cat} score (${strategy})`, value: v, unit: "score",
    status: v == null ? STATUS.N_A : (v >= 90 ? STATUS.PASS : v >= 50 ? STATUS.WARN : STATUS.FAIL),
    reason: v == null ? "no score" : `${cat} ${v}/100`, evidence: String(score01), source, collectedAt: at });
}

// Lighthouse reports which nodes failed an audit under details.items[].node.snippet.
// Keeping them turns "contrast is insufficient somewhere" into an actionable target.
const MAX_ELEMENTS = 3;
function affectedElements(a) {
  const snippets = (a.details?.items ?? [])
    .map((it) => it?.node?.snippet)
    .filter((s) => typeof s === "string" && s.trim());
  if (!snippets.length) return "";
  const shown = snippets.slice(0, MAX_ELEMENTS).map((s) => s.replace(/\s+/g, " ").trim().slice(0, 120));
  const rest = snippets.length - shown.length;
  return shown.join(" · ") + (rest > 0 ? ` … +${rest}` : "");
}

export function parsePsi(psi, { strategy, collectedAt: at, source = "psi-lab" }) {
  const out = [];
  const lr = psi.lighthouseResult ?? {};
  const cats = lr.categories ?? {};
  const audits = lr.audits ?? {};

  for (const c of CATS) out.push(scoreFinding(c, strategy, cats[c]?.score ?? null, at, source));

  // perf lab CWV
  for (const [auditKey, key, label] of LAB) {
    const v = audits[auditKey]?.numericValue;
    if (typeof v !== "number") { out.push(na({ id: `perf.${key}.lab.${strategy}`, category: "performance", metric: `${label} (${strategy}, lab)`, reason: "audit missing", collectedAt: at })); continue; }
    const val = key === "cls" ? Number(v.toFixed(3)) : Math.round(v);
    const rating = rateMetric(key, val);
    out.push(makeFinding({ id: `perf.${key}.lab.${strategy}`, category: "performance", metric: `${label} (${strategy}, lab)`, value: val, unit: key === "cls" ? "" : "ms", status: rating ? RATING_TO_STATUS[rating] : STATUS.N_A, reason: rating ? `${label} ${rating}` : "unrated", evidence: String(v), source, collectedAt: at }));
  }

  // field (CrUX)
  const fieldMetrics = psi.loadingExperience?.metrics ?? {};
  const FIELD = [["INTERACTION_TO_NEXT_PAINT", "inp", "INP"], ["LARGEST_CONTENTFUL_PAINT_MS", "lcp", "LCP"], ["CUMULATIVE_LAYOUT_SHIFT_SCORE", "cls", "CLS"]];
  for (const [fk, key, label] of FIELD) {
    const m = fieldMetrics[fk];
    if (!m) continue;
    const raw = key === "cls" ? Number((m.percentile / 100).toFixed(3)) : m.percentile;
    const rating = rateMetric(key, raw);
    out.push(makeFinding({ id: `perf.${key}.field.${strategy}`, category: "performance", metric: `${label} (${strategy}, field p75)`, value: raw, unit: key === "cls" ? "" : "ms", status: rating ? RATING_TO_STATUS[rating] : STATUS.N_A, reason: `field ${m.category ?? ""}`.trim(), evidence: JSON.stringify(m), source: "psi-field", collectedAt: at }));
  }

  // failed a11y / seo / best-practices audits → findings
  const AUDIT_CAT = { "color-contrast": "accessibility", "meta-description": "seo" };
  for (const c of ["accessibility", "seo", "best-practices"]) {
    const refs = cats[c]?.auditRefs ?? [];
    const refIds = refs.length ? refs.map((r) => r.id) : Object.keys(AUDIT_CAT).filter((k) => AUDIT_CAT[k] === c);
    for (const aid of refIds) {
      const a = audits[aid];
      if (!a || a.score === null || a.score === undefined) continue;
      if (a.score < 1) out.push(makeFinding({
        // Namespaced by form-factor like the perf findings (perf.lcp.lab.mobile):
        // without it, mobile and desktop emit the same id into one document.
        id: `${c}.${aid}.${strategy}`, category: c, metric: a.title ?? aid,
        value: a.score, unit: "",
        status: a.score === 0 ? STATUS.FAIL : STATUS.WARN,
        // The verdict, NOT a copy of the title — metric already carries the title,
        // and duplicating it made the report's two columns identical.
        reason: `${aid} scored ${a.score}/1 (${strategy})`,
        evidence: (a.description ?? "").slice(0, 200),
        elements: affectedElements(a),
        source, collectedAt: at,
      }));
    }
  }
  return out;
}

async function psiFetch(url, strategy, key) {
  const u = new URL("https://www.googleapis.com/pagespeedonline/v5/runPagespeed");
  u.searchParams.set("url", url);
  u.searchParams.set("strategy", strategy);
  for (const c of CATS) u.searchParams.append("category", c);
  if (key) u.searchParams.set("key", key);
  const res = await fetchTimeout(u, {}, 45000);
  if (!res.ok) throw new Error(`PSI HTTP ${res.status}`);
  return res.json();
}

async function localLighthouse(url, strategy, chromePath) {
  // The URL is the only dynamic value that reaches a shell command line; reject
  // anything that isn't a clean URL so it can never break out of the quoting.
  if (!isShellSafe(url)) throw new Error("url contains shell-unsafe characters");
  const env = { ...process.env, ...(chromePath ? { CHROME_PATH: chromePath } : {}) };
  const args = ["--yes", "lighthouse@latest", url, "--quiet", "--output=json", "--output-path=stdout",
    "--only-categories=performance,accessibility,seo,best-practices",
    `--form-factor=${strategy === "mobile" ? "mobile" : "desktop"}`,
    strategy === "desktop" ? "--preset=desktop" : "--throttling-method=simulate",
    `--chrome-flags=--headless=new --no-sandbox`];
  const r = await runCmd("npx", args, { env, maxBuffer: 64 * 1024 * 1024, timeout: 180000 });
  if (!r.stdout) throw new Error(r.error || r.stderr || "lighthouse produced no output");
  // Wrap to PSI-like shape so parsePsi works unchanged.
  return { lighthouseResult: JSON.parse(r.stdout) };
}

export async function collect(ctx) {
  if (!ctx.url) return [na({ id: "lighthouse.all", category: "performance", metric: "Lighthouse", reason: "no url", collectedAt: ctx.collectedAt })];
  const strategies = ctx.strategies ?? ["mobile", "desktop"];
  const out = [];
  for (const strategy of strategies) {
    let parsed = null;
    if (ctx.psiKey) {
      try { parsed = parsePsi(await psiFetch(ctx.url, strategy, ctx.psiKey), { strategy, collectedAt: ctx.collectedAt, source: "psi-lab" }); }
      catch (e) { ctx.log?.(`PSI ${strategy} failed: ${e.message}`); }
    }
    if (!parsed && !ctx.noLab) {
      try { parsed = parsePsi(await localLighthouse(ctx.url, strategy, ctx.chromePath), { strategy, collectedAt: ctx.collectedAt, source: "lighthouse-local" }); }
      catch (e) { ctx.log?.(`local lighthouse ${strategy} failed: ${e.message}`); }
    }
    if (!parsed) {
      for (const c of CATS) out.push(na({ id: `${c}.score.${strategy}`, category: c, metric: `${c} score (${strategy})`, reason: "PSI unavailable and local lab disabled/failed", collectedAt: ctx.collectedAt }));
    } else out.push(...parsed);
  }
  return out;
}
