import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from rules import load_rules, run_rules


class TestRuleTable(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def test_every_rule_has_required_fields(self):
        for r in self.rules:
            for field in ("id", "severity", "pattern", "message", "isnad"):
                self.assertIn(field, r, f"rule {r.get('id')} lacks {field}")

    def test_severity_is_one_of_three(self):
        for r in self.rules:
            self.assertIn(r["severity"], ("hard", "recommendation", "divergence"))

    def test_every_rule_carries_a_non_empty_isnad(self):
        for r in self.rules:
            self.assertTrue(r["isnad"].strip(), f"rule {r['id']} has an empty isnad")

    def test_rule_ids_are_unique(self):
        ids = [r["id"] for r in self.rules]
        self.assertEqual(len(ids), len(set(ids)))


class TestHardRules(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def fire(self, text):
        return {f["id"] for f in run_rules(text, self.rules)}

    def test_typo01_space_before_arabic_comma(self):
        self.assertIn("AR-TYPO-01", self.fire("قال الوزير ، ثم صمت"))

    def test_typo01_clean_text_does_not_fire(self):
        self.assertNotIn("AR-TYPO-01", self.fire("قال الوزير، ثم صمت"))

    def test_typo02_latin_comma_between_arabic(self):
        self.assertIn("AR-TYPO-02", self.fire("الشمس طالعة, والنسيم عليل"))

    def test_typo02_arabic_comma_does_not_fire(self):
        self.assertNotIn("AR-TYPO-02", self.fire("الشمس طالعة، والنسيم عليل"))

    def test_orth01_joined_hundreds(self):
        self.assertIn("AR-ORTH-01", self.fire("ثلاثمائة دينار"))

    def test_orth01_detached_hundreds_clean(self):
        self.assertNotIn("AR-ORTH-01", self.fire("ثلاث مئة دينار"))

    def test_script01_latin_run_inside_arabic(self):
        self.assertIn("AR-SCRIPT-01", self.fire("روى عن Umm Salama رضي الله عنها"))

    def test_script01_parenthesised_latin_is_allowed(self):
        self.assertNotIn("AR-SCRIPT-01", self.fire("مدينة بوردو (Bordeaux) الفرنسية"))

    def test_relig02_ornate_parens_reversed(self):
        self.assertIn("AR-RELIG-02", self.fire("﴾إن الله مع الصابرين﴿"))

    def test_relig02_ornate_parens_correct(self):
        self.assertNotIn("AR-RELIG-02", self.fire("﴿إن الله مع الصابرين﴾"))

    def test_relig01_is_a_recommendation_not_hard(self):
        r = [x for x in self.rules if x["id"] == "AR-RELIG-01"][0]
        self.assertEqual(r["severity"], "recommendation")


# ---------------------------------------------------------------------------
# Everything below is additional to the task specification. It exists because
# the RED baseline (tests/baseline/results-red.md) established that on this
# project a false positive costs far more than a missed error: these rules run
# over text somebody already believes is correct. Each case below is a defect
# found by reading a pattern against real Arabic rather than against the
# example strings of the specification, and each one failed before the pattern
# was repaired.
#
# Ornate parentheses are written as escapes, never as literals: U+FD3E is named
# ORNATE LEFT PARENTHESIS but is General_Category Pe (a closer), so a literal in
# the source reads as the opposite of what it does.
# ---------------------------------------------------------------------------

ORNATE_OPEN = "﴿"   # Ps, despite being named ORNATE RIGHT PARENTHESIS
ORNATE_CLOSE = "﴾"  # Pe, despite being named ORNATE LEFT PARENTHESIS


class TestRuleKind(unittest.TestCase):
    """A rule that is not a regex must say so, and must never be compiled."""

    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def test_every_rule_declares_a_kind(self):
        for r in self.rules:
            self.assertIn(r["kind"], ("pattern", "ratio", "consistency"), r["id"])

    def test_pattern_rules_have_a_non_empty_pattern(self):
        for r in self.rules:
            if r["kind"] == "pattern":
                self.assertTrue(r["pattern"], r["id"])

    def test_non_pattern_rules_carry_a_null_pattern_not_an_empty_one(self):
        # An empty regex matches at every position. Storing "" would make such a
        # rule fire once per character; storing null makes re.compile refuse and
        # makes load_rules reject it loudly.
        for r in self.rules:
            if r["kind"] != "pattern":
                self.assertIsNone(r["pattern"], r["id"])

    def test_diac01_is_declared_a_ratio_rule(self):
        r = [x for x in self.rules if x["id"] == "AR-DIAC-01"][0]
        self.assertEqual(r["kind"], "ratio")
        self.assertEqual(r["severity"], "recommendation")

    def test_run_rules_does_not_evaluate_ratio_rules(self):
        # AR-DIAC-01 is a ratio over the whole text and must exclude Qur'anic
        # and hadith citations before measuring. run_rules is a pattern matcher;
        # it leaves the rule to the later measurement pass rather than guess.
        heavy = "قَالَ الْوَزِيرُ إِنَّ الْأَمْرَ قَدِ انْتَهَى وَلَا رَجْعَةَ فِيهِ."
        self.assertNotIn("AR-DIAC-01", {f["id"] for f in run_rules(heavy, self.rules)})

    def _write_temp_table(self, rule):
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"version": "test", "rules": [rule]}, fh)
        return path

    def test_load_rules_refuses_an_empty_pattern(self):
        import os
        path = self._write_temp_table({
            "id": "X", "kind": "pattern", "severity": "hard", "pattern": "",
            "message": "m", "isnad": "i"})
        try:
            with self.assertRaises(ValueError):
                load_rules(path)
        finally:
            os.unlink(path)

    def test_load_rules_refuses_an_unknown_severity(self):
        # run_rules filters on severity, so a typo would silently never fire.
        import os
        path = self._write_temp_table({
            "id": "X", "kind": "pattern", "severity": "harde", "pattern": "a",
            "message": "m", "isnad": "i"})
        try:
            with self.assertRaises(ValueError):
                load_rules(path)
        finally:
            os.unlink(path)

    def test_load_rules_refuses_a_pattern_on_a_ratio_rule(self):
        import os
        path = self._write_temp_table({
            "id": "X", "kind": "ratio", "severity": "recommendation",
            "pattern": "a", "message": "m", "isnad": "i"})
        try:
            with self.assertRaises(ValueError):
                load_rules(path)
        finally:
            os.unlink(path)


