---
name: domain-price
description: Recherche multi-sources de noms de domaine au meilleur prix (disponibilité + comparaison registrars). Utiliser dès que l'utilisateur parle d'acheter/chercher un nom de domaine, "prix domaine", "domaine dispo", "registrar le moins cher", "domain availability", "buy domain". Ne JAMAIS répondre avec un seul fournisseur.
---

# domain-price — comparateur multi-registrars

Règle d'or : **jamais un seul fournisseur**. Toujours croiser au minimum 3 sources vérifiées.

## Workflow

### 1. Baseline déterministe (script, aucune clé requise)

```bash
python "C:\Users\PC\.claude\skills\domain-price\scripts\check_domains.py" candidat1.com candidat2.fr candidat3.app
```

Donne pour chaque domaine : disponibilité **RDAP** (registre officiel, 404=libre / 200=pris),
prix **Porkbun** (USD, reg+renouvellement, ~900 TLDs) et **OVH** (EUR HT, promo 1ère année + prix standard).
Premier run OVH : télécharge ~30 Mo puis cache un extrait 7 jours.

### 2. Croiser avec Vercel (MCP déjà connecté)

Appeler `mcp__plugin_vercel_vercel__check_domain_availability_and_price` (max 10 domaines/appel).
Sert de 2e avis sur la dispo + prix Vercel (souvent proche du prix coûtant sur .com).

### 3. Promos 1ère année et comparateur complet (si besoin du prix plancher absolu)

`tld-list.com` compare ~50 registrars mais **bloque les fetchers HTTP (403 Cloudflare)** —
WebFetch et ddg-search échouent. Passer par le navigateur piloté (claude-in-chrome ou
Playwright MCP) : ouvrir `https://tld-list.com/tld/<tld>` et lire le tableau.
Registrars souvent en tête sur la 1ère année : Spaceship, Namecheap (promo), Porkbun, Cloudflare.

### 4. Conseil de restitution

- Séparer **prix 1ère année** (promo marketing) et **prix de renouvellement** (le vrai coût récurrent).
- Cloudflare Registrar vend à prix coûtant (gros + taxe ICANN ~0,18 $) mais sans promo 1ère année
  et nécessite un compte CF → stratégie classique : acheter la promo ailleurs, transférer chez
  Cloudflare/Porkbun pour renouveler pas cher. (Attendre 60 j avant transfert, règle ICANN.)
- Pour un .fr : OVH/Gandi/Bookmyname sont compétitifs et en EUR. Le .fr est **absent** de l'API
  pricing Porkbun (vérifié 2026-07-08) → pour ce TLD, s'appuyer sur OVH + tld-list via navigateur.
- Étiqueter tout prix non vérifié à l'instant T : les promos changent chaque semaine.

## Sources et leurs limites (vérifié 2026-07-08)

| Source | Accès | Couverture | Limite |
|---|---|---|---|
| RDAP (rdap.org) | HTTP libre | Tous TLDs à registre RDAP | Dispo seulement, pas de prix |
| Porkbun API | HTTP libre, sans clé | ~907 TLDs, USD | Un seul registrar |
| OVH catalogue public | HTTP libre, sans clé | ~942 TLDs, EUR HT | Renouvellement = approximation (create_std) |
| Vercel MCP | connecté (plugin vercel) | dispo + prix Vercel | 10 domaines max/appel, un seul vendeur |
| tld-list.com | navigateur uniquement (403 bots) | ~50 registrars comparés | Scraping manuel via Chrome piloté |
| Namecheap / Dynadot / Gandi API | clé requise (non configurée) | — | À configurer seulement si besoin récurrent |
