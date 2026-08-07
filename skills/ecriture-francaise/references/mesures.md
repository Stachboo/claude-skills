# Mesures de rythme — calcul et calibration

## Pourquoi mesurer

Les marqueurs lexicaux se corrigent par substitution : on remplace un mot, la faute
disparaît. Le rythme, non. C'est le défaut qui survit à une passe de réécriture, parce
qu'il tient à la façon dont le texte a été produit, pas aux mots choisis.

Il faut donc le chiffrer, sans quoi on discute de goût.

## Le coefficient de variation

Sur la longueur des phrases, en mots :

```
CV = écart-type / moyenne
```

Le coefficient de variation est préférable à l'écart-type seul parce qu'il est sans
dimension. Un texte de phrases longues et un texte de phrases courtes deviennent
comparables.

**Ce qu'il capte.** Un texte machine produit des phrases de longueur voisine. Un
rédacteur alterne : une phrase de six mots qui assène la règle, puis une de soixante
qui la nuance. Le CV mesure cette alternance.

**Ce qu'il ne capte pas.** Un texte peut avoir un bon CV et rester mauvais. La mesure
écarte un défaut, elle ne produit pas une qualité.

## Seuils

| CV | Lecture |
|---|---|
| < 0,40 | rythme plat, signal fort |
| 0,40 – 0,55 | acceptable, sans être vivant |
| > 0,55 | rythme humain |

**Ces seuils sont provisoires.** Ils proviennent d'un échantillon trop restreint pour
fonder une norme. Ils sont utilisables comme indication, pas comme règle de blocage.
Tant qu'ils ne sont pas recalibrés, le vérificateur les signale sans faire échouer.

## Méthode de calibration

Pour transformer ces indications en seuils fondés, il faut une distribution de
référence. La procédure :

1. **Réunir un corpus de contrôle** : au moins trente textes français authentiques du
   genre visé, écrits avant 2022 pour écarter toute contamination. Le genre compte —
   une note juridique, un article de presse et un roman n'ont pas le même rythme, et un
   seuil unique n'a pas de sens.
2. **Mesurer le CV de chaque texte** avec le même découpage en phrases que le
   vérificateur, sans quoi les valeurs ne sont pas comparables.
3. **Calculer les quantiles** de la distribution obtenue.
4. **Fixer le seuil de blocage au 5ᵉ centile** : en dessous, le texte est plus plat que
   95 % des textes humains du même genre.
5. **Consigner** dans ce fichier la taille du corpus, sa composition, la date et les
   quantiles obtenus. Sans cette trace, le seuil n'est pas vérifiable et n'a pas plus
   de valeur qu'une opinion.

Tant que cette procédure n'a pas été exécutée, le tableau ci-dessus reste marqué comme
provisoire.

## Le découpage en phrases

La mesure dépend entièrement de la façon dont on compte les phrases. Le vérificateur
segmente sur `.`, `!`, `?` et `…`, après avoir neutralisé les abréviations courantes
(`M.`, `art.`, `cf.`, `p.`, `etc.`, `n°`…).

Limites connues, à garder en tête avant d'accorder du crédit à une valeur :

- une abréviation non listée coupe une phrase en deux et abaisse artificiellement la
  moyenne ;
- les titres et les cellules de tableau sont comptés comme des phrases s'ils dépassent
  deux mots ;
- les énumérations à puces faussent la distribution, chaque puce comptant pour une
  phrase.

Sur un texte comportant beaucoup de tableaux ou de listes, la mesure de rythme est peu
fiable. Le vérificateur l'indique en donnant le nombre de phrases retenues : en dessous
de trente, la valeur est indicative.

## Autres mesures utiles, non implémentées

**Densité de faits vérifiables.** Nombre de chiffres, dates, noms propres et références
pour cent mots. Un texte machine est pauvre en éléments vérifiables parce qu'il ne peut
pas en inventer sans risque. Mesure prometteuse, mais elle exige de distinguer un
chiffre porteur d'information d'un numéro de version ou de page. Non implémentée.

**Uniformité des paragraphes.** Même calcul de CV, appliqué au nombre de phrases par
paragraphe. Simple à ajouter. À faire.

**Répétition des ouvertures.** Proportion de phrases commençant par le même type de
mot. Un texte machine ouvre souvent sur un connecteur. Simple à ajouter.

## Interpréter honnêtement

Une mesure basse est un signal, pas un verdict. Un texte juridique cite des articles et
reprend des formules imposées : son rythme est contraint par le genre, et il sera plat
sans que le rédacteur y soit pour quelque chose.

Inversement, un CV élevé ne prouve rien. On peut alterner phrases courtes et longues
mécaniquement, et produire un texte creux.

La mesure sert à repérer un défaut réel, pas à décerner un certificat.
