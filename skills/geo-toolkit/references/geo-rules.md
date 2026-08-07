# Règles GEO consolidées — Gourdon + Mauhin 2026

## Principe
Être CITÉ dans les réponses IA (ChatGPT, Perplexity, Gemini, AI Overviews), pas seulement classé.
Logique probabiliste. Chevauchement top 10 Google / citations IA : 17-38% en 2026 → deux logiques distinctes, le SEO reste la base.

**KPI cibles :**
- Taux de citation (TC) ≥ 30% sur les requêtes clés
- Part de réponse (PR) ≥ 40%
- Share of Model (SoM) suivi vs concurrents

## Les 5 piliers (Gourdon)

### 1. Technique
- Contenu 100% lisible sans JavaScript (SSR ou HTML statique)
- TTFB < 200 ms, page complète < 2 s
- Bots IA autorisés dans robots.txt : GPTBot, ClaudeBot, PerplexityBot, CCBot
- Zéro erreur 4xx/5xx sur les pages clés, sitemap à jour

### 2. Structure
- Tableaux comparatifs = probabilité d'extraction très élevée (dater les en-têtes)
- Hiérarchie H1→H3 stricte, listes
- Schema.org : Article, FAQPage, HowTo, Product, LocalBusiness

### 3. Cluster sémantique
- Page pilier 1500-2000 mots + 3-5 pages satellites liées
- L'IA décompose en sous-requêtes (query fan-out + RRF) : un cluster bat une page unique

### 4. Autorité
- Brand mentions sur sites tiers MÊME SANS LIEN = signal aussi fort qu'un backlink pour l'IA
- Avis tiers (Trustpilot, G2), pages auteur complètes, presse locale
- Reddit = 1ère source citée sur Perplexity en 2026

### 5. Chunking
- L'IA découpe en chunks de 200-500 mots → chaque paragraphe doit être AUTONOME (jamais « comme vu précédemment »)
- Pyramide inversée : réponse dans les 40-60 premiers mots
- Paragraphes 100-200 mots max
- Passage extractable idéal : 280-320 caractères

## Règles Mauhin 2026
- **llms.txt** à la racine (analogue robots.txt pour LLM)
- **Fraîcheur critique** : 50% du contenu cité a < 13 semaines → mettre à jour dateModified régulièrement (FAQ : tous les 6 mois minimum)
- **Statistiques chiffrées sourcées** = +30 à 65% de visibilité IA ; citer sources explicites (auteur, titre, date)
- **Résumé extractable ≤ 120 mots** en tête de chaque section
- **Local** : AI Overview cite max 3 sources sur requête locale → LocalBusiness JSON-LD complet OBLIGATOIRE (adresse, geo, horaires, priceRange, sameAs, privacyPolicy), sinon absent
- **HowTo** : étapes en `<ol>`, HowToStep de 80-120 mots chacune, totalTime/estimatedCost/tool — chaque étape citable individuellement
- **acceptedAnswer FAQ** : 40-150 mots, issues de vraies questions clients
- **Délais de résultat** : technique 2-4 semaines, citations 8-12 semaines

## Erreurs fatales (échec automatique du module GEO)
1. GPTBot ou autre bot IA bloqué dans robots.txt
2. JSON-LD dupliqué sans @id unique
3. Contenu thin < 800 mots sur pages clés
4. dateModified figé / jamais mis à jour
5. Zéro présence off-site (aucune mention tierce)

## Barème module GEO (/100)
- Technique (SSR, TTFB, bots, erreurs) : /25
- Structure (tableaux, Hn, Schema.org) : /20
- Clusters sémantiques : /15
- Autorité off-site : /20
- Chunking + fraîcheur + llms.txt : /20
Chaque erreur fatale : plafonne le score à 40.

## Suivi
- Ahrefs Brand Radar (MCP) : citations et mentions IA
- Test manuel hebdo des requêtes clés dans ChatGPT, Perplexity, Gemini
- Otterly.ai (49€/mois) si besoin d'automatisation supplémentaire
