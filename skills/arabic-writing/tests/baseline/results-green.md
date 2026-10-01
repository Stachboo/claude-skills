# Baseline GREEN — ce que les mêmes scénarios donnent AVEC le skill

**Date :** 2026-09-17 · **Statut : [mesuré]** · Contrepartie de `results-red.md`.
Mêmes scénarios, sous-agents neufs, skill présent à
la racine du skill (`arabic-writing/`), consigne ajoutée :
« lis d'abord son `SKILL.md` et suis-le ».

---

## Réserve de méthode, à lire avant les chiffres

Ces agents disposent d'outils et **lisent le skill en entier** — `SKILL.md`, les
références, l'asset de règles, et pour certains les sources d'origine. Un agent
qui reçoit le skill comme simple contexte injecté, sans pouvoir ouvrir
`references/`, n'obtiendra pas cela.

**Ces résultats sont donc une borne haute, pas le cas moyen.** Ils mesurent ce que
le skill rend possible, non ce qu'il garantit.

Comme en RED, les agents héritent aussi du `CLAUDE.md` de l'utilisateur, qui porte
une méthode de vérification mais rien sur l'arabe. Le delta RED→GREEN est donc
imputable au skill, les deux côtés partageant ce socle.

---

## Le tableau, défaut par défaut

| défaut mesuré en RED | RED | GREEN | fermé ? |
|---|---|---|---|
| **S5** — sur-vocalisation des noms propres | 770 ‰ | **0 ‰** | oui |
| **S4** — sur-vocalisation de la prose autour d'une citation | 807 ‰ | **34 ‰** | oui |

| **S1** — auditoire jamais déclaré, phrases hors plafond | 24 mots (plafond 15) | **9 mots**, auditoire déclaré | oui |
| **S3** — règle inventée sur le tiret | 1 invention | **0**, et réfutée explicitement | oui |
| **S3** — observations sans source | **0 / 15** | **10 / 10 étiquetées** | oui |

Les chiffres de vocalisation sont en diacritiques pour mille lettres arabes,
**citations retirées des deux côtés à l'identique**.

> **Ne pas confondre avec le tableau de `results-red.md`**, qui donne 784 ‰ pour
> S4 et 770 ‰ pour S5. Ces valeurs-là portent sur le **texte entier, citations
> comprises** ; les 807 ‰ ci-dessus portent sur la **prose seule**. Sur S4 la
> prose est plus vocalisée que les citations qu'elle encadre, d'où 807 > 784.
> Les deux colonnes du tableau ci-dessus sont mesurées de la même façon, ce qui
> est la seule chose que la comparaison exige.
 Sur S4, le texte entier
GREEN est à 218 ‰ et sa prose seule à 34 ‰ : l'écart est la démonstration que
retirer les citations n'est pas un ajustement de confort mais une condition pour
que le nombre veuille dire quelque chose.

---

## S3, le test décisif

C'est le scénario qui, sans le skill, avait produit une bonne relecture **et**
une règle fausse énoncée avec aplomb : « le tiret d'incise est un import
anglais/français ; l'arabe standard emploie des parenthèses ou des virgules. »
Quinze observations, zéro source.

### L'invention a disparu, et elle est activement réfutée

Le rapport GREEN porte une section « **Things that look wrong and are not — do
not flag** » dont la première entrée est le tiret, avec sa chaîne : Zakī 1912,
confirmé par Hārūn, exemplifié verbatim dans le guide de la Banque mondiale. Et
la note : « An agent without this skill called exactly this an English/French
import; it is false. »

Le skill ne s'est pas contenté de ne pas produire l'erreur : il a armé l'agent
pour la nommer.

### Les dix observations portent toutes une étiquette

| # | objet | étiquette |
|---|---|---|
| 1-2 | espace avant `,` et `؟` | `[AR-TYPO-01, verified]` — Netflix §21 **relu en première main** |
| 3 | virgule latine U+002C | `[AR-TYPO-02, verified]` — relevé de codepoint |
| 4 | hamzat qaṭʿ manquantes | `[verified]` — Majmaʿ du Caire 1959/60 |
| 5 | `؟` sur une déclarative | `[verified]` — Zakī 1912, cité `fichier:ligne` |
| 6 | `و قال` détachée | `[verified, indirect + measured]` — Damas + comptage |
| 7 | `ثلاثمائة` soudée | `[AR-ORTH-01, recommendation]` — avec le contre-comptage BAREC |
| 8 | calques `تم` / `من قبل` | **« Weak chain, stated as such »** — `[hypothèse]` |
| 9 | espace avant le point final | **`[dhann ~0.9, no source in this pack]`** |
| 10 | ouverture nominale en presse | `[reported]` — « nothing verified this » |

Sept portent une chaîne jusqu'à une source ; trois sont étiquetées comme non
établies. **Aucune n'est présentée nue.**

### Le moment qui vaut le chantier entier

