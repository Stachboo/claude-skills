// scripts/report.mjs
const DOT = { green: "🟢", yellow: "🟡", red: "🔴", gray: "⚪" };
const ST = { PASS: "✅", WARN: "⚠️", FAIL: "❌", N_A: "▫️" };

const byId = (findings, id) => findings.find((f) => f.id === id);
const byCat = (findings, cat) => findings.filter((f) => f.category === cat);

// Markdown table cells: a stray pipe from a DOM snippet would silently shear the
// table into the wrong number of columns.
const td = (s) => String(s ?? "").replace(/\|/g, "\\|").replace(/\s*\n\s*/g, " ").trim();

// Spec §7.3: each cell = value + colour + SOURCE. Without the source, a PSI number
// and a local-Lighthouse number sit side by side looking comparable.
const cell = (f) => {
  if (!f) return "—";
  if (f.status === "N_A") return `N/A — ${f.reason}`;
  const v = `${f.value ?? ""}${f.unit ? " " + f.unit : ""} ${ST[f.status]}`;
  return f.source && f.source !== "N_A" ? `${v} · ${f.source}` : v;
};

const labSources = (findings, strategy) => new Set(
  findings
    .filter((x) => x.id.endsWith(`.lab.${strategy}`) && x.status !== "N_A" && x.source && x.source !== "N_A")
    .map((x) => x.source)
);

const FF_RE = /\.(mobile|desktop)$/;
const FF_ORDER = ["mobile", "desktop"];
const SEVERITY = { FAIL: 2, WARN: 1 };

// One Lighthouse audit failing on both form-factors is ONE problem. Listing it
// twice (which is what unnamespaced ids used to produce) reads as two.
function groupAudits(fails) {
  const groups = new Map();
  for (const x of fails) {
    const key = x.id.replace(FF_RE, "");
    const ff = x.id.match(FF_RE)?.[1] ?? null;
    const cur = groups.get(key);
    if (!cur) { groups.set(key, { ...x, formFactors: ff ? [ff] : [] }); continue; }
    if (ff && !cur.formFactors.includes(ff)) cur.formFactors.push(ff);
    if ((SEVERITY[x.status] ?? 0) > (SEVERITY[cur.status] ?? 0)) cur.status = x.status;
    if (!cur.evidence && x.evidence) cur.evidence = x.evidence;
    if (!cur.elements && x.elements) cur.elements = x.elements;
  }
  return [...groups.values()];
}

