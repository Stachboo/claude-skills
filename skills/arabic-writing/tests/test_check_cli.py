# -*- coding: utf-8 -*-
"""The CLI is the only thing this skill can actually enforce.

The portable Agent Skill spec has no hooks, no model field, no effort field. A
script that exits non-zero is the whole enforcement surface, so these tests are
about the contract at the process boundary -- exit code, what reaches stdout,
what reaches stderr -- and not about the internals, which their own modules
test.

Three exit codes, and they must stay distinguishable:
  0  nothing hard was violated
  1  a hard rule was violated
  2  the run could not happen (bad usage, unreadable input, broken table)

A crash that returns 1 masquerades as a hard finding; a crash that returned 0
would be worse. Several tests below exist only to pin that down.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check.py"

# Written as escapes, never as literals. U+FD3E is named ORNATE LEFT
# PARENTHESIS but is General_Category Pe -- a closer -- so a literal pasted
# into the source reads as the opposite of what it does. U+FD3F opens.
ORNATE_OPEN = "\uFD3F"
ORNATE_CLOSE = "\uFD3E"

# Fully vocalised. Correct inside a citation, wrong in running prose.
VERSE = ("إِنَّ اللَّهَ"
         " مَعَ"
         " الصَّابِرِينَ")
HADITH = ("إِنَّمَا"
          " الْأَعْمَالُ"
          " بِالنِّيَّاتِ")

# Running prose, fully vocalised: the defect the RED baseline measured at 784
# and 770 diacritics per 1000 Arabic letters. Copied from test_rules.py, which
# already uses it for the same purpose.
VOCALISED_PROSE = "قَالَ الْوَزِيرُ إِنَّ الْأَمْرَ قَدِ انْتَهَى وَلَا رَجْعَةَ فِيهِ."

# News register: one functional mark, the tanwin fath. Taken from the clean
# corpus in test_rules.py, which already proves it fires no hard rule, so a
# failure here can only be about vocalisation.
NEWS_PROSE = "قال الوزير، ثم صمت طويلًا؛ ولم يجب عن السؤال. لا أحد يدري!"

# Plain, unvocalised prose. Used as the neutral carrier around a citation.
PLAIN = "قال الوزير، ثم صمت."
PLAIN_TAIL = " ثم انصرف القوم دون جواب."


def run(text, *args):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    p = subprocess.run(
        [sys.executable, str(CHECK), path, *args],
        capture_output=True, text=True, encoding="utf-8",
    )
    Path(path).unlink()
    return p


class TestCli(unittest.TestCase):
    """The seven cases of the task specification, unchanged."""

    def test_clean_text_exits_zero(self):
        p = run("قال الوزير، ثم صمت. هذا كل شيء.")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_hard_violation_exits_one(self):
        p = run("الشمس طالعة, والنسيم عليل.")
        self.assertEqual(p.returncode, 1)
        self.assertIn("AR-TYPO-02", p.stdout)

    def test_recommendation_alone_exits_zero(self):
        p = run("قال النبي (ص) خيرا.")
        self.assertEqual(p.returncode, 0)
        self.assertIn("AR-RELIG-01", p.stdout)

    def test_output_carries_the_isnad(self):
        p = run("ثلاثمائة دينار.")
        self.assertIn("Majma", p.stdout)

    def test_preset_is_reported(self):
        p = run(PLAIN, "--preset", "news")
        self.assertIn("news", p.stdout)

    def test_unknown_preset_exits_two(self):
        p = run("نص", "--preset", "nope")
        self.assertEqual(p.returncode, 2)
        self.assertIn("news", p.stderr + p.stdout)

    def test_json_output_is_parseable(self):
        p = run("الشمس طالعة, والنسيم عليل.", "--json")
        json.loads(p.stdout)


class TestOutputSurvivesTheConsole(unittest.TestCase):
    """Printing an Arabic excerpt must not be able to kill the run.

    Measured on this machine: a child Python writing to a pipe gets
    sys.stdout.encoding == 'cp1252', and printing an Arabic character raises
    UnicodeEncodeError, which exits 1 -- indistinguishable from a hard finding.
    A checker whose evidence is Arabic cannot leave that to the console.
    """

    def test_the_arabic_excerpt_reaches_stdout_intact(self):
        p = run("الشمس طالعة, والنسيم عليل.")
        self.assertIn("طالعة", p.stdout)
        self.assertNotIn("Traceback", p.stderr)

    def test_json_keeps_the_arabic_readable(self):
        p = run("الشمس طالعة, والنسيم عليل.", "--json")
        report = json.loads(p.stdout)
        self.assertIn("طالعة", report["findings"][0]["excerpt"])


class TestExitTwoIsForEverythingThatIsNotAVerdict(unittest.TestCase):
    def test_missing_file_exits_two(self):
        p = subprocess.run(
            [sys.executable, str(CHECK), str(ROOT / "no-such-file.txt")],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 2)

    def test_a_file_that_is_not_utf8_exits_two_not_one(self):
        # A mis-encoded file is the single most likely thing to be handed to an
        # Arabic checker. Decoding it raises UnicodeDecodeError, which is a
        # ValueError and not an OSError, so a handler that only catches OSError
        # lets the traceback out and exits 1 -- reported as a hard finding.
        with tempfile.NamedTemporaryFile("wb", suffix=".txt", delete=False) as f:
            f.write("الشمس طالعة".encode("cp1256"))
            path = f.name
        try:
            p = subprocess.run([sys.executable, str(CHECK), path],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertNotIn("Traceback", p.stderr)
        finally:
            Path(path).unlink()

    def test_a_file_with_no_arabic_exits_two(self):
        # "0 hard, 0 recommendation" over a file holding no Arabic is success
        # the checker has not earned: it found nothing because there was
        # nothing of its kind to find. That is a pointing error, not a verdict.
        p = run("This file is in English.\n")
        self.assertEqual(p.returncode, 2)
        self.assertIn("no Arabic", p.stderr)

    def test_an_empty_file_exits_two_without_crashing(self):
        p = run("")
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)

    def test_a_utf8_bom_does_not_become_a_finding(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".txt", delete=False) as f:
            f.write(("﻿" + PLAIN).encode("utf-8"))
            path = f.name
        try:
            p = subprocess.run([sys.executable, str(CHECK), path],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        finally:
            Path(path).unlink()


class TestDiacriticDensity(unittest.TestCase):
    """AR-DIAC-01, the one defect the baseline showed actually occurs.

    Generated prose measured 784 and 770 diacritics per 1000 Arabic letters; a
    news dispatch measured 9. The rule fires only where the declared profile
    says diacritics are functional, and only on prose OUTSIDE citations.
    """

    def test_fully_vocalised_prose_fires(self):
        p = run(VOCALISED_PROSE, "--preset", "news")
        self.assertIn("AR-DIAC-01", p.stdout)

    def test_a_recommendation_does_not_change_the_exit_code(self):
        p = run(VOCALISED_PROSE, "--preset", "news")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_news_register_prose_does_not_fire(self):
        p = run(NEWS_PROSE, "--preset", "news")
        self.assertNotIn("AR-DIAC-01", p.stdout)

    def test_a_correctly_quoted_verse_does_not_make_clean_prose_fire(self):
        # The case that matters. Full vocalisation is REQUIRED inside a
        # citation by the same 1959-60 decision that discourages it outside.
        # Measuring the citation would fail every properly sourced religious
        # text -- the worst failure available in this project.
        text = PLAIN + " " + ORNATE_OPEN + VERSE + ORNATE_CLOSE + PLAIN_TAIL
        p = run(text, "--preset", "news")
        self.assertNotIn("AR-DIAC-01", p.stdout)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_a_correctly_quoted_hadith_does_not_make_clean_prose_fire(self):
        text = PLAIN + " «" + HADITH + "»" + PLAIN_TAIL
        p = run(text, "--preset", "news")
        self.assertNotIn("AR-DIAC-01", p.stdout)

    def test_a_text_that_is_only_a_citation_is_not_measured(self):
        # Nothing left outside the citation: the ratio has no denominator. It
        # must say so, not divide by zero and not invent a verdict.
        p = run(ORNATE_OPEN + VERSE + ORNATE_CLOSE, "--preset", "religious")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn("AR-DIAC-01", p.stdout)
        self.assertNotIn("Traceback", p.stderr)

    def test_the_religious_preset_does_not_fire_on_density(self):
        # diacritics == "citations-full": the author declared that policy.
        p = run(VOCALISED_PROSE, "--preset", "religious")
        self.assertNotIn("AR-DIAC-01", p.stdout)

    def test_the_children_preset_does_not_fire_on_density(self):
        # diacritics == "full": a vocalised reader is the point, not a defect.
        p = run(VOCALISED_PROSE, "--preset", "children")
        self.assertNotIn("AR-DIAC-01", p.stdout)

    def test_the_ratio_is_reported_even_with_no_preset(self):
        # Reported always; judged only against a declared profile.
        p = run(VOCALISED_PROSE)
        self.assertIn("per 1000", p.stdout)
        self.assertNotIn("AR-DIAC-01", p.stdout)

    def test_json_carries_the_measurement_and_the_threshold(self):
        p = run(VOCALISED_PROSE, "--preset", "news", "--json")
        d = json.loads(p.stdout)["diacritics"]
        self.assertGreater(d["per_1000"], 200)
        self.assertEqual(d["threshold"], 200)
        self.assertGreater(d["arabic_letters"], 0)

    def test_the_citation_is_excluded_from_the_denominator_too(self):
        # Stripping must remove the citation's LETTERS as well as its marks.
        # Keeping the letters would dilute the ratio and hide a real defect in
        # any text that happens to quote scripture.
        plain = run(PLAIN, "--json")
        quoted = run(PLAIN + " " + ORNATE_OPEN + VERSE + ORNATE_CLOSE, "--json")
        self.assertEqual(json.loads(plain.stdout)["diacritics"]["arabic_letters"],
                         json.loads(quoted.stdout)["diacritics"]["arabic_letters"])


class TestLengthReport(unittest.TestCase):
    def test_a_sentence_over_the_cap_is_reported(self):
        # children -> foundational -> max 15 words.
        long_one = " ".join(["كلمة"] * 20) + "."
        p = run(long_one, "--preset", "children")
        self.assertIn("20 words", p.stdout)
        self.assertIn("15", p.stdout)

    def test_no_length_report_without_a_declared_profile(self):
        long_one = " ".join(["كلمة"] * 20) + "."
        p = run(long_one)
        self.assertNotIn("over the", p.stdout)

    def test_json_length_block_matches_the_declared_audience(self):
        p = run(PLAIN, "--preset", "legal", "--json")
        length = json.loads(p.stdout)["length"]
        self.assertEqual(length["cap"], 37)          # specialized
        self.assertEqual(length["over_cap"], [])


class TestDemotedScriptRule(unittest.TestCase):
    """Ruling of 2026-09-17: AR-SCRIPT-01 reports, it no longer blocks."""

    def test_a_bare_latin_brand_reports_but_does_not_fail_the_run(self):
        text = ("تعاونت شركة "
                "Microsoft العالمية "
                "معنا.")
        p = run(text)
        self.assertIn("AR-SCRIPT-01", p.stdout)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()


sys.path.insert(0, str(ROOT / "scripts"))
import check  # noqa: E402  -- after the path insert, by necessity


class TestARatioRuleCannotBeSilentlyInert(unittest.TestCase):
    """The failure this task existed to repair, pinned so it cannot recur.

    AR-DIAC-01 shipped recorded, sourced and typed `kind: "ratio"` -- and
    nothing computed it. run_rules skips ratio rules by construction, so the
    rule was inert and every test still passed. A new ratio rule added to the
    table must therefore not be quietly skipped here: it raises, which the CLI
    turns into exit 2, a packaging fault rather than a clean verdict.
    """

    def test_an_unregistered_ratio_rule_raises_instead_of_being_skipped(self):
        rule = {"id": "AR-NEW-99", "kind": "ratio", "severity": "recommendation",
                "pattern": None, "message": "m", "isnad": "i"}
        with self.assertRaises(ValueError) as cm:
            check.ratio_findings([rule], None, {"per_1000": 500})
        self.assertIn("AR-NEW-99", str(cm.exception))

    def test_the_registered_measurement_covers_every_ratio_rule_in_the_table(self):
        rules = check.load_rules(check.RULES_PATH)
        ratio = [r["id"] for r in rules if r["kind"] == "ratio"]
        self.assertTrue(ratio, "the table no longer has a ratio rule to measure")
        for rid in ratio:
            self.assertIn(rid, check.RATIO_MEASUREMENTS)


class TestDensityMeasurementDirectly(unittest.TestCase):
    """Unit-level checks on the measurement, below the process boundary."""

    def test_a_directory_is_an_unreadable_file_not_a_verdict(self):
        p = subprocess.run([sys.executable, str(CHECK), str(ROOT)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)

    def test_the_superscript_alef_counts_as_a_diacritic(self):
        # U+0670 sits outside the tashkeel block but is a mark like the rest;
        # a range-only test would miss it, and it is common in vocalised text.
        d = check.diacritic_density("\u0647\u0670\u0630\u0627")
        self.assertEqual(1, d["diacritics"])
        self.assertEqual(3, d["arabic_letters"])

    def test_stripping_leaves_a_separator_behind(self):
        # A citation removed to nothing would fuse the words on either side.
        stripped = check.strip_citations(
            "\u0623 " + ORNATE_OPEN + VERSE + ORNATE_CLOSE + " \u0628")
        self.assertEqual(2, len(stripped.split()))

    def test_two_separate_citations_do_not_swallow_the_prose_between_them(self):
        # The negated character class is what stops one span running from the
        # close of the first quotation to the open of the second.
        middle = "\u0648\u0642\u064A\u0644"
        text = (ORNATE_OPEN + VERSE + ORNATE_CLOSE + " " + middle + " " +
                ORNATE_OPEN + VERSE + ORNATE_CLOSE)
        self.assertIn(middle, check.strip_citations(text))

    def test_a_ratio_rule_without_a_threshold_raises_rather_than_crashing(self):
        # A missing cut-off is a packaging fault: it must route to exit 2, not
        # escape as a KeyError and exit 1, which reads as a defective text.
        rule = {"id": "AR-DIAC-01", "kind": "ratio", "severity": "recommendation",
                "pattern": None, "message": "m", "isnad": "i"}
        profile = {"diacritics": "functional"}
        with self.assertRaises(ValueError):
            check.ratio_findings([rule], profile, {"per_1000": 900})


class TestTheTwoTypographyRulesCompose(unittest.TestCase):
    """The reported symptom was an exit code, so it is pinned as one.

    Before AR-TYPO-01 was widened on 2026-09-17, this sentence exited 0 with
    nothing reported: a space before a Latin comma fell between the two hard
    typography rules.
    """

    SPACED_LATIN = ("\u0627\u0644\u0634\u0631\u0643\u0629 "
                    "\u0631\u0627\u0626\u062F\u0629 , "
                    "\u0648\u0647\u064A \u0643\u0628\u064A\u0631\u0629.")
    TIGHT_LATIN = ("\u0627\u0644\u0634\u0631\u0643\u0629 "
                   "\u0631\u0627\u0626\u062F\u0629, "
                   "\u0648\u0647\u064A \u0643\u0628\u064A\u0631\u0629.")
    CORRECT = ("\u0627\u0644\u0634\u0631\u0643\u0629 "
               "\u0631\u0627\u0626\u062F\u0629\u060C "
               "\u0648\u0647\u064A \u0643\u0628\u064A\u0631\u0629.")

    def test_a_space_before_a_latin_comma_now_fails_the_run(self):
        p = run(self.SPACED_LATIN)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("AR-TYPO-01", p.stdout)
        self.assertNotIn("AR-TYPO-02", p.stdout)

    def test_removing_the_space_leaves_the_glyph_fault_behind(self):
        p = run(self.TIGHT_LATIN)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("AR-TYPO-02", p.stdout)
        self.assertNotIn("AR-TYPO-01", p.stdout)

    def test_repairing_both_faults_exits_clean(self):
        p = run(self.CORRECT)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_each_finding_carries_its_own_source(self):
        # Two faults, two rules, two isnads -- not one rule stretched over both.
        spaced = json.loads(run(self.SPACED_LATIN, "--json").stdout)["findings"]
        tight = json.loads(run(self.TIGHT_LATIN, "--json").stdout)["findings"]
        self.assertIn("Netflix", spaced[0]["isnad"])
        self.assertIn("unicodedata", tight[0]["isnad"])


# A sentence of 20 Arabic words: over the foundational cap of 15, under the
# advanced cap of 26. It is the S1 shape -- prose aimed at readers with no
# training that silently lands in the advanced band.
TWENTY_WORDS = ("الزكاة حصة صغيرة من مالك تخرجها كل سنة لمن يحتاجها من الفقراء "
                "والمساكين وابن السبيل وسائر الأصناف.")


class TestSetOverrides(unittest.TestCase):
    """`--set field=value` exists because the seven presets are seven fixed
    points in a space the engine already models as independent fields.

    Measured on 2026-09-17: no preset pairs `audience: foundational` with
    `diacritics: functional`. `children` is the only foundational preset and it
    declares `diacritics: full`, which switches AR-DIAC-01 off. So a plain-
    language text for untrained adult readers could get the right length cap or
    a vocalisation check, never both -- a GREEN scenario agent hit exactly this
    and had to run the checker twice and join the results by hand.

    `resolve()` already took an `overrides` mapping, with a documented contract
    about why unknown keys raise and values do not. Only the CLI was missing.
    The alternative -- an eighth preset -- was rejected: a preset must carry a
    genre, and a genre carries a measured verbal ratio. There is no measured
    ratio for "adult plain-language explainer" in this project's corpus, and
    inventing one would break the rule that a published number names its source
    and its count.
    """

    def test_foundational_cap_and_vocalisation_check_can_now_coexist(self):
        # The S1 scenario, end to end, in one run instead of two.
        p = run(VOCALISED_PROSE + " " + TWENTY_WORDS,
                "--preset", "children", "--set", "diacritics=functional")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        # The foundational cap (15) still applies: the 20-word sentence is over.
        self.assertIn("15", p.stdout)
        # And AR-DIAC-01 now judges, which `children` alone would not do.
        self.assertIn("AR-DIAC-01", p.stdout)

    def test_children_alone_does_not_judge_vocalisation(self):
        # The control. If this ever starts reporting AR-DIAC-01, the test above
        # proves nothing, because it would pass without the override.
        p = run(VOCALISED_PROSE + " " + TWENTY_WORDS, "--preset", "children")
        self.assertNotIn("AR-DIAC-01", p.stdout)

    def test_set_without_preset_exits_two(self):
        # Overriding nothing is a usage error, not an empty override: there is
        # no profile to override, so every other field would be unset.
        p = run(PLAIN, "--set", "diacritics=functional")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("--preset", p.stderr + p.stdout)

    def test_malformed_set_exits_two(self):
        p = run(PLAIN, "--preset", "news", "--set", "diacritics")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)

    def test_unknown_field_exits_two_and_names_the_valid_fields(self):
        # The typo `audiance` must not leave `audience` at its preset value
        # while looking as if it had been set.
        p = run(PLAIN, "--preset", "news", "--set", "audiance=foundational")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("audience", p.stderr + p.stdout)

    def test_overrides_are_repeatable(self):
        p = run(PLAIN, "--preset", "news",
                "--set", "audience=foundational", "--set", "diacritics=full",
                "--json")
        prof = json.loads(p.stdout)["profile"]
        self.assertEqual(prof["audience"], "foundational")
        self.assertEqual(prof["diacritics"], "full")

    def test_json_records_the_overrides_next_to_the_preset_name(self):
        # Without this, a JSON consumer reads `preset: news` beside a profile
        # that is not what `news` means, and cannot tell why.
        p = run(PLAIN, "--preset", "news", "--set", "audience=foundational", "--json")
        report = json.loads(p.stdout)
        self.assertEqual(report["preset"], "news")
        self.assertEqual(report["overrides"], {"audience": "foundational"})

    def test_a_boolean_field_stays_a_boolean(self):
        # `italics` is the one non-string field. Passing the string "true"
        # through would store a truthy string that is not True -- latent today,
        # because no rule reads the field, and a real defect the day one does.
        p = run(PLAIN, "--preset", "news", "--set", "italics=true", "--json")
        self.assertIs(json.loads(p.stdout)["profile"]["italics"], True)

    def test_a_nonboolean_value_for_a_boolean_field_exits_two(self):
        p = run(PLAIN, "--preset", "news", "--set", "italics=maybe")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
