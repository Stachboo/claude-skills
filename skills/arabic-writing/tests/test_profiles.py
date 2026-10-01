# -*- coding: utf-8 -*-
"""Unit tests for preset resolution.

The user makes ONE choice -- a preset name -- and every other setting follows
from it. These tests pin that contract: the preset list, the fields a resolved
profile carries, the audience each preset targets, and the fact that an
explicit override still wins for the expert who wants to tune one field.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from profiles import resolve, targets, PRESET_NAMES


class TestProfiles(unittest.TestCase):
    def test_preset_names_are_stable(self):
        self.assertEqual(
            set(PRESET_NAMES),
            {"news", "magazine", "literary", "legal", "reference", "religious", "children"},
        )

    def test_one_word_resolves_a_full_profile(self):
        p = resolve("news")
        for key in ("school", "digits", "italics", "diacritics", "audience", "genre"):
            self.assertIn(key, p)

    def test_news_targets_advanced_audience(self):
        self.assertEqual(resolve("news")["audience"], "advanced")

    def test_children_targets_foundational(self):
        self.assertEqual(resolve("children")["audience"], "foundational")

    def test_legal_targets_specialized(self):
        self.assertEqual(resolve("legal")["audience"], "specialized")

    def test_religious_requires_full_diacritics_on_citations(self):
        self.assertEqual(resolve("religious")["diacritics"], "citations-full")

    def test_override_wins_over_preset(self):
        self.assertEqual(resolve("news", {"digits": "arabic-indic"})["digits"], "arabic-indic")

    def test_unknown_preset_raises_with_the_list(self):
        with self.assertRaises(ValueError) as ctx:
            resolve("nope")
        self.assertIn("news", str(ctx.exception))


class TestOverrideSafety(unittest.TestCase):
    """A mistyped override must not pass silently.

    `resolve("news", {"audiance": "advanced"})` would otherwise add a junk key
    and leave the real `audience` at its preset value -- silently changing which
    sentence-length cap applies. The profile keys are a closed set, so rejecting
    an unknown one is free and deterministic.
    """

    def test_unknown_override_key_raises_naming_the_key_and_the_valid_ones(self):
        with self.assertRaises(ValueError) as ctx:
            resolve("news", {"audiance": "advanced"})
        message = str(ctx.exception)
        self.assertIn("audiance", message)
        self.assertIn("audience", message)

    def test_resolving_twice_is_not_contaminated_by_a_mutated_result(self):
        first = resolve("news")
        first["audience"] = "foundational"
        self.assertEqual(resolve("news")["audience"], "advanced")


class TestTargets(unittest.TestCase):
    def test_advanced_sentence_band(self):
        t = targets("advanced", "news")
        self.assertEqual(t["sentence_words"]["p25"], 7)
        self.assertEqual(t["sentence_words"]["p75"], 20)
        self.assertEqual(t["sentence_words"]["max"], 26)

    def test_foundational_is_shorter_than_specialized(self):
        self.assertLess(
            targets("foundational", "children")["sentence_words"]["max"],
            targets("specialized", "legal")["sentence_words"]["max"],
        )

    def test_news_is_mostly_verbal(self):
        self.assertGreaterEqual(targets("advanced", "news")["verbal_ratio"], 0.6)

    def test_legal_is_mostly_nominal(self):
        self.assertLessEqual(targets("specialized", "legal")["verbal_ratio"], 0.5)


class TestTargetsEdges(unittest.TestCase):
    """The audience/genre asymmetry, and the nested band the caller gets back."""

    def test_unknown_audience_raises_with_the_list(self):
        # The audience set is closed by registers.json and drives a real cap,
        # so an unmatched audience can only be a mistake.
        with self.assertRaises(ValueError) as ctx:
            targets("intermediate", "news")
        message = str(ctx.exception)
        self.assertIn("intermediate", message)
        self.assertIn("advanced", message)

    def test_unknown_genre_yields_no_ratio_rather_than_raising(self):
        # The genre space is open: an author may declare a genre nobody has
        # measured. The key is still present, so a caller can tell "unmeasured"
        # from a measured value -- and must test `is None`, since 0.0 is falsy.
        t = targets("advanced", "screenplay")
        self.assertIn("verbal_ratio", t)
        self.assertIsNone(t["verbal_ratio"])

    def test_mutating_a_returned_band_does_not_reach_the_next_call(self):
        # The band is nested, so a shallow copy would hand out the module's own
        # dict and let one caller rewrite every later caller's cap.
        first = targets("advanced", "news")
        first["sentence_words"]["max"] = 999
        self.assertEqual(targets("advanced", "news")["sentence_words"]["max"], 26)


if __name__ == "__main__":
    unittest.main()
