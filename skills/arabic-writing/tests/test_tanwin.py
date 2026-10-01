# -*- coding: utf-8 -*-
"""AR-TANWIN-01: the two placements of tanwin al-fath, mixed in one text.

Two byte sequences render almost identically and are both in print:
  before the alif   letter + U+064B + U+0627   (Netflix house rule)
  on the alif       letter + U+0627 + U+064B
Measured on BAREC v1.0 on 2026-10-01, functional prose: 7 publishers out of 15
put the mark before the alif in majority, 6 on it. That is a divergence, so the
rule never says which placement is right. It only reports a text that uses
both, and it never changes the exit code.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check import tanwin_placements  # noqa: E402
from rules import load_rules  # noqa: E402

CHECK = ROOT / "scripts" / "check.py"
RULES = ROOT / "assets" / "rules.json"

FATHATAN = "ً"
ALIF = "ا"
SHADDA = "ّ"

# aydan and jiddan, built from codepoints so the byte order under test is the
# one written here and not whatever an editor normalised a literal into.
AYDAN_BEFORE = "أيض" + FATHATAN + ALIF
AYDAN_ON = "أيض" + ALIF + FATHATAN
JIDDAN_BEFORE = "جد" + FATHATAN + ALIF
JIDDAN_ON = "جد" + ALIF + FATHATAN
JIDDAN_SHADDA_BEFORE = "جد" + SHADDA + FATHATAN + ALIF
AYDAN_BARE = "أيض" + ALIF

ORNATE_OPEN = "﴿"
ORNATE_CLOSE = "﴾"


def sentence(word):
    return "قال ذلك " + word + "، ثم انصرف."


def run(text, *args):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    p = subprocess.run([sys.executable, str(CHECK), path, *args],
                       capture_output=True, text=True, encoding="utf-8")
    Path(path).unlink()
    return p


class TestPlacementCount(unittest.TestCase):

    def test_before_the_alif(self):
        c = tanwin_placements(sentence(AYDAN_BEFORE))
        self.assertEqual((len(c["before"]), len(c["on"])), (1, 0))

    def test_on_the_alif(self):
        c = tanwin_placements(sentence(AYDAN_ON))
        self.assertEqual((len(c["before"]), len(c["on"])), (0, 1))

    def test_shadda_between_letter_and_mark_still_counts_as_before(self):
        c = tanwin_placements(sentence(JIDDAN_SHADDA_BEFORE))
        self.assertEqual((len(c["before"]), len(c["on"])), (1, 0))

    def test_bare_alif_is_neither(self):
        # Omitting the mark is attested usage (20.6% in BAREC functional prose)
        # and is not this rule's business.
        c = tanwin_placements(sentence(AYDAN_BARE))
        self.assertEqual((len(c["before"]), len(c["on"])), (0, 0))

    def test_cited_scripture_is_not_counted(self):
        # A quoted verse follows the mushaf's own conventions, not the
        # author's house style.
        text = sentence(AYDAN_BEFORE) + " " + ORNATE_OPEN + JIDDAN_ON + ORNATE_CLOSE
        c = tanwin_placements(text)
        self.assertEqual((len(c["before"]), len(c["on"])), (1, 0))


class TestRuleTable(unittest.TestCase):

    def test_rule_is_a_sourced_divergence(self):
        rule = next(r for r in load_rules(RULES) if r["id"] == "AR-TANWIN-01")
        self.assertEqual(rule["severity"], "divergence")
        self.assertEqual(rule["kind"], "consistency")
        self.assertIn("BAREC", rule["isnad"])


class TestCli(unittest.TestCase):

    def test_mixed_placements_report_one_divergence_and_exit_zero(self):
        p = run(sentence(AYDAN_BEFORE) + " " + sentence(JIDDAN_ON), "--json")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        report = json.loads(p.stdout)
        found = [f for f in report["findings"] if f["id"] == "AR-TANWIN-01"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["severity"], "divergence")
        self.assertEqual(report["counts"]["divergence"], 1)
        self.assertEqual((found[0]["before"], found[0]["on"]), (1, 1))

    def test_one_placement_throughout_reports_nothing(self):
        for text in (sentence(AYDAN_BEFORE) + " " + sentence(JIDDAN_BEFORE),
                     sentence(AYDAN_ON) + " " + sentence(JIDDAN_ON)):
            p = run(text, "--json")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            ids = [f["id"] for f in json.loads(p.stdout)["findings"]]
            self.assertNotIn("AR-TANWIN-01", ids)

    def test_finding_points_at_the_minority_placement(self):
        text = (sentence(AYDAN_BEFORE) + "\n" + sentence(JIDDAN_BEFORE) + "\n"
                + sentence(JIDDAN_ON))
        report = json.loads(run(text, "--json").stdout)
        f = next(f for f in report["findings"] if f["id"] == "AR-TANWIN-01")
        self.assertEqual(f["line"], 3)

    def test_human_report_names_both_counts(self):
        p = run(sentence(AYDAN_BEFORE) + " " + sentence(JIDDAN_ON), "--preset", "news")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("AR-TANWIN-01", p.stdout)
        self.assertIn("1 divergence", p.stdout)


if __name__ == "__main__":
    unittest.main()
