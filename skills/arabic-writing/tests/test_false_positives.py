# -*- coding: utf-8 -*-
"""A false-positive budget for the hard rules, measured on published prose.

Why this test exists
--------------------
The checker's only enforcement is its exit code, and it exits non-zero on a
violated hard rule. The 2026-09-17 RED baseline ran five scenarios through
agents without this skill and no hard rule fired on any of the four generated
texts: the model already wrote ornate parentheses around its verse and used no
Latin punctuation. So the hard rules will spend their working life over
human-written, legacy, translated and CMS-pasted Arabic that somebody already
believes is finished. On that material a false positive costs far more than a
missed error, because it blocks a build over text that was correct.

The French sibling of this skill shipped two typography rules that reported
spaces absent from the source. The same failure has already happened here:
AR-RELIG-02 fired on two correctly quoted Qur'anic verses whose adjacent close
and open formed a reversed ornate pair. This test is the standing guard.

The corpus
----------
`fixtures/clean/` holds twelve excerpts of published Arabic drawn from BAREC
(CC BY-SA 4.0), spread over its two edited-prose sources (Hindawi, literature
and essays; Wikipedia, encyclopedia), three domains and three readability
bands. Each file opens with `#` provenance lines naming corpus, source and
document id; they are stripped before checking. Fixtures were selected for
diversity, never by running the rules over candidates and keeping the quiet
ones -- that would make this measurement circular.

The denominator
---------------
`segment.sentences()`, not `text.count(".")`. It is the project's own
segmenter, measured against BAREC's human annotators at 87.8% boundary
precision, so the budget is stated in the same unit the rest of the skill
reasons about. A dot count is not a sentence count in Arabic: it sees nothing
of a clause closed by the question or exclamation mark, and it counts the dot
inside a decimal, an ellipsis and an abbreviation, all of which the segmenter
already knows to leave alone. On this corpus the two totals happen to land
close together (143 against 139), but per file they do not -- fixture 03
carries 6 dots against 22 annotated sentences -- and the dot count would drift
on any input richer in numerals. Both run well under BAREC's 254 human
boundaries, which shrinks the denominator and so tightens the budget: the
error is in the safe direction.

Fixtures are single flowing paragraphs, one per file, because that is how the
underlying documents read. Reconstructing them one annotated sentence per line
was tried and rejected: it makes a line start of every boundary, and BAREC
annotators sometimes cut between a full stop and its closing guillemet, so six
of seven AR-TYPO-03 reports under that layout were artifacts of the
reconstruction rather than defects of the text. Line-anchored AR-TYPO-03 is
therefore only lightly exercised here; that limit is real and recorded.

Measured, 2026-09-17, over the committed fixtures
-------------------------------------------------
1 hard finding / 143 sentences = 0.007, against a budget of 0.02.
The one finding is a TRUE positive: AR-TYPO-01 on `...المحددة ، ويقال` in the
Arabic Wikipedia article on engineering -- a space before the Arabic comma,
which no consulted source permits. It is kept rather than edited away: real
published prose carries a low density of real errors, and a budget that only
ever sees flawless text measures nothing. Two earlier fixtures were swapped
out for the same defect before it became clear the defect is endemic to
crowd-edited Wikipedia, not particular to one article. A third was swapped for
an unrelated reason: it turned out to be a template-generated geography stub,
which is not the edited prose this corpus is supposed to represent.

Measured over the whole 443-document Hindawi + Wikipedia population (11,888
sentences), for context that twelve fixtures cannot carry:
  AR-TYPO-01   17 findings, all Wikipedia, none in 8,215 sentences of
               professionally typeset Hindawi. Every one a real space before
               an Arabic comma or exclamation mark. Precision 17/17.
  AR-ORTH-01   17 findings, every one of them false. All seventeen are the
               joined spelling of a hundreds numeral -- thalathmi'a,
               arba'mi'a, khamsmi'a -- in ordinary published prose from a
               professional publisher and from Wikipedia. Counted across all
               thirty BAREC sources, the joined form outnumbers the detached
               one 60 to 3: 95% of published usage. The rule's isnad is a
               Cairo Academy decision with four motives attached, which is an
               argued reform, not the unanimity `hard` requires (see the
               severity definitions in scripts/rules.py). Measured precision
               0/17. This rule should be demoted to `recommendation`; the
               pattern itself is correct and needs no narrowing. Not changed
               here because assets/rules.json belongs to another task.
  AR-TYPO-02, AR-TYPO-03, AR-RELIG-02   no findings.

AR-TYPO-03 is line-anchored and the fixtures are single paragraphs, so the
population sweep above was also re-run with one annotated sentence per line.
It reported 7: six were a closing guillemet that a BAREC annotator had cut
away from its own full stop, which is an artifact of that layout and not of
any published text, and the seventh was a real stray `.` before a `،` in the
Arabic Wikipedia article on the history of Kuwait.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from rules import load_rules, run_rules            # noqa: E402
from segment import sentences, word_count          # noqa: E402

CLEAN = Path(__file__).resolve().parent / "fixtures" / "clean"

# At most 2 hard findings per 100 sentences of published prose. Raising this is
# not a way to make a failure go away: a hard rule that fires on correct text
# has to be narrowed, and a fixture that carries a real error has to be
# replaced. The number is the contract, not the dial.
BUDGET = 0.02

MIN_WORDS = 200
MIN_FILES = 10


def _body(path):
    """The fixture's text, with its `#` provenance lines stripped."""
    raw = path.read_text(encoding="utf-8")
    return "\n".join(l for l in raw.split("\n") if not l.startswith("#"))