Observation 9. L'agent constate un espace avant le point final, cherche
l'autorité, lit Netflix §21 à la source, et découvre qu'elle nomme **la virgule,
le point d'interrogation et le point d'exclamation — pas le point**. Il écrit :

> « Almost certainly wrong; I could not find an authority that says so, **and I
> will not invent one**. »

C'est très exactement le mode de défaillance de S3 en RED, inversé. En RED,
l'agent avait comblé une absence de source par une affirmation d'autorité. Ici,
il laisse le trou ouvert et le nomme.

Il pousse la granularité plus loin encore : dans l'observation 4, qui est sourcée,
il isole la sous-question `إنّ` contre `أنّ` et la marque non sourcée séparément.

---

## Deux choses que le GREEN a trouvées et que je n'avais pas vues

### 1. Un trou de conception dans les préréglages — corrigé

S1 a déclaré l'auditoire `foundational`, comme le skill le demande, puis a dû
lancer le vérificateur **deux fois** : `children` est le seul préréglage
fondamental et déclare `diacritics: full`, ce qui éteint `AR-DIAC-01`.

Vérifié : sur les sept préréglages, **aucun** n'apparie `audience: foundational`
et `diacritics: functional`. Un texte en langue simple pour un lecteur adulte non
formé pouvait obtenir le bon plafond de longueur **ou** un contrôle de
vocalisation, jamais les deux.

**Correctif livré** (`acfd668`) : `--set FIELD=VALUE`, répétable, exigeant
`--preset`. `resolve()` acceptait déjà une table d'overrides ; seule la CLI ne
l'exposait pas.

**Un huitième préréglage a été écarté** : il aurait bouché ce trou-là plutôt que
la forme du problème, et un préréglage porte un genre, donc un ratio verbal
mesuré. Ce projet n'a **aucun ratio mesuré** pour « explicatif adulte en langue
simple ». En publier un sans source ni comptage aurait enfreint la règle à
laquelle tout le reste du pack est tenu.

Le scénario S1 tient maintenant en une passe :

```
$ check.py texte.txt --preset children --set diacritics=functional
preset: children (audience=foundational, genre=children)
sentences over the 15-word cap for this audience:
    17 words: الزكاة حصة صغيرة من مالك تخرجها كل سنة لمن يحتاجها من الفقراء والمساكي...
vocalisation: 173 diacritics per 1000 Arabic letters, cited scripture excluded
```

148 tests passent (139 avant). Trois des neuf nouveaux tests passaient **avant**
que l'option existe, argparse rejetant `--set` en bloc ; chacun a été testé par
mutation ensuite.

### 2. Un chiffre à retirer, des deux côtés

L'observation 6 s'appuyait sur deux comptages. J'ai voulu les refaire plutôt que
les croire.

**Sur les fixtures propres, la mesure de l'agent se reproduit exactement :
0 wāw détachée sur 498.** Mon premier essai donnait 28 — mon instrument était
faux : mon lookahead excluait les lettres mais pas les diacritiques, de sorte que
`وَقال` comptait comme détachée. L'agent avait raison, moi non.

**Sur `sources/majma-qahira-244-decisions.md`, elle ne se reproduit pas** :
l'agent annonce 14 sur 2 111 (0,7 %), j'obtiens 77 sur 2 177 (3,5 %). En
inspectant les occurrences, la divergence s'explique — et condamne le chiffre
quel qu'il soit :

```
... 20. ( إعراب اإلسم بعد ) إن ( و ) إذا ...
... ( إقرار اإلستثناء ب ) غير ( و ) سوى ...
```

Ce document est un ouvrage **sur** les particules. Un `و` isolé entre parenthèses
y est l'**objet du discours**, pas une conjonction : le compter comme wāw
détachée est une erreur de catégorie. Et `اإلسم` pour `الإسم` montre une ligature
lām-alef cassée par l'OCR.

**Le corpus est inapte à la question.** Le chiffre majma est retiré des deux
versions. La conclusion — la wāw de ʿaṭf s'écrit soudée — tient sur les fixtures
seules, où elle est nette et re-mesurable.

---

## Ce que ce GREEN ne prouve pas

- **Il ne mesure pas le cas moyen** (voir la réserve en tête).
- **Il ne teste pas l'audit d'existant**, qui est l'usage principal du
  vérificateur selon le RED. Les cinq scénarios portent sur du texte produit ou
  dégradé pour l'occasion, pas sur des pages web réelles.
- **S2** (dépêche de presse) n'avait aucun défaut en RED — 9 ‰, 22 mots, zéro
  règle dure. Il n'a pas été rejoué : un scénario sans défaut ne peut pas montrer
  de fermeture de défaut.
- `AR-TYPO-01` garde un rappel mesuré de 0,62 sur son flanc gauche. Un résultat
  d'espacement propre reste une absence de preuve, non une preuve d'absence —
  le rapport GREEN de S3 le dit lui-même dans sa section « What was not checked ».
