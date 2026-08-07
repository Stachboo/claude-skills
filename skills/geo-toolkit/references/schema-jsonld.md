# Snippets JSON-LD prêts à l'emploi

Règles : un @id unique par entité, JSON valide, pas de duplication entre pages, dateModified réel et maintenu.

## LocalBusiness (OBLIGATOIRE en local — sinon absent des AI Overviews)
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://DOMAINE/#business",
  "name": "NOM",
  "url": "https://DOMAINE/",
  "telephone": "+33XXXXXXXXX",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "RUE",
    "postalCode": "84000",
    "addressLocality": "Avignon",
    "addressCountry": "FR"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 0.0, "longitude": 0.0 },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "opens": "08:00", "closes": "19:00"
  }],
  "priceRange": "€€",
  "sameAs": ["URL_GOOGLE_BUSINESS", "URL_AVIS", "URL_RESEAU"],
  "areaServed": "VILLE et alentours"
}
```
Ne pas oublier une page politique de confidentialité liée (privacyPolicy attendu par les moteurs de réponse).

## FAQPage (acceptedAnswer : 40-150 mots, vraies questions clients)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://DOMAINE/PAGE#faq",
  "mainEntity": [{
    "@type": "Question",
    "name": "QUESTION CLIENT RÉELLE ?",
    "acceptedAnswer": { "@type": "Answer", "text": "Réponse directe de 40 à 150 mots, autonome, avec un chiffre sourcé si possible." }
  }]
}
```

## HowTo (chaque étape 80-120 mots, citable seule)
```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "@id": "https://DOMAINE/PAGE#howto",
  "name": "TITRE DU GUIDE",
  "totalTime": "PT30M",
  "estimatedCost": { "@type": "MonetaryAmount", "currency": "EUR", "value": "80" },
  "tool": [{ "@type": "HowToTool", "name": "OUTIL" }],
  "step": [{
    "@type": "HowToStep",
    "name": "Étape 1 — ACTION",
    "text": "80 à 120 mots, autonomes, réponse dans les premiers mots."
  }]
}
```
Dans le HTML, les étapes vont dans un `<ol>`.

## Article (fraîcheur = critère de citation)
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "https://DOMAINE/PAGE#article",
  "headline": "TITRE",
  "author": { "@type": "Person", "@id": "https://DOMAINE/auteur#person", "name": "AUTEUR", "url": "https://DOMAINE/auteur" },
  "datePublished": "2026-01-15",
  "dateModified": "2026-08-01",
  "publisher": { "@type": "Organization", "@id": "https://DOMAINE/#org", "name": "NOM" }
}
```
dateModified doit bouger réellement : viser < 13 semaines sur les pages stratégiques.

## llms.txt (à la racine)
```markdown
# NOM DU SITE
> Description en une phrase de ce que fait le site.

## Pages clés
- [Titre page pilier](https://DOMAINE/pilier) : résumé une ligne
- [Titre satellite](https://DOMAINE/satellite) : résumé une ligne

## Contact
- Zone : VILLE / région
- Téléphone : +33XXXXXXXXX
```
