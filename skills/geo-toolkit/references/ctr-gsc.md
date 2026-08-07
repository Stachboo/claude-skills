# Module C — CTR / Search Console (Windsor.ai MCP)

Windsor.ai agrège Google Search Console + GA4. Charger via tool_search : `get_connectors`, `get_fields`, `get_data`.
Workflow : 1) `get_connectors` pour vérifier que GSC est relié au compte, 2) `get_fields` sur le connecteur google_search_console, 3) `get_data` avec les champs page/query/clicks/impressions/ctr/position sur 90 jours.

## Benchmarks CTR par position (desktop, référence 2026)
| Position | CTR attendu |
|---|---|
| 1 | ~28% |
| 2 | ~15% |
| 3 | ~10% |
| 4-5 | ~6% |
| 6-10 | ~2-4% |

## Détections automatiques

### 1. Pages « rankent mais ne cliquent pas »
Position ≤ 5 ET CTR < 50% du benchmark → problème de title/meta.
Correctif : réécrire title (chiffre + bénéfice + année, règles Ogilvy : promesse concrète, pas de superlatif creux) et meta description (réponse en 40-60 mots, appel à l'action).

### 2. Opportunités position 4-10
Impressions élevées + position 4-10 → une amélioration on-page (cluster + chunking selon geo-rules.md) peut faire gagner le top 3. Prioriser par impressions × (CTR_pos3 − CTR_actuel).

### 3. Cannibalisation
Deux pages sur la même requête avec positions instables → fusionner ou différencier les intentions.

### 4. Requêtes sans page dédiée
Requêtes à impressions fortes servies par une page générique → créer une page satellite du cluster.

## Barème (/100)
- CTR moyen pondéré vs benchmark : /40
- Volume d'opportunités position 4-10 traitées : /25
- Absence de cannibalisation : /15
- Couverture des requêtes (pages dédiées) : /20

## Sorties actionnables
Tableau : page | requête | position | impressions | CTR actuel | CTR attendu | clics perdus/mois | correctif proposé (title/meta réécrits inclus).
