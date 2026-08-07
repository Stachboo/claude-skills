// scripts/collectors/headers.mjs
import { makeFinding, na, STATUS } from "../lib/finding.mjs";
import { fetchTimeout } from "../lib/fetch-timeout.mjs";

const CAT = "security.headers";
const mk = (id, metric, value, status, reason, evidence, at) =>
  makeFinding({ id, category: CAT, metric, value, unit: "", status, reason, evidence, source: "fetch", collectedAt: at });

export function parseHeaders(h, ctx) {
  const at = ctx.collectedAt;
  const get = (k) => h[k] ?? null;
  const out = [];

  // HSTS
  const hsts = get("strict-transport-security");
  if (!hsts) out.push(mk("headers.hsts", "HSTS", null, STATUS.FAIL, "Strict-Transport-Security absent", "", at));
  else {
    const m = /max-age=(\d+)/i.exec(hsts);
    const age = m ? Number(m[1]) : 0;
    const sub = /includesubdomains/i.test(hsts);
    if (age < 15552000 || !sub) out.push(mk("headers.hsts", "HSTS", hsts, STATUS.WARN, "max-age < 180d or no includeSubDomains", hsts, at));
    else out.push(mk("headers.hsts", "HSTS", hsts, STATUS.PASS, "strong HSTS", hsts, at));
  }

  // CSP
  const csp = get("content-security-policy");
  const cspRO = get("content-security-policy-report-only");
  if (!csp && !cspRO) out.push(mk("headers.csp", "CSP", null, STATUS.FAIL, "Content-Security-Policy absent", "", at));
  else if (!csp && cspRO) out.push(mk("headers.csp", "CSP", cspRO, STATUS.WARN, "report-only CSP (not enforced)", cspRO, at));
  else if (/unsafe-inline|unsafe-eval|default-src\s+\*/i.test(csp)) out.push(mk("headers.csp", "CSP", csp, STATUS.WARN, "weak CSP (unsafe-inline/eval/wildcard)", csp, at));
  else out.push(mk("headers.csp", "CSP", csp, STATUS.PASS, "restrictive CSP", csp, at));

  // Clickjacking: XFO OR CSP frame-ancestors
  const xfo = get("x-frame-options");
  const hasFA = csp && /frame-ancestors/i.test(csp);
  if (xfo || hasFA) out.push(mk("headers.clickjacking", "Clickjacking protection", xfo || "frame-ancestors", STATUS.PASS, "XFO or frame-ancestors present", xfo || csp, at));
  else out.push(mk("headers.clickjacking", "Clickjacking protection", null, STATUS.FAIL, "no X-Frame-Options and no CSP frame-ancestors", "", at));

  // nosniff
  const nosniff = (get("x-content-type-options") || "").toLowerCase() === "nosniff";
  out.push(mk("headers.nosniff", "X-Content-Type-Options", nosniff ? "nosniff" : null, nosniff ? STATUS.PASS : STATUS.FAIL, nosniff ? "nosniff set" : "missing nosniff", get("x-content-type-options") || "", at));

  // Referrer-Policy
  const ref = get("referrer-policy");
  if (!ref) out.push(mk("headers.referrer", "Referrer-Policy", null, STATUS.WARN, "Referrer-Policy absent", "", at));
  else if (/unsafe-url/i.test(ref)) out.push(mk("headers.referrer", "Referrer-Policy", ref, STATUS.WARN, "unsafe-url leaks full URL", ref, at));
  else out.push(mk("headers.referrer", "Referrer-Policy", ref, STATUS.PASS, "safe referrer policy", ref, at));

  // Permissions-Policy
  const perm = get("permissions-policy");
  out.push(mk("headers.permissions", "Permissions-Policy", perm, perm ? STATUS.PASS : STATUS.WARN, perm ? "present" : "Permissions-Policy absent", perm || "", at));

  // Cross-origin isolation (informational)
  for (const [k, id, label] of [["cross-origin-opener-policy","headers.coop","COOP"],["cross-origin-embedder-policy","headers.coep","COEP"],["cross-origin-resource-policy","headers.corp","CORP"]]) {
    const v = get(k);
    out.push(mk(id, label, v, v ? STATUS.PASS : STATUS.WARN, v ? "present" : `${label} absent`, v || "", at));
  }

  // Cookies
  const sc = h["set-cookie"];
  if (sc) {
    const cookies = Array.isArray(sc) ? sc : [sc];
    const weak = cookies.filter((c) => !/;\s*secure/i.test(c) || !/;\s*httponly/i.test(c));
    if (weak.length) out.push(mk("headers.cookies", "Cookie flags", `${weak.length} weak`, STATUS.FAIL, "cookie without Secure/HttpOnly", weak[0].split(";")[0] + "; ...", at));
    else out.push(mk("headers.cookies", "Cookie flags", "all hardened", STATUS.PASS, "all cookies Secure+HttpOnly", "", at));
  }

  // Version leak
  const leak = get("x-powered-by") || (/(\d+\.\d+)/.test(get("server") || "") ? get("server") : null);
  if (leak) out.push(mk("headers.leak", "Version disclosure", leak, STATUS.WARN, "Server/X-Powered-By exposes version", leak, at));

  return out;
}

export async function collect(ctx) {
  if (!ctx.url) return [na({ id: "headers.all", category: CAT, metric: "HTTP headers", reason: "no url", collectedAt: ctx.collectedAt })];
  try {
    const res = await fetchTimeout(ctx.url, { method: "GET" }, 15000);
    const h = {};
    for (const [k, v] of res.headers.entries()) h[k.toLowerCase()] = v;
    const sc = res.headers.getSetCookie?.();
    if (sc?.length) h["set-cookie"] = sc;
    return parseHeaders(h, ctx);
  } catch (e) {
    return [na({ id: "headers.all", category: CAT, metric: "HTTP headers", reason: `fetch failed: ${e.message}`, collectedAt: ctx.collectedAt })];
  }
}
