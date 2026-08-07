# site-auditor
Standalone `/audit` skill: performance + accessibility + SEO + best-practices + security (headers, TLS, dep CVEs, secrets) for any URL or local repo. Zero npm dependencies — pure Node 24.

## Use
- In Claude Code: `/audit <url|name> [local-path] [flags]`
- Direct: `node scripts/run.mjs https://example.com`
- All configured sites: `node scripts/run.mjs --all`

## Output
`audit-report.md` (human) + `audit.json` (CI/fleet). Failed probes → `N/A + reason`, never fabricated.

## Flags
`--mobile-only` `--desktop-only` `--no-lab` `--runs N` `--live-only` `--local-only` `--all` `--json-only` `--fast` `--out <path>`
`--fail-on <never|red|yellow>` `--require-complete`

## Exit codes
Le gate est **opt-in** : par défaut l'outil sort `0` même sur un site rouge — le verdict est dans le rapport,
pas dans le code retour. Pour l'utiliser en CI, l'exiger explicitement.

| Code | Sens | Fautif |
|---|---|---|
| `0` | audit produit, gate satisfait | — |
| `1` | gate échoué (`--fail-on`, ou dimension non évaluée sous `--require-complete`) | le **site** |
| `2` | plantage de l'auditeur (inclut un `--fail-on` invalide) | l'**outil** |
| `3` | `audit.json` ne valide pas contre le schéma — ne pas s'y fier | l'**outil** |

- `--fail-on red` : échoue si une dimension est rouge · `yellow` : rouge **ou** jaune · `never` : jamais (défaut).
- `--json-only` implique `--fail-on red` (compat spec §138) ; un `--fail-on` explicite l'emporte.
- `--require-complete` : échoue si une dimension n'a **pas** été évaluée (toutes ses sondes en N/A → gris).
  Axe indépendant de la couleur, parce que « absence n'est pas un succès » — mais opt-in, car `--local-only`
  grise volontairement les dimensions réseau.
- Une valeur `--fail-on` inconnue **lève** au lieu de deviner : un typo ne doit pas se lire comme une politique.

## Install globally
`powershell -ExecutionPolicy Bypass -File deploy.ps1` (junctions this folder into `~/.claude/skills/audit`).

## Config
`cp audit.config.example.json audit.config.json` (le fichier réel est gitignoré : clé PSI + chemins machine),
puis renseigner `psiApiKey` et les entrées `nom → {url, localPath}`. Sans ce fichier, les URLs directes
fonctionnent quand même ; seules les cibles **par nom** et `--all` nécessitent la config.
Les seuils CWV et les cutoffs de couleur ne sont pas configurables en v0.1 (figés dans `scripts/lib/thresholds.mjs`).

## Tests
`npm test` (Node built-in test runner, zero deps). 73 tests across collectors, scoring, gate, reporter, and driver.

## Architecture
`SKILL.md` (thin) → `scripts/run.mjs` (driver) → 5 collectors → schema-validated `audit.json` → pure `scripts/report.mjs` → `audit-report.md`. See `docs/specs/` and `docs/plans/` for the full design.
