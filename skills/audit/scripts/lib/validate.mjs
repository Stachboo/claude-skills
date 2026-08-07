// scripts/lib/validate.mjs
const FINDING_FIELDS = ["id","category","metric","value","unit","status","reason","evidence","source","collectedAt"];
const STATUS = new Set(["PASS","WARN","FAIL","N_A"]);

export function validateFinding(f) {
  const errors = [];
  if (typeof f !== "object" || f === null) return { ok: false, errors: ["finding is not an object"] };
  for (const k of FINDING_FIELDS) if (!(k in f)) errors.push(`missing field: ${k}`);
  if ("status" in f && !STATUS.has(f.status)) errors.push(`invalid status: ${f.status}`);
  if ("value" in f && !["number","string"].includes(typeof f.value) && f.value !== null)
    errors.push("value must be number|string|null");
  // "elements" is optional (audit findings only) but must be a string when present.
  for (const k of ["id","category","metric","unit","reason","evidence","source","collectedAt","elements"])
    if (k in f && typeof f[k] !== "string") errors.push(`${k} must be a string`);
  return { ok: errors.length === 0, errors };
}

export function validateAudit(doc) {
  const errors = [];
  if (typeof doc !== "object" || doc === null) return { ok: false, errors: ["audit doc is not an object"] };
  if (doc.schemaVersion !== 1) errors.push("schemaVersion must be 1");
  for (const k of ["target","startedAt","finishedAt","tools","findings","scores"])
    if (!(k in doc)) errors.push(`missing field: ${k}`);
  if (!Array.isArray(doc.findings)) errors.push("findings must be an array");
  else doc.findings.forEach((f, i) => {
    const r = validateFinding(f);
    if (!r.ok) errors.push(`findings[${i}]: ${r.errors.join("; ")}`);
  });
  return { ok: errors.length === 0, errors };
}
