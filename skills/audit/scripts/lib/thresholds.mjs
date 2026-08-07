// scripts/lib/thresholds.mjs
// [good_max, poor_min] — value ≤ good_max => good; value > poor_min => poor; else ni
export const CWV = {
  lcp: [2500, 4000], inp: [200, 500], cls: [0.1, 0.25], tbt: [200, 600], ttfb: [800, 1800],
};

export function rateMetric(key, value) {
  const t = CWV[key];
  if (!t || typeof value !== "number") return null;
  const [good, poor] = t;
  if (value <= good) return "good";
  if (value > poor) return "poor";
  return "ni";
}

export function rateScore(score) {
  if (typeof score !== "number") return null;
  if (score >= 90) return "good";
  if (score >= 50) return "ni";
  return "poor";
}

export const RATING_TO_STATUS = { good: "PASS", ni: "WARN", poor: "FAIL" };
