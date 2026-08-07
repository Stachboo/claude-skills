// scripts/lib/gate.mjs
// Colors that count as a gate failure, per policy level.
const LEVELS = { never: [], red: ["red"], yellow: ["red", "yellow"] };

// 0 ok · 1 the SITE failed the gate · 2 the TOOL crashed (thrown, see run.mjs)
// · 3 the TOOL produced an invalid artifact.
const MEANING = {
  1: "gate failed — a score breached the --fail-on level, or a dimension was unassessed under --require-complete",
  2: "fatal — the auditor itself crashed",
  3: "invalid artifact — audit.json failed schema validation; do not trust it",
};

export function explainExit(code) {
  return MEANING[code] ?? null;
}

const anyScore = (docs, pred) => docs.some((d) => Object.values(d.scores).some(pred));

export function decideExit({ docs, flags, invalid = false }) {
  const raw = flags["fail-on"] ?? (flags["json-only"] ? "red" : "never");
  const bad = LEVELS[raw];
  // A typo must never be read as a policy: silence here would turn a
  // misconfigured gate into a false pass.
  if (!bad) throw new Error(`--fail-on: expected one of ${Object.keys(LEVELS).join("|")}, got ${JSON.stringify(raw)}`);
  // A false artifact is the tool's fault and outranks any site verdict —
  // it must never be reported as a clean run, gate opted in or not.
  if (invalid) return 3;
  // Incompleteness is its own axis: a dimension whose probes all returned N/A
  // scores gray, which no color gate can see. "absence is not a pass" — but
  // --local-only grays dimensions on purpose, so this stays opt-in.
  if (flags["require-complete"] && anyScore(docs, (s) => s.color === "gray")) return 1;
  if (bad.length === 0) return 0;
  return anyScore(docs, (s) => bad.includes(s.color)) ? 1 : 0;
}
