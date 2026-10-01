# Typographie française — règles complètes

Source de référence : *Lexique des règles typographiques en usage à l'Imprimerie
nationale*. Les usages belge, suisse et québécois divergent sur quelques points ; ils
sont signalés le cas échéant.

## Les espaces

Le français distingue trois espaces là où l'anglais n'en a qu'une. C'est la source
première des fautes dans un texte produit par un modèle.

| Nom | Unicode | Entité HTML | Emploi |
|---|---|---|---|
| Espace fine insécable | U+202F | `&#8239;` | avant `;` `!` `?` |
| Espace insécable | U+00A0 | `&nbsp;` | avant `:`, dans les guillemets, dans les nombres, avant `%` et les unités |
| Espace ordinaire | U+0020 | — | partout ailleurs |

**Règle des ponctuations doubles.** Les signes composés de deux éléments (`;` `!` `?`
`:`) prennent une espace avant. Les signes simples (`.` `,`) n'en prennent pas.
Mnémotechnique fiable : deux signes, deux espaces ; un signe, une espace.

**Cas des deux-points.** L'usage français retient l'espace insécable ordinaire, non la
fine. L'espace fine progresse mais n'est pas la norme établie.

**Une seule espace, jamais deux.** L'insécable remplace l'espace ordinaire, elle ne
s'y ajoute pas. Une espace ordinaire collée à une insécable (`Étape 1` + espace +
U+00A0 + `:`) ne se voit pas à l'écran mais casse la ligne au mauvais endroit.
Le vérificateur la signale (`TYPO-11`). C'est le défaut que `corriger.py` produisait
après un chiffre avant le 2026-10-01 : sur 898 fichiers réels, 400 occurrences.

**Nombres.** Séparateur de milliers : espace insécable, jamais de virgule.
`15 000 €`, jamais `15,000 €` ni `15000€`. L'unité et le symbole monétaire sont
précédés d'une insécable.

**Pourcentage.** `12 %` avec insécable. Jamais `12%`.

**Abréviations et références.** L'insécable évite les coupures absurdes en fin de
ligne : `art. L. 3120-2`, `p. 47`, `n° 12`, `M. Dupont`, `XIX<sup>e</sup> siècle`.

## Les guillemets

Les guillemets français sont les chevrons doubles `«` `»`. Les guillemets droits
`"` sont une survivance de la machine à écrire.

À l'intérieur, une **espace insécable** suit le chevron ouvrant et précède le chevron
fermant : `« citation »`.

Citation dans une citation : chevrons pour le premier niveau, guillemets anglais
doubles pour le second. `« Il a dit “oui” hier. »`

Ponctuation finale : si la citation est une phrase complète, le point reste à
l'intérieur. Sinon il sort.

## L'apostrophe

L'apostrophe typographique est `’` (U+2019), courbe. L'apostrophe droite `'` (U+0027)
est un caractère de programmation.

Elle ne prend aucune espace : `l’article`, `aujourd’hui`, `qu’il`.

## Les points de suspension

Un seul caractère : `…` (U+2026). Jamais trois points successifs.

Ils ne se cumulent pas avec un point final. Après `etc.`, on ne met pas de points de
suspension.

## Les tirets

Trois caractères distincts, trois usages.

| Signe | Unicode | Usage |
|---|---|---|
| Trait d'union `-` | U+002D | mots composés : `arc-en-ciel` |
| Tiret demi-cadratin `–` | U+2013 | intervalles : `p. 12–18` |
| Tiret cadratin `—` | U+2014 | incise, dialogue |

Le tiret cadratin n'est pas un signe de respiration dramatique. Cet emploi vient de
l'anglais et signale un texte machine quand il se répète. En français, l'incise se
marque plus souvent par des virgules ou des parenthèses.

## Les parenthèses et crochets

Pas d'espace à l'intérieur : `(ainsi)`, jamais `( ainsi )`. Une espace ordinaire à
l'extérieur, avant l'ouvrante et après la fermante.

Les crochets signalent une intervention dans une citation : `[…]` pour une coupure,
`[sic]`, `[souligné par nous]`.

## Les capitales

Les capitales s'accentuent : `À`, `É`, `Ê`, `Ç`. L'usage contraire vient des
limitations des anciennes machines. `État`, jamais `Etat`.

Les titres et intitulés ne prennent pas de capitale à chaque mot. C'est un usage
anglais. `Note de cadrage juridique`, non `Note De Cadrage Juridique`.

## Les nombres et dates

Les nombres de zéro à seize s'écrivent en toutes lettres dans un texte suivi, au-delà
en chiffres. Les nombres qui portent une donnée (montants, mesures, articles) restent
en chiffres quelle que soit leur valeur.

Dates : `28 juillet 2026`, sans virgule, mois en minuscule.

Heures : `14 h 30`, avec insécables, non `14:30` ni `14h30`.

## Les sigles

Sans points ni espaces : `SNCF`, `RGPD`, `VTC`. Au premier emploi, développer :
`véhicule de transport avec chauffeur (VTC)`.

## Ce qui ne se vérifie pas mécaniquement

Le vérificateur détecte l'absence d'insécable, pas son emploi abusif. Il ne distingue
pas un tiret cadratin légitime d'un tiret décoratif. Il ne peut pas juger si une
capitale est justifiée par un nom propre.

Ces points restent à la charge du rédacteur.