export function renderReport(audit) {
  const f = audit.findings;
  const t = audit.target;
  const L = [];
  L.push(`# Audit — ${t.name ?? t.url ?? "(no target)"}`);
  L.push("");
  L.push(`- **URL:** ${t.url ?? "N/A"}`);
  L.push(`- **Repo local:** ${t.localPath ?? "N/A — not provided"}`);
  L.push(`- **Quand:** ${audit.startedAt} → ${audit.finishedAt}`);
  L.push(`- **Outils:** node ${audit.tools.node}, chrome ${audit.tools.chrome ?? "—"}, lighthouse ${audit.tools.lighthouse ?? "—"}, PSI ${audit.tools.psi ?? "—"}`);
  L.push(`- **Légende:** field = données réelles (CrUX p75) · lab = mesure synthétique · ${ST.PASS}/${ST.WARN}/${ST.FAIL}/${ST.N_A}`);
  L.push("");
  const s = audit.scores;
  L.push(`## ${DOT[s.overall.color]} Score global : ${s.overall.value}/100`);
  L.push("");
  L.push(`| Perf | A11y | SEO | Best-Practices | Sécurité |`);
  L.push(`|---|---|---|---|---|`);
  L.push(`| ${DOT[s.performance.color]} ${s.performance.value ?? "N/A"} | ${DOT[s.accessibility.color]} ${s.accessibility.value ?? "N/A"} | ${DOT[s.seo.color]} ${s.seo.value ?? "N/A"} | ${DOT[s["best-practices"].color]} ${s["best-practices"].value ?? "N/A"} | ${DOT[s.security.color]} ${s.security.value ?? "N/A"} |`);
  L.push("");

  // Performance CWV
  L.push(`## Performance — Core Web Vitals`);
  L.push("");
  L.push(`| Métrique | Mobile field | Mobile lab | Desktop field | Desktop lab |`);
  L.push(`|---|---|---|---|---|`);
  for (const [key, label] of [["lcp","LCP"],["inp","INP"],["cls","CLS"],["tbt","TBT"],["ttfb","TTFB"]]) {
    L.push(`| ${label} | ${cell(byId(f, `perf.${key}.field.mobile`))} | ${cell(byId(f, `perf.${key}.lab.mobile`))} | ${cell(byId(f, `perf.${key}.field.desktop`))} | ${cell(byId(f, `perf.${key}.lab.desktop`))} |`);
  }
  L.push("");

  // a11y / seo / bp failed audits
  for (const [cat, title] of [["accessibility","Accessibilité"],["seo","SEO"],["best-practices","Best-Practices"]]) {
    const fails = byCat(f, cat).filter((x) => x.status === "FAIL" || x.status === "WARN");
    L.push(`## ${title}`);
    L.push("");
    if (!fails.length) { L.push(`_Aucun problème détecté._`); L.push(""); continue; }
    L.push(`| Statut | Critère | Form-factor | Éléments concernés | Détail |`);
    L.push(`|---|---|---|---|---|`);
    for (const x of groupAudits(fails)) {
      const ff = x.formFactors.length ? FF_ORDER.filter((s) => x.formFactors.includes(s)).join(", ") : "—";
      // evidence is the Lighthouse description ("how to fix"); fall back to reason
      // so a finding collected before evidence was captured still says something.
      const detail = td(x.evidence) || td(x.reason) || "—";
      L.push(`| ${ST[x.status]} | ${td(x.metric)} | ${ff} | ${td(x.elements) || "—"} | ${detail} |`);
    }
    L.push("");
  }

  // Security network
  L.push(`## Sécurité réseau`);
  L.push("");
  L.push(`| Statut | Contrôle | Valeur | Pourquoi |`);
  L.push(`|---|---|---|---|`);
  for (const x of [...byCat(f, "security.headers"), ...byCat(f, "security.tls")]) {
    L.push(`| ${ST[x.status]} | ${x.metric} | ${x.value ?? "—"}${x.unit ? " " + x.unit : ""} | ${x.reason} |`);
  }
  L.push("");

  // Security code
  L.push(`## Sécurité code (repo local)`);
  L.push("");
  const code = [...byCat(f, "security.deps"), ...byCat(f, "security.secrets")];
  if (!code.length) { L.push(`_N/A._`); }
  else {
    L.push(`| Statut | Élément | Valeur | Détail |`);
    L.push(`|---|---|---|---|`);
    for (const x of code) L.push(`| ${ST[x.status]} | ${x.metric} | ${x.value ?? "—"} | ${x.reason} |`);
  }
  L.push("");

  // perf-unavailable banner
  const perfNA = byCat(f, "performance").every((x) => x.status === "N_A");
  if (perfNA && byCat(f, "performance").length) {
    L.unshift(`> ⚠️ **Perf indisponible de toutes les sources** — ce rapport ne couvre pas la performance. Voir raisons en section Performance.\n`);
  }

  // Mixed-engine banner: PSI can fail on one form-factor and fall back to local
  // Lighthouse on the other. Two engines on two machines are not comparable, and
  // reading the columns side by side invents differences the site does not have.
  const mobileLab = labSources(f, "mobile");
  const desktopLab = labSources(f, "desktop");
  if (mobileLab.size && desktopLab.size && new Set([...mobileLab, ...desktopLab]).size > 1) {
    L.unshift(`> ⚠️ **Mesures lab issues de moteurs différents** — mobile: ${[...mobileLab].join(", ")} · desktop: ${[...desktopLab].join(", ")}. Les colonnes mobile et desktop ne sont pas comparables entre elles ; ne pas lire leur écart comme un fait sur le site.\n`);
  }
  return L.join("\n");
}