# Correct Arabic that earlier versions of these patterns flagged. Not one of
# these may produce a single hard finding.
CLEAN = [
    ("plain prose",
     "قال الوزير، ثم صمت طويلًا؛ ولم يجب عن السؤال. لا أحد يدري!"),
    ("two correctly quoted verses in one paragraph",
     "قال تعالى " + ORNATE_OPEN + "إن الله مع الصابرين" + ORNATE_CLOSE +
     " ثم قال " + ORNATE_OPEN + "واتقوا الله لعلكم تفلحون" + ORNATE_CLOSE +
     " في السورة نفسها."),
    ("a verse closed against a full stop, then a second verse",
     "ورد " + ORNATE_OPEN + "إن مع العسر يسرا" + ORNATE_CLOSE + ". ثم جاء " +
     ORNATE_OPEN + "فإن مع العسر يسرا" + ORNATE_CLOSE + " بعدها مباشرة."),
    ("a bare domain is a URL, not a name to transliterate",
     "زر الموقع example.com للمزيد من التفاصيل."),
    ("a full URL inside Arabic prose",
     "نشر النص على https://www.example.com/page.html أمس."),
    ("a markdown image is not an exclamation mark",
     "انظر الشكل ![صورة توضيحية](img/a.png) لفهم الفكرة."),
    ("an elision opening a line is legitimate",
     "قال الراوي ما نصه\n... ثم انصرف القوم دون جواب."),
    ("the em dash parenthetical, attested in Zaki 1912 and Harun",
     "أعلن أحمد الشربيني – مؤلف هذا الكتاب – أنه سينشر الطبعة الثانية."),
    ("hundreds written detached",
     "دفع ثلاث مئة وخمسة وأربعين دينارا، ثم ثماني مئة أخرى."),
    ("a markdown image opening a line is not a stranded exclamation mark",
     "انظر الشكل التالي\n![صورة](img/a.png)\nيشرح الفكرة."),
    ("a Latin form in parentheses after the Arabic name",
     "ولد في مدينة بوردو (Bordeaux) الفرنسية سنة ألف وتسع مئة."),
    ("vocalised prose, correctly punctuated",
     "قَالَ الْوَزِيرُ، ثُمَّ صَمَتَ؛ وَلَمْ يُجِبْ."),
    ("the prayer written in full with the ligature",
     "قال النبي ﷺ: «إنما الأعمال بالنيات»، رواه البخاري."),
]