def _printable(s):
    """`s`, made safe for whatever stdout this run happens to have.

    A default Windows console is cp1252, and printing an Arabic excerpt to it
    raises UnicodeEncodeError -- which unittest reports as a failing test, so a
    diagnostic line would turn a passing budget into a red suite. Measured: the
    excerpt below crashes under `python -m unittest` with PYTHONIOENCODING
    unset. Escaping only what the terminal cannot render keeps the Arabic
    legible wherever it can be, and keeps the finding locatable where it
    cannot.
    """
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    return s.encode(enc, "backslashreplace").decode(enc, "replace")


class TestCleanCorpus(unittest.TestCase):
    """The measurement is only worth its denominator if the corpus is intact."""

    def test_corpus_contract(self):
        files = sorted(CLEAN.glob("*.txt"))
        self.assertGreaterEqual(len(files), MIN_FILES,
                                "need at least %d clean fixtures" % MIN_FILES)
        for f in files:
            head = f.read_text(encoding="utf-8").split("\n")[0]
            self.assertTrue(head.startswith("#"),
                            "%s has no provenance line" % f.name)
            self.assertIn("BAREC", head,
                          "%s does not name the corpus it came from" % f.name)
            self.assertIn("Document:", head,
                          "%s does not name its source document" % f.name)
            n = word_count(_body(f))
            self.assertGreaterEqual(n, MIN_WORDS,
                                    "%s has %d Arabic words, need %d"
                                    % (f.name, n, MIN_WORDS))

    def test_sources_and_bands_are_spread(self):
        """Ten near-identical Wikipedia stubs would meet the budget and prove
        nothing. Require both sources and more than one readability band."""
        heads = [f.read_text(encoding="utf-8").split("\n")[0]
                 for f in sorted(CLEAN.glob("*.txt"))]
        for src in ("Hindawi", "Wikipedia"):
            self.assertTrue(any("Source: %s" % src in h for h in heads),
                            "no fixture from %s" % src)
        bands = {h.split("Readability_Level_3:")[1].strip()[0]
                 for h in heads if "Readability_Level_3:" in h}
        self.assertGreaterEqual(len(bands), 2,
                                "fixtures span only band(s) %s" % sorted(bands))


class TestFalsePositives(unittest.TestCase):
    def test_hard_rules_stay_within_budget(self):
        rules = load_rules(ROOT / "assets" / "rules.json")
        files = sorted(CLEAN.glob("*.txt"))
        self.assertGreaterEqual(len(files), MIN_FILES,
                                "need at least %d clean fixtures" % MIN_FILES)
        total_sentences = hard = 0
        offenders = {}
        detail = []
        for f in files:
            text = _body(f)
            # max(1, ...) so that a fixture the segmenter cannot cut still
            # contributes a denominator rather than dividing by zero.
            total_sentences += max(1, len(sentences(text)))
            for finding in run_rules(text, rules, severities=["hard"]):
                hard += 1
                offenders[finding["id"]] = offenders.get(finding["id"], 0) + 1
                detail.append("%s:%d:%d %s: %s"
                              % (f.name, finding["line"], finding["col"],
                                 finding["id"], finding["excerpt"]))
        rate = hard / total_sentences
        print("\nfalse-positive rate: %d hard / %d sentences = %.3f  %s"
              % (hard, total_sentences, rate, offenders))
        for d in detail:
            print("  " + _printable(d))
        self.assertLessEqual(rate, BUDGET, "offenders: %s" % offenders)


if __name__ == "__main__":
    unittest.main()
