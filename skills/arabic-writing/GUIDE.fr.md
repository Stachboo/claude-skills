# Guide de démarrage

Ce guide s’adresse aux débutants. La documentation complète, en anglais, est dans
[`README.md`](README.md) et [`SKILL.md`](SKILL.md). Version arabe : [`GUIDE.ar.md`](GUIDE.ar.md).

## À quoi sert ce skill

`arabic-writing` s’ajoute à votre assistant d’IA (Claude Code, Codex, Gemini CLI, Cursor…). Il
l’aide à relire et à rédiger de l’arabe littéraire moderne.

Il vérifie la ponctuation, l’encodage, la densité des voyelles écrites (le *tashkīl*) et la longueur
des phrases. Chaque remarque cite sa source : une décision d’académie de langue arabe ou un guide
de style publié.

Son rôle premier est d’empêcher l’IA d’inventer une règle. Un modèle relit bien l’arabe, mais il
lui arrive d’affirmer une règle qui n’existe pas. Pour quelqu’un qui ne lit pas l’arabe, une règle
inventée et une vraie se ressemblent.

Vous n’avez pas besoin de lire l’arabe pour l’utiliser : les remarques sortent en anglais.

## Ce qu’il ne fait pas

- Il ne corrige ni l’orthographe ni la grammaire.
- Il ne tranche aucune question de fiqh.
- Il ne choisit pas de camp quand les académies se contredisent.
- Un texte qui cite le Coran ou un hadith doit être relu par une personne qualifiée avant d’être
  publié.

## Étape 1  : vérifier que Python est installé

Le skill a besoin de Python 3.8 ou plus récent, sans rien d’autre à installer.

Ouvrez un terminal (sous Windows : PowerShell) et tapez :

```
python --version
```

Sur Mac et Linux, tapez `python3` à la place de `python`, ici comme dans tout le reste du guide.

Si la commande est introuvable, installez Python depuis [python.org](https://www.python.org/downloads/).
Sous Windows, cochez la case **Add python.exe to PATH** pendant l’installation.

## Étape 2  : installer le skill

La méthode la plus simple ne demande aucun outil :

1. Ouvrez [github.com/Stachboo/claude-skills](https://github.com/Stachboo/claude-skills).
2. Cliquez sur **Code**, puis sur **Download ZIP**.
3. Décompressez le fichier.
4. Copiez le dossier `skills/arabic-writing` dans le dossier des skills de votre assistant.

| assistant | dossier |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex, Gemini CLI, Cursor | `~/.agents/skills/` |

Le signe `~` désigne votre dossier personnel. Sous Windows, c’est `C:\Users\VotreNom`. Créez le
dossier `skills` s’il n’existe pas.

Dans Claude Code, deux commandes suffisent :

```
/plugin marketplace add Stachboo/claude-skills
/plugin install stachboo-skills@stachboo-skills
```

Relancez ensuite votre assistant.

## Étape 3  : l’utiliser avec votre assistant

Aucune commande à retenir. Demandez en français ce que vous voulez, par exemple :

- « Relis ce texte arabe, c’est un article de presse. »
- « Écris un paragraphe en arabe pour des lecteurs sans formation religieuse. »
- « Vérifie cette page en arabe avant que je la publie. »

Dites toujours à qui le texte s’adresse. C’est ce qui fixe la longueur maximale des phrases.

## Étape 4 (facultative) : lancer le vérificateur vous-même

Enregistrez votre texte dans un fichier encodé en UTF-8. Dans le Bloc-notes de Windows :
**Fichier → Enregistrer sous**, puis choisissez **UTF-8** dans la liste « Encodage ».

Placez-vous dans le dossier du skill, puis tapez :

```
python scripts/check.py texte.txt --preset news
```

### Lire le résultat

La dernière ligne résume tout, par exemple `2 hard, 0 recommendation, 0 divergence`.

| niveau | sens | que faire |
|---|---|---|
| **hard** | faute établie, avec sa source | corriger |
| **recommendation** | question de jugement | à vous de décider |
| **divergence** | les académies ne sont pas d’accord | rien à corriger, juste à savoir |

Chaque remarque indique la règle, la correction et la source.

Le programme rend aussi un code de sortie, utile si vous l’automatisez : **0** veut dire aucune
faute établie, **1** au moins une, **2** que la vérification n’a pas pu avoir lieu (fichier
introuvable, mauvais encodage, préréglage inconnu). Le code 2 ne juge pas le texte : corrigez
l’entrée et relancez.

### Choisir le préréglage

| préréglage | pour quel texte |
|---|---|
| `news` | dépêche, article de presse |
| `magazine` | article de magazine, analyse |
| `literary` | récit, texte littéraire |
| `legal` | texte juridique ou administratif |
| `reference` | texte de référence, technique ou scientifique |
| `religious` | texte religieux |
| `children` | texte pour enfants |

Pour un texte simple destiné à des **adultes** débutants :

```
python scripts/check.py texte.txt --preset children --set diacritics=functional
```

## En cas de problème

| message | solution |
|---|---|
| `command not found` ou `is not recognized` | essayez `python3` ou `py`, sinon installez Python (étape 1) |
| `cannot read … No such file` | vérifiez le nom et l’emplacement du fichier |
| `it is not UTF-8` | réenregistrez le fichier en UTF-8 (étape 4) |
| `Unknown preset` | choisissez un nom du tableau ci-dessus |
