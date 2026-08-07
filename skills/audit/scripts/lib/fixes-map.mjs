// scripts/lib/fixes-map.mjs
export function inferHeaderTarget(files) {
  const set = new Set(files);
  if (set.has("vercel.json")) return "vercel.json (headers[])";
  if (set.has("netlify.toml")) return "netlify.toml ([[headers]])";
  if ([...set].some((f) => f.startsWith("astro.config"))) return "astro.config.mjs / public/_headers";
  if ([...set].some((f) => f.startsWith("next.config"))) return "next.config.js (headers())";
  if ([...set].some((f) => f.startsWith("nuxt.config"))) return "nuxt.config.ts (routeRules)";
  return "public/_headers or server config";
}
