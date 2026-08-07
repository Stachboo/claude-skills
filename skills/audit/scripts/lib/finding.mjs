// scripts/lib/finding.mjs
export const STATUS = { PASS: "PASS", WARN: "WARN", FAIL: "FAIL", N_A: "N_A" };

export function makeFinding(p) {
  const f = {
    id: p.id, category: p.category, metric: p.metric,
    value: p.value ?? null, unit: p.unit ?? "",
    status: p.status, reason: p.reason ?? "",
    evidence: p.evidence ?? "", source: p.source ?? "N_A",
    collectedAt: p.collectedAt,
  };
  // Optional 11th field: only Lighthouse audit findings know which DOM nodes
  // failed. Omitted entirely when the caller has nothing to say, so every other
  // finding keeps its exact 10-field shape in audit.json.
  if (p.elements !== undefined) f.elements = p.elements;
  return f;
}

export function na(p) {
  return makeFinding({
    id: p.id, category: p.category, metric: p.metric,
    value: null, unit: p.unit ?? "", status: STATUS.N_A,
    reason: p.reason, evidence: p.evidence ?? "", source: "N_A",
    collectedAt: p.collectedAt,
  });
}