class TestNoFalsePositivesOnCorrectProse(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def test_clean_corpus_produces_no_hard_finding(self):
        for label, text in CLEAN:
            with self.subTest(label):
                found = run_rules(text, self.rules, severities=["hard"])
                self.assertEqual(
                    [], found,
                    "%s: %r" % (label, [(f["id"], f["excerpt"]) for f in found]))

    def test_latin_comma_rule_ignores_arabic_indic_decimals(self):
        # "١,٥" is a number separator in legacy Arabic text, not sentence
        # punctuation; flagging it would be a false positive. This is why the
        # left-hand class of AR-TYPO-02 takes letters and marks but not digits.
        found = {f["id"] for f in run_rules("بلغ السعر ١,٥ مليون دينار", self.rules)}
        self.assertNotIn("AR-TYPO-02", found)


class TestVocalisedTextStillCaught(unittest.TestCase):
    """The baseline measured generated prose at 784 diacritics per 1000 letters.
    A pattern anchored on bare letters misses every defect in such a text,
    because the character before the space is a mark, not a letter."""

    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def fire(self, text):
        return {f["id"] for f in run_rules(text, self.rules)}

    def test_typo01_fires_after_a_diacritic(self):
        self.assertIn("AR-TYPO-01", self.fire("قَالَ الْوَزِيرُ ، ثُمَّ صَمَتَ"))

    def test_typo02_fires_after_a_diacritic(self):
        self.assertIn("AR-TYPO-02", self.fire("الشَّمْسُ طَالِعَةٌ, وَالنَّسِيمُ عَلِيلٌ"))

    def test_script01_fires_after_a_diacritic(self):
        self.assertIn("AR-SCRIPT-01", self.fire("رَوَى عَنْ Umm Salama رَضِيَ اللهُ عَنْهَا"))


class TestRemainingHardRules(unittest.TestCase):
    """AR-TYPO-03 carries no test in the specification; these supply one."""

    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def fire(self, text):
        return {f["id"] for f in run_rules(text, self.rules)}

    def test_typo03_mark_opening_a_line(self):
        self.assertIn("AR-TYPO-03", self.fire("قال الوزير\n، ثم صمت طويلا"))

    def test_typo03_closing_guillemet_opening_a_line(self):
        self.assertIn("AR-TYPO-03", self.fire("«إنما الأعمال\n» قال الراوي"))

    def test_typo03_clean_lines_do_not_fire(self):
        self.assertNotIn("AR-TYPO-03", self.fire("قال الوزير\nثم صمت طويلا"))

    def test_relig01_abbreviated_prayer(self):
        self.assertIn("AR-RELIG-01", self.fire("قال النبي (ص) في الحديث"))
        self.assertIn("AR-RELIG-01", self.fire("قال النبي (صلعم) في الحديث"))

    def test_relig01_page_citation_does_not_fire(self):
        self.assertNotIn("AR-RELIG-01", self.fire("انظر الكتاب (ص ١٢) للتفصيل"))

    def test_script01_flags_a_bare_latin_brand_between_arabic_words(self):
        # Intended behaviour, not an accident: the Cairo Academy decision cited
        # in the isnad asks for the Arabic form, with the Latin in parentheses.
        self.assertIn("AR-SCRIPT-01", self.fire("تعاونت شركة Microsoft العالمية معنا"))


class TestFindingShape(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def test_finding_reports_line_and_column_and_carries_its_isnad(self):
        text = "سطر أول\nسطر ثان\nقال الوزير ، ثم صمت"
        found = [f for f in run_rules(text, self.rules) if f["id"] == "AR-TYPO-01"]
        self.assertEqual(1, len(found))
        self.assertEqual(3, found[0]["line"])
        # col is 1-based and points at the first character of the match, which
        # for AR-TYPO-01 is the Arabic letter just before the offending space.
        third_line = text.split("\n")[2]
        self.assertEqual("ر", third_line[found[0]["col"] - 1])
        self.assertTrue(found[0]["isnad"].strip())

    def test_severity_filter_excludes_recommendations(self):
        text = "قال النبي (ص) وقال الوزير ، ثم صمت"
        ids = {f["id"] for f in run_rules(text, self.rules, severities=["hard"])}
        self.assertIn("AR-TYPO-01", ids)
        self.assertNotIn("AR-RELIG-01", ids)

    def test_an_empty_severity_list_reports_nothing(self):
        # Not the same as None. A filter that turns "report nothing" into
        # "report everything" fails in the direction that breaks a build.
        text = "قال النبي (ص) وقال الوزير ، ثم صمت"
        self.assertNotEqual([], run_rules(text, self.rules, severities=None))
        self.assertEqual([], run_rules(text, self.rules, severities=[]))

    def test_findings_are_sorted_by_position(self):
        text = "قال الوزير ، ثم صمت\nالشمس طالعة, والنسيم عليل"
        found = run_rules(text, self.rules)
        self.assertEqual(sorted(found, key=lambda f: (f["line"], f["col"])), found)


class TestRulingsOf20260917(unittest.TestCase):
    """Three rulings on the table, pinned so a later edit cannot undo them.

    All three are judgements, not transmissions, and each is recorded in its
    rule's own isnad or note. The tests exist because a severity is one word in
    a JSON file: without them, a hand edit that made AR-SCRIPT-01 or AR-ORTH-01
    hard again, or that dropped the diacritic threshold, would pass every other
    test in this file.

    The two demotions rest on different grounds, and the difference is the
    lesson. AR-SCRIPT-01 failed on reasoning: the case it was written for is
    not mechanically distinguishable from a legitimate one. AR-ORTH-01 failed
    on measurement: its source is excellent and nobody follows it. A sourced
    rule and an observed rule are not the same thing, and `hard` needs both.
    """

    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def test_exactly_four_rules_are_hard(self):
        # Four, down from six. `hard` means unanimous AND decidable without
        # context. AR-SCRIPT-01 is neither; AR-ORTH-01 is decidable but not
        # unanimous -- BAREC has the form it blocks at 60 against 3.
        hard = sorted(r["id"] for r in self.rules if r["severity"] == "hard")
        self.assertEqual(
            ["AR-RELIG-02", "AR-TYPO-01", "AR-TYPO-02", "AR-TYPO-03"], hard)

    def test_orth01_is_a_recommendation_not_hard(self):
        r = [x for x in self.rules if x["id"] == "AR-ORTH-01"][0]
        self.assertEqual("recommendation", r["severity"])

    def test_orth01_still_reports_with_its_isnad(self):
        # Demoted, not deleted. The Academy's preference is real and worth
        # surfacing; it just no longer fails a build.
        text = "ثلاثمائة دينار"
        found = [f for f in run_rules(text, self.rules) if f["id"] == "AR-ORTH-01"]
        self.assertEqual(1, len(found))
        self.assertIn("Majma", found[0]["isnad"])
        self.assertEqual([], run_rules(text, self.rules, severities=["hard"]))

    def test_orth01_records_the_measurement_that_demoted_it(self):
        # The count, not just the judgement: a later reader must be able to see
        # WHY, and re-run it. This is the rule that proved a good source is not
        # sufficient evidence for a hard rule.
        r = [x for x in self.rules if x["id"] == "AR-ORTH-01"][0]
        self.assertIn("precision 0.00", r["isnad"])
        self.assertIn("60 to 3", r["isnad"])

    def test_typo01_records_its_deferred_left_hand_gap(self):
        # Measured and NOT fixed in the same change as the right-hand class.
        # Recorded with its number so the next reader finds it.
        r = [x for x in self.rules if x["id"] == "AR-TYPO-01"][0]
        self.assertIn("DEFERRED", r["note"])
        self.assertIn("0.62", r["note"])

    def test_script01_is_a_recommendation_not_hard(self):
        r = [x for x in self.rules if x["id"] == "AR-SCRIPT-01"][0]
        self.assertEqual("recommendation", r["severity"])

    def test_script01_still_reports(self):
        # Demoted, not deleted. A bare Latin brand is still worth telling the
        # author about; it just no longer fails the build.
        text = ("\u062A\u0639\u0627\u0648\u0646\u062A \u0634\u0631\u0643\u0629 "
                "Microsoft \u0627\u0644\u0639\u0627\u0644\u0645\u064A\u0629 "
                "\u0645\u0639\u0646\u0627")
        self.assertIn("AR-SCRIPT-01", {f["id"] for f in run_rules(text, self.rules)})
        self.assertEqual([], run_rules(text, self.rules, severities=["hard"]))

    def test_script01_records_why_it_was_demoted(self):
        r = [x for x in self.rules if x["id"] == "AR-SCRIPT-01"][0]
        self.assertIn("Demoted from hard to recommendation", r["isnad"])

    def test_diac01_carries_a_threshold_the_measurement_pass_can_read(self):
        # The number lives in the table, not in a code comment, so that the
        # reasoning travels with the rule it governs.
        r = [x for x in self.rules if x["id"] == "AR-DIAC-01"][0]
        self.assertEqual(200, r["threshold"]["diacritics_per_1000_letters"])

    def test_the_diacritic_threshold_is_marked_provisional(self):
        # It is inferred from measurement, not transmitted from a source. It is
        # the one figure in this table with no isnad of its own, and saying so
        # is the difference between a calibrated claim and a fabricated one.
        r = [x for x in self.rules if x["id"] == "AR-DIAC-01"][0]
        self.assertEqual("provisional", r["threshold"]["status"])
        self.assertIn("PROVISIONAL", r["note"])


class TestSpaceBeforeAMarkIsGlyphAgnostic(unittest.TestCase):
    """AR-TYPO-01 is a rule about SPACING, and its source says nothing about
    which comma.

    Widened on 2026-09-17. Before that, a space before a LATIN comma escaped
    both hard typography rules and the text exited clean: AR-TYPO-01 wanted an
    Arabic mark after the space, AR-TYPO-02 wanted the Latin mark adjacent, and
    the case fell between them. The rule's scope had been narrower than its own
    isnad -- a source whose coverage was not being used, which is the opposite
    of the unsourced rule this table guards against.
    """

    # "al-sharika ra'ida , wa-hiya kabira." -- the case that exposed the gap.
    SPACED_LATIN = ("\u0627\u0644\u0634\u0631\u0643\u0629 "
                    "\u0631\u0627\u0626\u062F\u0629 , "
                    "\u0648\u0647\u064A \u0643\u0628\u064A\u0631\u0629.")
    # The same sentence with the space removed: one fault left, not zero.
    TIGHT_LATIN = ("\u0627\u0644\u0634\u0631\u0643\u0629 "
                   "\u0631\u0627\u0626\u062F\u0629, "
                   "\u0648\u0647\u064A \u0643\u0628\u064A\u0631\u0629.")
    # Both faults repaired: Arabic comma, no space before it.
    CORRECT = ("\u0627\u0644\u0634\u0631\u0643\u0629 "
               "\u0631\u0627\u0626\u062F\u0629\u060C "
               "\u0648\u0647\u064A \u0643\u0628\u064A\u0631\u0629.")

    def setUp(self):
        self.rules = load_rules(ROOT / "assets" / "rules.json")

    def fire(self, text):
        return {f["id"] for f in run_rules(text, self.rules, severities=["hard"])}

    def test_the_two_rules_compose_across_the_repair_sequence(self):
        # The sequence the widening exists to produce: two faults, two
        # findings, each carrying its own source, and only then silence.
        self.assertEqual({"AR-TYPO-01"}, self.fire(self.SPACED_LATIN))
        self.assertEqual({"AR-TYPO-02"}, self.fire(self.TIGHT_LATIN))
        self.assertEqual(set(), self.fire(self.CORRECT))

    def test_a_space_before_a_latin_semicolon_or_question_mark_fires(self):
        for mark in (";", "?"):
            with self.subTest(mark):
                text = "\u0627\u0644\u0634\u0631\u0643\u0629 \u0631\u0627\u0626\u062F\u0629 %s \u0648\u0647\u064A" % mark
                self.assertIn("AR-TYPO-01", self.fire(text))

    def test_the_arabic_marks_still_fire(self):
        # The widening adds glyphs; it must not have dropped any.
        for mark in ("\u060C", "\u061B", "\u061F", "!"):
            with self.subTest(mark):
                text = "\u0642\u0627\u0644 \u0627\u0644\u0648\u0632\u064A\u0631 %s \u062B\u0645" % mark
                self.assertIn("AR-TYPO-01", self.fire(text))

    def test_a_markdown_image_keeps_its_guard(self):
        # '!' is the one mark shared by both scripts that can legitimately open
        # a Markdown image, which is why it stays outside the widened class.
        text = ("\u0627\u0646\u0638\u0631 \u0627\u0644\u0634\u0643\u0644 "
                "![\u0635\u0648\u0631\u0629](img/a.png) "
                "\u0644\u0641\u0647\u0645 \u0627\u0644\u0641\u0643\u0631\u0629.")
        self.assertNotIn("AR-TYPO-01", self.fire(text))

    def test_the_widening_records_its_reason(self):
        r = [x for x in self.rules if x["id"] == "AR-TYPO-01"][0]
        self.assertIn("glyph-agnostic", r["note"])
