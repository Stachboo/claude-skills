// scripts/lib/score.mjs
import { rateScore } from "./thresholds.mjs";

const RATING_COLOR = { good: "green", ni: "yellow", poor: "red" };
const PENALTY = { FAIL: 25, WARN: 8 };
const DIM_WEIGHT = { security: 0.35, performance: 0.30, accessibility: 0.15, seo: 0.10, "best-practices": 0.10 };

const DIMS = ["performance", "accessibility", "seo", "best-practices", "security"];
function dimOf(cat) { return cat.startsWith("security.") ? "security" : cat; }
function colorOf(score) { const r = rateScore(score); return r ? RATING_COLOR[r] : "red"; }

export function computeScores(findings) {
  const byDim = Object.fromEntries(DIMS.map((d) => [d, []]));
  for (const f of findings) {
    const d = dimOf(f.category);
    if (byDim[d]) byDim[d].push(f);
  }

  const scores = {};
  for (const d of DIMS) {
    const fs = byDim[d];
    // No findings at all, or every finding is N/A → dimension not assessed.
    // Report it as null/"gray", NEVER as a green 100 (absence is not a pass).
    if (fs.length === 0 || fs.every((f) => f.status === "N_A")) { scores[d] = { value: null, color: "gray" }; continue; }
    // Lighthouse category-score findings have ids like "performance.score.mobile"
    // / ".desktop" (or a bare "<dim>.score"). Detect via ".score" substring and
    // average across form-factors. If present, the category score already accounts
    // for individual audit failures, so we trust it over the penalty model.
    const scoreFindings = fs.filter((f) => /\.score(\.|$)/.test(f.id) && typeof f.value === "number");
    let value;
    if (scoreFindings.length) {
      value = Math.round(scoreFindings.reduce((s, f) => s + f.value, 0) / scoreFindings.length);
    } else {
      // Exclude ".summary" roll-up findings from the penalty: they restate the
      // same vulns already counted by their individual ".cve.*" findings, so
      // penalizing both double-counts a single issue.
      const penalty = fs
        .filter((f) => !f.id.endsWith(".summary"))
        .reduce((sum, f) => sum + (PENALTY[f.status] || 0), 0);
      value = Math.max(0, 100 - penalty);
    }
    scores[d] = { value, color: colorOf(value) };
  }

  // overall — only assessed (non-null) dimensions count
  const present = DIMS.filter((d) => scores[d].value !== null);
  const totalW = present.reduce((s, d) => s + DIM_WEIGHT[d], 0) || 1;
  const mean = present.reduce((s, d) => s + scores[d].value * DIM_WEIGHT[d], 0) / totalW;
  let color = "green";
  if (present.some((d) => scores[d].color === "red")) color = "red";
  else if (present.some((d) => scores[d].color === "yellow")) color = "yellow";
  scores.overall = { value: Math.round(mean), color };
  return scores;
}
