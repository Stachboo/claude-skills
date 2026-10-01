# Baseline RED — ce qu'un agent fait de l'arabe SANS le skill

**Date :** 2026-09-17 · **Statut : [mesuré]** · Cinq scénarios, cinq sous-agents neufs,
skill absent (il n'existait alors qu'en coquille vide).

**Réserve de méthode.** Ces agents héritent du `CLAUDE.md` de l'utilisateur, qui porte une méthode
de vérification mais **rien sur le style arabe**. La baseline est donc « sans skill d'écriture
arabe », non « sans aucune instruction ». C'est inévitable dans cet environnement, et il vaut mieux
que ce soit écrit.

---

## Le résultat, et il contredit ce que le plan prédisait

| scénario | phrases | phrase la plus longue | plafond | diacritiques ‰ | défauts durs détectés |
|---|---|---|---|---|---|
| S1 — zakat, lecteur profane | 6 | 24 mots | 26 | 43 | **aucun** |
| S2 — dépêche de presse | 3 | 22 mots | 26 | 9 | **aucun** |
| S4 — paragraphe avec citation | 4 | 23 mots | 26 | **784** | **aucun** |
| S5 — noms propres | 1 | 14 mots | 26 | **770** | **aucun** |

**Aucune des six règles dures n'a été déclenchée par une seule des quatre productions.**

Contrôles effectués sur chaque texte : espace avant ponctuation arabe · ponctuation latine dans du
texte arabe · centaines soudées · tiret cadratin · latin nu dans une phrase arabe · `(ص)` abrégé ·
parenthèses ornées inversées. Zéro occurrence.

Et sur S4, le registre religieux est **exact** : verset entre `﴿ ﴾`, hadith entre `« »`,
`ﷺ` en U+FDFA, références `[البقرة: ١٥٣]` et `[رواه البخاري ومسلم]`.

Sur S5, le défaut que le dossier prédisait le plus fortement — les noms propres laissés en
caractères latins, `Umm Salama`, `Darul Ihsan` — **ne s'est pas produit** : l'agent a écrit
`أُمُّ سَلَمَةَ` et `دَارِ الْإِحْسَانِ`.

---

## Ce que cela dit du skill, sans détour

**Les six règles dures ne déclencheront presque jamais sur de l'arabe fraîchement produit par un
modèle.** Leur cible n'est pas là. Elle est dans le texte **humain, ancien, traduit, recopié d'un
CMS** — exactement le cas qui a déclenché ce chantier, des pages web dégradées.

Cela ne les invalide pas. Cela déplace leur usage, et il faut l'écrire dans le skill : ce
vérificateur sert à **auditer de l'existant**, pas à corriger ce qu'un modèle vient d'écrire.

---

## Les trois défauts réels, dont deux n'étaient pas prédits

### 1. Sur-vocalisation de la prose courante — NON PRÉDIT

S4 à **784 ‰** et S5 à **770 ‰** : toute la prose est diacritée, pas seulement les citations.

C'est contraire à la décision du Majmaʿ de 1959-60 (`12`), qui réserve le **شكل كامل** aux āyāt et
aux hadiths et prescrit ailleurs l'omission de la fatḥa, et au principe fonctionnel corroboré par
Netflix et la Banque mondiale (`08`) : on diacrite là où l'absence change le sens.

À titre de comparaison, S2 — la dépêche — est à **9 ‰**, ce qui est juste.

**Le modèle sur-applique le diacritique dès qu'il sent un registre soutenu.** C'est un défaut
mesurable, et aucune de mes six règles ne l'attrape.

### 2. Purisme non sourcé dans la relecture — NON PRÉDIT, et c'est le plus intéressant

S3 a relu le texte volontairement dégradé et a trouvé **presque tout** : virgule latine, espace
avant ponctuation, `و قال` séparé, hamzas manquantes, `إن`/`أن` après un verbe de parole,
le calque `تم + من قبل`, l'ordre SVO au lieu de VSO. C'est une bonne relecture.

**Mais elle a aussi énoncé une règle que les sources contredisent :**

> « Em dashes used as parenthetical brackets. This is an English/French typographic convention
> imported into Arabic; standard Arabic uses parentheses or commas for a parenthetical clause. »

C'est faux. **Zakī 1912** donne au tiret deux emplois légitimes, dont précisément l'incise
(`06`) ; **Hārūn** le confirme et y ajoute deux emplois de plus (`12`) ; et le **guide de la
Banque mondiale** en donne l'exemple exact — `أعلن أحمد الشربيني – مؤلف هذا الكتاب – أنه...` (`08`).

L'agent a condamné un usage attesté depuis l'acte de naissance de la ponctuation arabe, en le
présentant comme un import occidental. Et **aucun de ses quinze points ne portait de source**.

> **C'est là qu'est la valeur du skill.** Pas à trouver les fautes — un bon modèle les trouve.
> À **empêcher le faux positif d'autorité** : la règle inventée, énoncée avec aplomb, sans isnad.

### 3. L'auditoire n'est jamais demandé

Aucun des quatre agents n'a demandé pour qui il écrivait. S1 visait « des lecteurs sans formation
religieuse » et a produit des phrases allant jusqu'à **24 mots** — au-dessus du plafond
**fondamental** (15) même si sous le plafond **avancé** (26).

Le modèle choisit un registre par défaut, plutôt dense, et ne le déclare pas.

---

## Conséquences pour la suite du plan

**Pour le `SKILL.md` (tâche 10)** — le corps ne doit pas être construit autour des six règles
dures. Il doit être construit autour de ce qui manque réellement :

1. **déclarer l'auditoire avant d'écrire** — un préréglage, une fois ;
2. **la politique de diacritiques** : plein sur les citations, fonctionnel ailleurs ;
3. **ne jamais énoncer une règle sans sa source** — et la contre-liste des règles souvent
   inventées, à commencer par « le tiret est un import occidental », qui est faux ;
4. **l'audit d'existant** comme usage principal du vérificateur.

**Pour la table de règles (tâche 4)** — ajouter deux entrées que la baseline a révélées :

| id | sévérité | ce qu'elle attrape |
|---|---|---|
| `AR-DIAC-01` | recommandation | prose courante au-dessus d'un seuil de diacritiques hors citation |
| `AR-DASH-01` | *(à l'inverse)* | **ne pas** signaler le tiret d'incise — documenter qu'il est légitime |

**Pour le budget de faux positifs (tâche 8)** — la baseline confirme qu'il est le bon garde-fou :
le risque n'est pas de rater des fautes, c'est d'en inventer.

---

## Fichiers

Sortie brute des cinq agents : transcriptions de session du 2026-09-17.
Ce fichier sera recopié en `arabic-writing/tests/baseline/results-red.md` à la tâche 2.
