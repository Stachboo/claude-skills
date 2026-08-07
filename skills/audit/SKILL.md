---
name: audit
description: Audit any URL (and optionally its local repo) for performance, accessibility, SEO, best-practices, and security (HTTP headers, TLS, dependency CVEs, exposed secrets). Produces audit-report.md + audit.json. Triggers: "audit", "audit du site", "perf et sécurité", "/audit <url>".
---

# /audit — Web performance & security auditor

## What this does
Runs `scripts/run.mjs` which fans out 5 collectors (lighthouse, headers, tls, deps, secrets), merges schema-validated findings into `audit.json`, and renders `audit-report.md`. **You (the model) never invent a number** — every metric comes from a collector; failed probes are `N/A` with a reason.

## Invocation
```
node scripts/run.mjs <url|name> [local-path] [flags]
```
- `<url|name>`: a full `https://…` URL, or a key from `audit.config.json`.
- `[local-path]`: repo dir for deps+secrets (optional; omitted ⇒ those render N/A).
- Flags: `--mobile-only` `--desktop-only` `--no-lab` `--runs N` `--live-only` `--local-only` `--all` `--json-only` `--fast` `--out <path>` `--fail-on <never|red|yellow>` `--require-complete`.
- Exit codes: `0` ok · `1` gate échoué (le site) · `2` plantage de l'auditeur · `3` `audit.json` invalide (ne pas s'y fier). Le gate est opt-in : sans `--fail-on`/`--json-only`, un site rouge sort quand même `0` — le verdict se lit dans le rapport, pas dans le code retour.

## Steps for the model
1. Resolve the target. If the user gave a name, confirm it exists in `audit.config.json`; if they gave a URL with no local path and a matching project exists, offer to add the local path.
2. Run the command via Bash (from the skill dir). Stream stderr to the user.
3. Read the generated `audit-report.md`.
4. **Author the "Top fixes" section** (the ONLY place you add analysis): read `reference/fixes-map.md` + `reference/scoring.md`, pick the highest risk×ease FAIL findings, and for each give the concrete target file (glob the local repo to confirm: `vercel.json` / `_headers` / `astro.config` / `next.config` / `pnpm up`) with a paste-ready snippet. Mark this section `> LLM-advice`.
5. Present the report. Never edit the measured tables.

## Hard rules
- Do not fabricate metrics. If a table cell says `N/A`, report it as N/A with its reason.
- Do not run `cso`/`ln-*` skills as subprocesses (interactive-hang risk) — this skill is self-contained.
- Heavy installs are forbidden; the only on-disk add is `npx lighthouse` (cached, ~tens of MB), gated on Chrome present.

## Setup (first run)
- If `audit.config.json` is absent (fresh deploy), copy `audit.config.example.json` to `audit.config.json`. Without it, full `https://…` URLs still work; only named targets and `--all` need the config.
- Optional but recommended: get a free PageSpeed Insights API key (https://developers.google.com/speed/docs/insights/v5/get-started) and put it in `audit.config.json` `psiApiKey` or env `AUDIT_PSI_KEY`. Without it, perf uses local Lighthouse (Chrome required).
