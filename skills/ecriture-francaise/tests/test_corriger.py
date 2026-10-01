# -*- coding: utf-8 -*-
"""Tests du correcteur typographique.

Lancer depuis la racine du skill :  python -m unittest discover -s tests -t .
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from corriger import corriger  # noqa: E402

NBSP = " "
NARROW = " "
# Une espace ordinaire collée à une espace insécable, dans un sens ou dans
# l'autre : le défaut constaté le 2026-10-01 sur « ## Étape 1 : ».
ESPACE_DOUBLE = re.compile("[ ][  ]|[  ][ ]")


def md(texte):
    compteur = {}
    return corriger(texte, ".md", compteur), compteur


class DeuxPoints(unittest.TestCase):

    def test_chiffre_espace_deux_points_une_seule_insecable(self):
        # Le cas qui a échoué : la garde des heures empêchait de partir juste
        # après le chiffre, le motif partait après l'espace et la laissait.
        out, _ = md("## Étape 1 : vérifier")
        self.assertEqual(out, "## Étape 1" + NBSP + ": vérifier")

    def test_mot_espace_deux_points(self):
        self.assertEqual(md("Voici : la liste")[0], "Voici" + NBSP + ": la liste")

    def test_mot_colle_aux_deux_points(self):
        self.assertEqual(md("Voici: la liste")[0], "Voici" + NBSP + ": la liste")

    def test_plusieurs_espaces(self):
        self.assertEqual(md("Voici   : la liste")[0], "Voici" + NBSP + ": la liste")

    def test_heure_intacte(self):
        self.assertEqual(md("Rendez-vous à 12:30 précises")[0], "Rendez-vous à 12:30 précises")

    def test_url_intacte(self):
        self.assertEqual(md("Voir http://exemple.fr ici")[0], "Voir http://exemple.fr ici")

    def test_rapport_numerique_intact(self):
        # Chiffre collé aux deux-points : traité comme une heure ou un ratio.
        self.assertEqual(md("un ratio 3:1 net")[0], "un ratio 3:1 net")


class Idempotence(unittest.TestCase):

    TEXTE = ("## Étape 1 : vérifier\n\nVraiment ? Oui ; « mot » et l'article : "
             "voilà... Puis 15 h : fin ! Et ( ceci ).")

    def test_aucune_espace_doublee(self):
        out, _ = md(self.TEXTE)
        self.assertIsNone(ESPACE_DOUBLE.search(out), repr(out))

    def test_deuxieme_passage_ne_change_rien(self):
        une, _ = md(self.TEXTE)
        deux, compteur = md(une)
        self.assertEqual(une, deux)
        self.assertEqual(compteur, {}, "un texte déjà corrigé ne doit compter aucune correction")


class Protections(unittest.TestCase):

    def test_code_markdown_intact(self):
        out, _ = md("Lancer `a : b` puis\n```\nx : y\n```\n")
        self.assertIn("`a : b`", out)
        self.assertIn("x : y", out)

    def test_entite_html_intacte(self):
        compteur = {}
        out = corriger("<p>Prix&nbsp;: 10 €</p>", ".html", compteur)
        self.assertIn("&nbsp;", out)


class FinsDeLigne(unittest.TestCase):
    """--ecrire doit rendre le fichier avec ses fins de ligne d'origine.

    Constaté le 2026-10-01 : sous Windows, write_text traduisait chaque \\n
    en \\r\\n, si bien qu'un fichier LF ressortait en CRLF à chaque passage.
    """

    def _passer(self, octets):
        import subprocess
        import tempfile
        script = Path(__file__).resolve().parents[1] / "scripts" / "corriger.py"
        with tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False) as f:
            f.write(octets)
            chemin = f.name
        subprocess.run([sys.executable, str(script), chemin, "--ecrire"],
                       capture_output=True, check=True)
        sortie = Path(chemin).read_bytes()
        Path(chemin).unlink()
        return sortie

    def test_fichier_lf_reste_lf(self):
        sortie = self._passer("Voici : un\nDeux : trois\n".encode("utf-8"))
        self.assertNotIn(b"\r\n", sortie)
        self.assertEqual(sortie.count(b"\n"), 2)

    def _sortie_standard(self, octets):
        import subprocess
        import tempfile
        script = Path(__file__).resolve().parents[1] / "scripts" / "corriger.py"
        with tempfile.NamedTemporaryFile("wb", suffix=".md", delete=False) as f:
            f.write(octets)
            chemin = f.name
        p = subprocess.run([sys.executable, str(script), chemin],
                           capture_output=True, check=True)
        Path(chemin).unlink()
        return p.stdout

    def test_sortie_standard_garde_les_fins_de_ligne(self):
        lf = self._sortie_standard("Voici : un\nDeux : trois\n".encode("utf-8"))
        self.assertNotIn(b"\r", lf)
        crlf = self._sortie_standard("Voici : un\r\nDeux : trois\r\n".encode("utf-8"))
        self.assertEqual(crlf.count(b"\r\n"), 2)
        self.assertNotIn(b"\r\r\n", crlf)

    def test_fichier_crlf_reste_crlf(self):
        sortie = self._passer("Voici : un\r\nDeux : trois\r\n".encode("utf-8"))
        self.assertEqual(sortie.count(b"\r\n"), 2)
        self.assertNotIn(b"\r\r\n", sortie)


if __name__ == "__main__":
    unittest.main()
