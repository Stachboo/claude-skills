---
name: geo-toolkit
description: Boîte à outils complète SEO/GEO, backlinks, CTR, conversion et leads. Utiliser ce skill dès que l'utilisateur demande un audit de site, une analyse SEO ou GEO (citations IA), un suivi de backlinks ou de mentions de marque, une analyse CTR/Search Console, une optimisation de conversion, la génération de leads, un plan d'action web, ou mentionne un de ses sites dans un contexte de visibilité ou de performance. À utiliser même si le mot « audit » n'est pas prononcé — toute question du type « pourquoi mon site ne convertit pas / ne ranke pas / n'est pas cité par les IA » déclenche ce skill.
---

# GEO-Toolkit — SEO / GEO / CTR / Conversion / Leads

Outil d'audit et de pilotage pour un site (le vôtre ou celui d'un client).
Objectif : être **classé** (SEO), **cité** (GEO), **cliqué** (CTR), **convertir** (CRO) et **capter des leads** — mesuré et priorisé.

## Sources de données (par ordre de priorité)

1. **MCP Ahrefs** — backlinks, referring domains, organic keywords, Brand Radar (citations/mentions IA)
2. **MCP Semrush** — organic research, competitors, site audit, position tracking
3. **MCP Windsor.ai** — agrégateur Google Search Console + GA4 (CTR, positions, clics, conversions)
4. **bash + web_fetch** — crawl technique direct (TTFB, robots.txt, llms.txt, SSR, JSON-LD)

Toujours vérifier quelles données sont réellement disponibles avant de promettre un chiffre. Si un connecteur échoue (auth), le signaler et continuer avec les autres modules.

## Workflow

### 1. Intake
Demander (ou déduire du contexte) :
- **Cible** : URL/domaine (+ concurrents si comparaison)
- **Périmètre** : audit complet (5 modules) ou module ciblé
- **Contexte** : local ou national ? Site vitrine, SaaS, e-commerce ?

### 2. Exécution des modules
Chaque module a son fichier de référence. **Lire le fichier de référence AVANT d'exécuter le module.**

| Module | Fichier | Sources |
|---|---|---|
| A. Technique + GEO | `references/audit-technique.md` | bash, web_fetch |
| B. Backlinks + Mentions | `references/backlinks-mentions.md` | Ahrefs, Semrush |
| C. CTR / Search Console | `references/ctr-gsc.md` | Windsor.ai, Semrush |
| D. Conversion (CRO) | `references/conversion-leads.md` | web_fetch + règles Ogilvy/Kennedy |
| E. Leads | `references/conversion-leads.md` | web_fetch, analyse funnel |

Les règles GEO complètes (Gourdon + Mauhin 2026) sont dans `references/geo-rules.md` — les lire pour tout scoring GEO.
Les snippets JSON-LD prêts à l'emploi sont dans `references/schema-jsonld.md`.

### 3. Scoring
Chaque module rend un score **/100** avec le détail des points perdus. Barème dans chaque fichier de référence.
Score global = moyenne pondérée : Technique/GEO ×0,30 · Backlinks ×0,20 · CTR ×0,15 · Conversion ×0,20 · Leads ×0,15.

### 4. Rapport final
Structure obligatoire :
1. **Scores** (tableau : module, score, verdict)
2. **Quick wins** — impact fort, effort < 1 jour, triés par ratio impact/effort
3. **Chantiers** — impact fort, effort > 1 jour, avec estimation de délai de résultat (technique : 2-4 sem., citations IA : 8-12 sem.)
4. **Erreurs fatales détectées** (GPTBot bloqué, LocalBusiness absent en local, contenu thin, etc.)
5. **Prochaine mesure** — quoi re-mesurer et quand

Format : rapport markdown dans la conversation par défaut ; fichier .md ou dashboard HTML si demandé.

## Règles de rigueur

- Jamais de chiffre inventé : chaque métrique vient d'un appel outil réel, sinon écrire « non mesuré ».
- Toujours dater les mesures (les données GEO périment en 13 semaines).
- Ton : direct, sans complaisance — signaler ce qui est mauvais et pourquoi, proposer le correctif exact.
- En local (serrurier, VTC…) : le module GEO local est prioritaire (AI Overview ne cite que 3 sources).
