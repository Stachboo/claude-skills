# -*- coding: utf-8 -*-
"""AR-ORTH-02: hamzat qat' or madda left off a word that has only one spelling.

The rule is a closed list on purpose. Each bare form below is a misspelling
and never another word, so the rule is decidable without a morphological
analyser. The negative cases are the traps found while measuring it on BAREC
v1.0 (2026-10-01): a prefix that makes a real word (wahid, fanin, wala) and
a bare form that is itself a word (al-qiran, the marriage contract).
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rules import load_rules, run_rules  # noqa: E402

CHECK = ROOT / "scripts" / "check.py"
RULES = load_rules(ROOT / "assets" / "rules.json")


def ids(text):
    return [f["id"] for f in run_rules(text, RULES) if f["id"] == "AR-ORTH-02"]


def frame(word):
    return "ذهب الرجل " + word + " البيت."


class TestFires(unittest.TestCase):

    def test_every_bare_form_on_the_list_fires(self):
        for w in ("الى", "اذا", "او", "ان", "انه", "اكثر", "ايضا", "اول", "امام",
                  "اخرى", "احد", "اصبح", "اطار", "اذ", "اما", "الاسلام", "الانسان",
                  "الان", "الاف", "الاخرة", "الاخرين", "اخرين"):
            self.assertEqual(len(ids(frame(w))), 1, w)

    def test_vocalised_bare_form_still_fires(self):
        self.assertEqual(len(ids(frame("الَى"))), 1)
        self.assertEqual(len(ids(frame("ايضًا"))), 1)

    def test_allowed_prefixes(self):
        for w in ("واذا", "فاذا", "وانه", "فانه", "وايضا", "واكثر"):
            self.assertEqual(len(ids(frame(w))), 1, w)

    def test_cli_exits_one(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as f:
            f.write("ذهب الولد الى المدرسة.")
            path = f.name
        p = subprocess.run([sys.executable, str(CHECK), path],
                           capture_output=True, text=True, encoding="utf-8")
        Path(path).unlink()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("AR-ORTH-02", p.stdout)


class TestDoesNotFire(unittest.TestCase):

    def test_correct_spellings(self):
        for w in ("إلى", "إذا", "أو", "أن", "إن", "أنه", "إنه", "أكثر", "أيضًا", "أول",
                  "أمام", "إمام", "أخرى", "أحد", "أصبح", "إطار", "إذ", "أما", "إما",
                  "الإسلام", "الإنسان", "الآن", "آلاف", "الآخرة", "الآخرين", "آخرين"):
            self.assertEqual(ids(frame(w)), [], w)

    def test_prefix_that_makes_a_real_word(self):
        # wahid "one", fanin "perishing" (Q 55:26), wala (verb), waw, Fao.
        for w in ("واحد", "فان", "والى", "واو", "فاو"):
            self.assertEqual(ids(frame(w)), [], w)

    def test_bare_form_that_is_another_word(self):
        # aqd al-qiran: the marriage contract. Found twice in BAREC Wikipedia.
        self.assertEqual(ids("استمرت مراسم عقد القران ساعة."), [])

    def test_list_word_inside_a_longer_word(self):
        for w in ("اولاد", "انسان", "امامة", "اذاعة", "الاخر", "اكثرية"):
            self.assertEqual(ids(frame(w)), [], w)

    def test_persian_and_urdu_letters_are_part_of_the_word(self):
        # Found on BAREC: tughyan written with Farsi yeh U+06CC (Kalima), and
        # Persian quoted in Wikipedia ("gurkani", with U+06A9 and U+06CC). A
        # boundary that only knew U+0621-U+064A read "an" inside both words.
        for w in ("طغیان", "گورککانی".replace("کک", "ک"),
                  "کان", "انی", "اذاہ"):
            self.assertEqual(ids(frame(w)), [], w)

    def test_arabic_punctuation_still_ends_a_word(self):
        for w in ("الى،", "اذا؟", "او؛"):
            self.assertEqual(len(ids(frame(w))), 1, w)

    def test_shadda_is_never_required(self):
        # Missing shadda is the norm in functional prose: 95.5% in BAREC.
        self.assertEqual(ids("ثم كل مرة قال إن الحق معه."), [])


class TestRuleTable(unittest.TestCase):

    def test_rule_is_hard_and_sourced(self):
        rule = next(r for r in RULES if r["id"] == "AR-ORTH-02")
        self.assertEqual(rule["severity"], "hard")
        self.assertIn("Damascus", rule["isnad"])
        self.assertIn("Harun", rule["isnad"])
        self.assertIn("BAREC", rule["isnad"])


if __name__ == "__main__":
    unittest.main()
