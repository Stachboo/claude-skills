# Module B — Backlinks + Mentions (Ahrefs / Semrush MCP)

Charger les outils via tool_search avant tout appel (les MCP sont différés). Toujours dater les extractions.

## 1. Profil de liens (Ahrefs)
Outils : `site-explorer-domain-rating`, `site-explorer-backlinks-stats`, `site-explorer-referring-domains`, `site-explorer-broken-backlinks`, `site-explorer-anchors`.
Relever :
- DR + évolution (domain-rating-history)
- Nombre de referring domains + tendance (refdomains-history)
- Backlinks cassés (= quick wins de récupération : rediriger ou contacter)
- Répartition des ancres (sur-optimisation = risque)

## 2. Mentions IA (Ahrefs Brand Radar)
Outils : `brand-radar-mentions-overview`, `brand-radar-citations-overview-entities`, `brand-radar-sov-overview`, `brand-radar-cited-pages`, `brand-radar-ai-responses`.
Relever :
- Mentions et citations de la marque dans les réponses IA
- Share of Voice vs concurrents
- Quelles pages sont citées (à renforcer) et lesquelles jamais (à retravailler selon geo-rules.md)
- Domaines tiers cités sur les requêtes cibles → cibles de brand mentions (rappel : mention sans lien = signal fort pour l'IA)

## 3. Comparaison concurrents (Semrush)
Outils : `backlinks_research`, `competitors_research`, `organic_research`.
- Gap de referring domains vs top 3 concurrents
- Sources de liens des concurrents absentes de notre profil = liste de prospection

## 4. Off-site GEO
Vérifier manuellement (web_search) : présence sur Reddit (1ère source Perplexity 2026), avis Trustpilot/G2/Google Business, presse locale. Zéro présence off-site = **erreur fatale GEO**.

## Barème (/100)
- DR et tendance : /20
- Referring domains vs concurrents : /25
- Backlinks cassés traités : /10
- Mentions/citations IA (Brand Radar) : /25
- Présence off-site (Reddit, avis, presse) : /20

## Sorties actionnables
1. Liste de 10 cibles de liens/mentions priorisées (source, angle de contact)
2. Backlinks cassés à récupérer (URL, action)
3. Pages jamais citées par l'IA + correctif chunking/structure à appliquer
