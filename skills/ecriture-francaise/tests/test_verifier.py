# -*- coding: utf-8 -*-
"""Tests du vérificateur : la règle TYPO-11, espace ordinaire collée à une insécable.

Lancer depuis la racine du skill :  python -m unittest discover -s tests -t .
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from verifier import analyse  # noqa: E402

NBSP = " "
NARROW = " "


def regles(texte, suffixe=".md"):
    return [f["regle"] for f in analyse(texte, suffixe)[0]]


class EspaceDoublee(unittest.TestCase):

    def test_defaut_de_l_ancien_correcteur(self):
        # Ce que corriger.py produisait avant le 2026-10-01 : chiffre, espace,
        # insécable, deux-points. Aucune règle ne le voyait.
        self.assertIn("TYPO-11", regles("## Étape 1 " + NBSP + ": vérifier"))
        self.assertIn("TYPO-11", regles("Mesuré le 2026-09-16 " + NBSP + ": fin."))

    def test_insecable_puis_espace(self):
        self.assertIn("TYPO-11", regles("«" + NBSP + " mot" + NBSP + "»"))

    def test_fine_insecable(self):
        self.assertIn("TYPO-11", regles("Vraiment " + NARROW + "?"))

    def test_texte_correct(self):
        self.assertNotIn("TYPO-11", regles("## Étape 1" + NBSP + ": vérifier"))
        self.assertNotIn("TYPO-11", regles("«" + NBSP + "mot" + NBSP + "» et 15" + NBSP + "000"))

    def test_balise_html_avant_insecable(self):
        # Une balise effacée laisse plusieurs espaces : ce n'est pas le défaut.
        html = "<p><strong>Prix</strong>&nbsp;: 10 €</p>"
        self.assertNotIn("TYPO-11", regles(html, ".html"))

    def test_insecable_avant_balise_html(self):
        html = "<p>Prix&nbsp;<em>net</em></p>"
        self.assertNotIn("TYPO-11", regles(html, ".html"))

    def test_separateur_html_volontaire(self):
        # Trouvés en validation (2026-10-01) : des séparateurs de mise en page,
        # pas de la ponctuation française. Ne pas les signaler.
        html = "<p>Date 2026-06-24 &nbsp;·&nbsp; Pour Stachboo &nbsp;|&nbsp; Suite</p>"
        self.assertNotIn("TYPO-11", regles(html, ".html"))

    def test_ecart_volontaire_apres_icone(self):
        self.assertNotIn("TYPO-11", regles("<td>✓&nbsp; Livré, validé</td>", ".html"))

    def test_faute_dans_un_livrable_html(self):
        # Le cas réel : un livrable généré depuis un Markdown abîmé.
        html = "<p>Entre le 28 et le 31 juillet 2026 &nbsp;: rien.</p>"
        self.assertIn("TYPO-11", regles(html, ".html"))

    def test_ligne_qui_suit_un_bloc_de_code_est_verifiee(self):
        # Trouvé en validation : « ^\s{4,}\S » traversait les sauts de ligne, et
        # la première ligne de prose après chaque bloc de code était effacée
        # avant vérification. 24 fautes manquées sur un seul plan.
        texte = "Avant.\n\n```ts\nx = 1\n```\n\n- [ ] **Step 2 " + NBSP + ": Lancer**\n"
        self.assertIn("TYPO-11", regles(texte))

    def test_code_indente_toujours_ignore(self):
        self.assertNotIn("TYPO-11", regles("Texte.\n\n    code 1 " + NBSP + ": x\n"))

    def test_code_en_ligne_ignore(self):
        self.assertNotIn("TYPO-11", regles("Lancer `a " + NBSP + ": b` ici."))


if __name__ == "__main__":
    unittest.main()
