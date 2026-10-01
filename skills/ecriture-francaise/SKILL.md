---
name: ecriture-francaise
description: Use when writing or editing ANY French text — documents, files, or replies. Enforces French typography (espaces insécables, guillemets, ponctuation) and removes the lexical, syntactic and rhythmic markers of machine-generated French. Triggers on any French output.
---

# Écriture française

Un texte français produit par un modèle porte deux défauts qu'un lecteur francophone
repère immédiatement : une typographie anglo-saxonne, et des tournures calquées de
l'anglais. Ce skill traite les deux.

## Le principe : en français, le marqueur dominant est le calque

Les listes de marqueurs publiées pour l'anglais ne se traduisent pas. Le tell français
n'est pas le même mot, c'est la **trace de l'anglais sous le français** : ponctuation
anglo-saxonne, vocabulaire décalqué, constructions importées.

C'est observable. Sur une note juridique de 47 paragraphes rédigée sans ce skill, le
défaut le plus systématique était **onze virgules avant « et »** — la virgule sérielle
anglaise, qui n'existe pas en français — devant zéro espace insécable correcte sur
quinze paires de guillemets. Le rédacteur pensait en anglais et rendait en français.

Corollaire pratique : **chercher d'abord l'anglais dans le texte**, avant de chercher
du vocabulaire pompeux.

## Statut des règles

Deux niveaux, à ne jamais confondre.

**Règles dures.** Mécaniquement vérifiables, sans jugement. Une occurrence est une
faute. Le vérificateur les fait échouer.

**Recommandations.** Elles demandent un jugement. Le vérificateur les signale, il ne
bloque pas. Le rédacteur tranche.

Toute règle porte sa source, ou elle n'entre pas ici.

## Règles dures — typographie

Référence : *Lexique des règles typographiques en usage à l'Imprimerie nationale*.

