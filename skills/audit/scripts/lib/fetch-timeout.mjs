// scripts/lib/fetch-timeout.mjs
export async function fetchTimeout(url, opts = {}, ms = 15000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try {
    return await fetch(url, { ...opts, signal: ctrl.signal, redirect: opts.redirect ?? "follow" });
  } finally {
    clearTimeout(t);
  }
}
