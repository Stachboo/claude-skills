# Scoring reference
- CWV cutoffs (good / poor): LCP 2500/4000 ms · INP 200/500 ms · CLS 0.1/0.25 · TBT 200/600 ms · TTFB 800/1800 ms.
- Category score: good ≥90, needs-improvement ≥50, poor <50.
- Per-dimension penalty (non-Lighthouse): FAIL −25, WARN −8, floored at 0.
- `.summary` roll-up findings are excluded from the penalty (display-only) so a vuln counted by its `.cve.*` finding is not double-counted. Note: moderate/low deps vulns appear only in the summary and therefore do not affect the score — they are reported but not scored; only high/critical CVEs (which get individual `.cve.*` findings) penalize.
- A dimension whose findings are all N/A (or empty) → value `null`, color gray. It is excluded from the overall mean. Absence of data is never a green pass.
- Overall color: red if any assessed dimension red; else yellow if any yellow; else green.
- Overall value: weighted mean of assessed dimensions — security .35, performance .30, a11y .15, seo .10, best-practices .10.