| Règle | Correct | Fautif |
|---|---|---|
| Espace fine insécable avant `;` `!` `?` | `Vraiment ?` (U+202F) | `Vraiment?` · `Vraiment ?` |
| Espace insécable avant `:` | `Voici :` (U+00A0) | `Voici:` · `Voici :` |
| Guillemets français avec insécables | `« mot »` (U+00A0 à l'intérieur) | `"mot"` · `« mot »` |
| Apostrophe typographique | `l’article` | `l'article` |
| Points de suspension | `…` | `...` |
| Pas d'espace avant `.` `,` | `mot, mot.` | `mot , mot .` |
| Pas d'espace après `(` ni avant `)` | `(ainsi)` | `( ainsi )` |
| Espace insécable dans les nombres | `15 000 €` | `15000€` |
| Une seule espace, jamais deux | `Étape 1 :` (U+00A0 seule) | espace ordinaire + U+00A0 |

Détail complet et cas limites : `references/typographie.md`.

## Règles dures — anglicismes de ponctuation

**Jamais de virgule avant `et` ou `ou` dans une énumération.** La virgule sérielle est
anglaise. En français : *le permis, la carte et l'assurance*. Jamais *le permis, la
carte, et l'assurance*.

**Le tiret cadratin n'est pas une respiration.** En français il sert à l'incise et au
dialogue, pas à créer du suspense. Plus d'un pour mille mots signale un texte machine.
Remplacer par une virgule, un point-virgule, une parenthèse, ou un point.

**Le gras n'est pas un surligneur.** Il marque un terme défini ou une règle opératoire.
Du gras au milieu d'une phrase pour « appuyer » est un marqueur.

## Règles dures — constructions

**L'antithèse.** *Ce n'est pas X, c'est Y.* / *Non pas X mais Y.* / *X et non Y.*
La construction la plus signalée dans toutes les listes publiées, anglaises comme
francophones. Elle sonne profonde et n'engage à rien. Dire ce que la chose est.

**Le titre-accroche.** Un intitulé doit annoncer le contenu de la section, pas le
teaser. *« Le coût caché de la commodité »* devient *« Ce que coûte l'abonnement »*.
Cas particulier à proscrire : le titre en antithèse, *« Ce que X démontre, et ce qu'il
ne démontre pas »*.

**Le méta-commentaire.** Le texte ne se commente pas lui-même. Supprimer *il convient
de noter que*, *ce point mérite d'être souligné*, *il s'agit là du point le plus
important*. Si c'est important, écrire l'idée, pas son étiquette.

**L'annonce du dénombrement.** *Trois raisons expliquent cela : …* Numéroter ou
exposer, sans annoncer le total.

Liste complète des marqueurs, calques et ouvertures : `references/marqueurs-ia.md`.

## Recommandations — rythme

Le défaut structurel le plus difficile à corriger n'est pas lexical. C'est la
**régularité**. Un texte machine produit des phrases de longueur voisine, et des
paragraphes de nombre de phrases voisin. Un rédacteur humain alterne : une phrase
brève qui assène, puis une longue qui nuance.

La mesure est le **coefficient de variation** de la longueur des phrases, soit
l'écart-type divisé par la moyenne.

| CV mesuré | Lecture |
|---|---|
| < 0,40 | Rythme plat. Signal fort. |
| 0,40 – 0,55 | Acceptable sans être vivant. |
| > 0,55 | Rythme humain. |

Ces seuils sont **provisoires**. Ils viennent d'un échantillon restreint et doivent
être recalibrés sur un corpus de textes français authentiques du même genre. La
méthode de calibration est décrite dans `references/mesures.md`. Tant qu'ils ne sont
pas recalibrés, ce sont des indications, pas des règles.

Correction : ne pas rallonger au hasard. Trouver la phrase qui porte la conclusion et
la raccourcir jusqu'à l'os.

## Recommandations — densité

Une affirmation vérifiable vaut mieux que trois adjectifs. Préférer un chiffre, une
date, un nom, une référence. Si une phrase ne peut pas être rendue plus précise, elle
est probablement du remplissage et se supprime.

Rien ne doit pouvoir être retiré sans perte. C'est le seul test de concision qui vaille.

## Procédure

**Avant d'écrire.** Identifier le genre et le destinataire. Une note juridique, un
courriel et une page de vente n'ont pas le même registre. Le registre se choisit, il
ne se subit pas.

**Après avoir écrit, avant de livrer.** Lancer le vérificateur :

```
python scripts/verifier.py <fichier>
```

Il accepte `.html`, `.md` et le texte brut. Il ignore le code, les feuilles de style et
les blocs préformatés. Il rend un code de sortie non nul si une règle dure est violée,
ce qui permet de l'utiliser en hook ou en intégration continue.

**Traiter les signalements dans cet ordre :** typographie d'abord, puisqu'elle est
objective. Anglicismes ensuite. Constructions après. Rythme en dernier, parce que c'est
le seul point qui demande de réécrire plutôt que de corriger.

**Ne pas livrer avant que les règles dures soient à zéro.**

## Ce que ce skill ne fait pas

Il ne vérifie ni l'orthographe ni la grammaire. Pour cela, utiliser un correcteur dédié
au français : Grammalecte, LanguageTool.

Il ne rend pas un texte indétectable. Les détecteurs d'IA affichent entre 12 et 26 % de
faux positifs sur des textes humains, et davantage hors de l'anglais. Le but ici n'est
pas de tromper un outil, c'est d'écrire correctement le français.

Il ne remplace pas la lecture. Un texte conforme à toutes ces règles peut rester
mauvais.

## Références

- `references/typographie.md` — règles typographiques complètes, cas limites, codes Unicode.
- `references/marqueurs-ia.md` — calques, vocabulaire, ouvertures, constructions.
- `references/mesures.md` — les mesures, leur calcul, la méthode de calibration.
- `scripts/verifier.py` — le vérificateur.
