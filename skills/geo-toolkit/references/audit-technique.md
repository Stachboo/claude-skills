# Module A — Audit technique + GEO (bash + web_fetch)

Exécuter dans l'ordre. Noter chaque résultat avec sa date. Barème en fin de fichier.

## 1. TTFB et temps de chargement
```bash
curl -o /dev/null -s -w "DNS: %{time_namelookup}s | TTFB: %{time_starttransfer}s | Total: %{time_total}s | Code: %{http_code}\n" -L https://DOMAINE/
```
Répéter 3 fois, garder la médiane. Cible : TTFB < 0,2 s, total < 2 s.

## 2. Bots IA dans robots.txt
```bash
curl -s https://DOMAINE/robots.txt
```
Vérifier qu'AUCUNE de ces lignes ne bloque : GPTBot, ClaudeBot, Claude-Web, PerplexityBot, CCBot, Google-Extended, Bytespider.
Un `Disallow: /` sous un de ces User-agent = **erreur fatale**.

## 3. llms.txt
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://DOMAINE/llms.txt
```
200 = présent. 404 = à créer (quick win : résumé du site + liens vers pages clés en markdown).

## 4. Lisibilité sans JavaScript (test SSR)
```bash
curl -s -A "GPTBot" https://DOMAINE/PAGE-CLE | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', html, flags=re.S)
words = len(text.split())
print(f'Mots visibles sans JS : {words}')
print('VERDICT :', 'OK (SSR/statique)' if words > 300 else 'ÉCHEC — contenu invisible pour les bots IA')
"
```
Comparer avec le contenu réel de la page (web_fetch). Si le curl brut est vide mais la page riche → rendu client only = **échec pilier technique**.

## 5. Sitemap et erreurs
```bash
curl -s https://DOMAINE/sitemap.xml | grep -c "<loc>"
```
Puis tester le code HTTP des 10 URLs principales (boucle curl -w "%{http_code}"). Toute 4xx/5xx sur page clé = points perdus.

## 6. JSON-LD
```bash
curl -s https://DOMAINE/PAGE | python3 -c "
import sys, re, json
html = sys.stdin.read()
blocks = re.findall(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', html, flags=re.S)
print(f'{len(blocks)} bloc(s) JSON-LD')
for b in blocks:
    try:
        d = json.loads(b)
        items = d if isinstance(d, list) else [d]
        for i in items:
            print('-', i.get('@type'), '| @id:', i.get('@id', 'ABSENT'))
    except Exception as e:
        print('JSON INVALIDE :', e)
"
```
Vérifier : types attendus présents (LocalBusiness en local !), @id uniques, JSON valide.

## 7. Structure et chunking (via web_fetch)

> **Statut épistémique de ces critères, à lire avant de noter.**
> Vérifié le 2026-08-04 contre
> `_bibliotheque-perso/referentiels/2026-08-01-dossier-recherche-seo-geo-cro.md`.
> **Deux critères seulement se déduisent d'un mécanisme documenté.** Les autres sont
> des conventions de rédaction. Ne jamais les présenter à un client comme des seuils
> établis, et signaler leur statut dans le rapport.

| Critère | Statut | Fondement |
|---|---|---|
| Paragraphes ≤ 200 mots, **autonomes** | `[DÉDUIT]` | Le chunking RAG découpe en blocs de 200 à 500 mots : l'unité de sélection est le chunk, pas la page |
| Un cluster de pages bat la page unique | `[DÉDUIT]` | Le query fan-out décompose la requête en sous-requêtes |
| Réponse dans les 40-60 premiers mots | `[PRATIQUE]` | Cohérent avec le mécanisme, jamais mesuré |
| Résumé ≤ 120 mots en tête de section | `[PRATIQUE]` | Convention |
| Tableau ou liste extractable | `[PRATIQUE]` | Plausible, non mesuré |
| `dateModified` < 13 semaines | `[NON VÉRIFIÉ]` | Adossé au chiffre « 50 % du contenu cité a moins de 13 semaines », source primaire non retrouvée |
| Contenu ≥ 800 mots | `[CONVENTION]` | **Aucun seuil de longueur n'est un facteur de classement.** Garde-fou anti-thin content, pas une cible |

Sur les 3 pages clés, vérifier :
- H1 unique, hiérarchie H1→H3 sans saut
- Réponse dans les 40-60 premiers mots de chaque section
- Paragraphes ≤ 200 mots, autonomes
- Résumé ≤ 120 mots en tête de section
- Au moins un tableau ou une liste extractable
- dateModified récent (< 13 semaines)
- Contenu ≥ 800 mots sur les pages piliers

## Barème (/100)
- TTFB/vitesse : /15 (TTFB<0,2s=15 ; <0,5s=8 ; sinon 0)
- Bots IA autorisés : /15 (fatale si bloqués)
- llms.txt : /5
- SSR/lisibilité sans JS : /20 (fatale si contenu invisible)
- Sitemap + zéro 4xx/5xx : /10
- JSON-LD valide et complet : /15
- Structure/chunking/fraîcheur : /20 — **ce sous-score repose aux deux tiers sur des
  conventions non mesurées (tableau du §7). L'annoncer comme indicatif, jamais comme
  une mesure.**
