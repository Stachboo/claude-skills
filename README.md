# claude-skills

Six **Agent Skills** écrits sur mesure pour [Claude Code](https://claude.com/claude-code) (et tout
runtime qui charge des [Agent Skills](https://agentskills.io)) : audit SEO/GEO, audit performance et
sécurité, écriture française débarrassée des marqueurs d’IA, relecture et rédaction en arabe
littéraire, comparateur de noms de domaine, et
rédaction de critique d’art.

Le fil conducteur des six : **aucun chiffre inventé**. Chaque métrique vient d’une mesure réelle ;
ce qui n’a pas pu être mesuré s’affiche `N/A` avec sa raison, jamais comblé par une estimation.

## Les skills

| Skill | Ce qu’il fait | Dépendances |
|---|---|---|
| [`geo-toolkit`](skills/geo-toolkit) | Audit et pilotage en 5 modules : technique + **GEO** (citations IA), backlinks & mentions de marque, CTR/Search Console, conversion (CRO), leads. Score /100 par module, quick wins triés par impact/effort, prochaine mesure datée. | MCP Ahrefs / Semrush / Windsor.ai (optionnels : le module tombe en `non mesuré` si absent) |
| [`audit`](skills/audit) | Audit d’une URL : performance (Lighthouse/PSI), en-têtes HTTP, TLS, CVE des dépendances, secrets exposés. 5 collecteurs en parallèle → `audit.json` validé par schéma → `audit-report.md`. Exit code exploitable en CI (`--fail-on`). | Node 18+, Chrome (optionnel), clé PageSpeed Insights (optionnelle) |
| [`ecriture-francaise`](skills/ecriture-francaise) | Typographie française (espaces insécables, guillemets « », apostrophes) **et** retrait des marqueurs lexicaux, syntaxiques et rythmiques du français généré par un modèle. Deux scripts : `verifier.py` (diagnostic chiffré) et `corriger.py` (correction typographique automatique). | Python 3 (bibliothèque standard uniquement) |
| [`arabic-writing`](skills/arabic-writing) | Relecture et rédaction en **arabe littéraire moderne** (fuṣḥā). Vérifie ponctuation, encodage et densité de vocalisation contre des décisions d’académies **sourcées**, et règle la longueur des phrases selon le registre visé (7 préréglages  presse, juridique, religieux, littéraire…). Pensé pour valider un texte arabe **sans lire l’arabe**  chaque constat sort en anglais avec sa source. Son rôle premier  empêcher l’IA d’inventer une règle. | Python 3.8+ (bibliothèque standard uniquement) |
| [`domain-price`](skills/domain-price) | Disponibilité d’un nom de domaine et comparaison des prix entre registrars. Règle d’or : **jamais un seul fournisseur**, minimum 3 sources croisées (RDAP + registrars). | Python 3 (bibliothèque standard uniquement) |
| [`art-criticism-writing`](skills/art-criticism-writing) | Notices d’œuvres, cartels, textes d’exposition et présentations de série. Méthode : matière → forme → sujet → sens → résonance, chaque phrase vérifiable à l’œil, on ouvre au lieu de conclure. Modèle stylistique : Daniel Arasse, pas le communiqué de presse. | aucune |

Les skills sont en français, sauf `arabic-writing`, documenté en anglais ; ils fonctionnent tout aussi bien sur des contenus anglophones.

## Installation

### Via le marketplace de plugins (recommandé)

```
/plugin marketplace add Stachboo/claude-skills
/plugin install stachboo-skills@stachboo-skills
```

Les six skills deviennent disponibles dans toutes vos sessions.

### À la main

```bash
git clone https://github.com/Stachboo/claude-skills.git
cp -r claude-skills/skills/* ~/.claude/skills/
```

Sous Windows, `skills/audit/deploy.ps1` crée une jonction depuis `~/.claude/skills/audit` vers le
dossier du dépôt, ce qui évite de recopier à chaque modification.

## Notes

- **`audit`** : au premier lancement, copier `audit.config.example.json` vers `audit.config.json`
  (ignoré par git : il contient votre clé PSI et vos chemins locaux). Sans ce fichier, les URLs
  `https://…` complètes fonctionnent quand même ; seules les cibles nommées et `--all` en ont besoin.
- **`geo-toolkit`** : les données GEO périment vite (~13 semaines). Le skill impose de dater chaque
  mesure et d’indiquer quand re-mesurer.

## Skill voisin

[`legal-compliance-fr-eu-skill`](https://github.com/Stachboo/legal-compliance-fr-eu-skill) génère
les documents légaux obligatoires d’un site FR/UE (mentions légales, CGV, RGPD, cookies, rétractation)
à partir des sources officielles. Dépôt séparé, même auteur.

## Licence

MIT, voir [LICENSE](LICENSE).
