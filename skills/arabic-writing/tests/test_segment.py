# -*- coding: utf-8 -*-
"""Unit tests for the segmenter, plus the BAREC agreement measurement.

The unit tests are self-contained. The agreement figures published in
references/registers.md come from a corpus this repository does not ship:

    corpus : CAMeL-Lab/BAREC-Corpus-v1.0  (HuggingFace)
    files  : data/dev-00000-of-00001.parquet   -> read here as dev.parquet
             data/test-00000-of-00001.parquet  -> read here as test.parquet
    split  : every published figure is the DEV split unless labelled
             otherwise; the held-out TEST split is reported only as a
             generalisation check.

To redo the measurement, download those files and point BAREC_DIR at the
directory holding them:

    BAREC_DIR=/path/to/barec python -m unittest tests.test_segment -v

Without BAREC_DIR the tests fall back to the machine this was first measured
on, and skip if it is absent. The harness prints the row count AND the SHA-256
of the file it actually read, so a run against a different corpus version is
visibly different rather than silently so: the row count catches a corpus that
changed size, the hash catches one that changed content without changing size.
"""
import hashlib
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from segment import TERMINATORS, is_arabic_letter, sentences, word_count


class TestSegment(unittest.TestCase):
    def test_splits_on_arabic_question_mark(self):
        self.assertEqual(
            sentences("هل حضر الوزير؟ نعم حضر."),
            ["هل حضر الوزير؟", "نعم حضر."],
        )

    def test_does_not_split_on_arabic_comma(self):
        self.assertEqual(
            len(sentences("الشمس طالعة، والنسيم عليل، والطيور مغردة.")), 1
        )

    def test_does_not_split_inside_decimal_number(self):
        self.assertEqual(len(sentences("بلغت النسبة 3.5 في المائة هذا العام.")), 1)

    def test_does_not_split_on_ellipsis(self):
        self.assertEqual(len(sentences("قال الرجل... ثم صمت.")), 1)

    def test_splits_on_newline(self):
        self.assertEqual(len(sentences("العنوان الأول\nالعنوان الثاني")), 2)

    def test_keeps_closing_quote_with_sentence(self):
        out = sentences('قال: «الحمد لله.» ثم مضى.')
        self.assertEqual(len(out), 2)
        self.assertTrue(out[0].endswith("»"))

    def test_empty_input(self):
        self.assertEqual(sentences(""), [])

    def test_keeps_curly_closing_quote_with_sentence(self):
        # A closer we do not list does not merely stay unattached: it defeats
        # the end-of-boundary lookahead, so the sentence is never split.
        out = sentences('قال: “الحمد لله.” ثم مضى.')
        self.assertEqual(len(out), 2)
        self.assertTrue(out[0].endswith("”"))

    def test_does_not_split_on_latin_initials(self):
        self.assertEqual(
            len(sentences("طور الحاسوب على يد جوزيف ليكليدر (J. C. R. Licklider) عام 1960.")), 1
        )

    def test_does_not_split_on_single_letter_abbreviation(self):
        # "ص. ب." = صندوق بريد (P.O. box); "ق. م." = قبل الميلاد (BCE).
        self.assertEqual(len(sentences("العنوان هو ص. ب. 682 أبو ظبي.")), 1)
        self.assertEqual(len(sentences("بني النقش عام 515 ق. م. في فارس.")), 1)

    def test_still_splits_after_a_diacritized_word(self):
        # Tashkeel are combining marks; the abbreviation guard must look past
        # them or it mistakes a real sentence ending for a one-letter token.
        out = sentences("هذا مُخَطَّطُ الدَّرْسِ. وهذا غيرُهُ.")
        self.assertEqual(len(out), 2)

    def test_sentence_ending_in_a_number_still_splits(self):
        self.assertEqual(len(sentences("بلغ العدد 2. ثم ارتفع بعد ذلك.")), 2)


# Opt-in: the corpus is not shipped (CC BY-SA, see NOTICE), so these tests
# run only when BAREC_DIR points at the downloaded parquet files. Checking
# the file rather than the directory: an emptied directory must skip, not fail.
BAREC = Path(os.environ.get("BAREC_DIR", ""))

try:
    import pyarrow  # noqa: F401  -- third-party, needed only for these tests
    _HAS_PYARROW = True
except ImportError:
    _HAS_PYARROW = False

BAREC_READY = (
    bool(os.environ.get("BAREC_DIR"))
    and (BAREC / "dev.parquet").is_file()
    and _HAS_PYARROW
)

SKIP_REASON = (
    "BAREC corpus not available. Set BAREC_DIR to a directory holding "
    "dev.parquet from CAMeL-Lab/BAREC-Corpus-v1.0 on HuggingFace "
    "(data/dev-00000-of-00001.parquet) and install pyarrow to reproduce "
    "the published figures."
)


def _sha256_16(path, chunk_size=1 << 20):
    """First 16 hex characters of the SHA-256 of `path`.

    Read in 1 MiB chunks rather than slurping the parquet, so hashing a corpus
    costs no more memory than reading it would. Truncated to 16 characters to
    stay readable in a provenance line; that is 64 bits, far more than enough
    to tell two corpus releases apart -- it is a drift check, not a defence
    against a forged corpus.
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk_size), b""):
            h.update(block)
    return h.hexdigest()[:16]


def _load_docs():
    import pyarrow.parquet as pq
    import collections

    path = BAREC / "dev.parquet"
    rows = pq.read_table(str(path)).to_pylist()
    docs = collections.defaultdict(list)
    for r in rows:
        docs[r["Document"]].append(r["Sentence"])
    return docs, len(rows), _sha256_16(path)


@unittest.skipUnless(BAREC_READY, SKIP_REASON)
class TestBarecAgreement(unittest.TestCase):
    """Measures, it does not assert a threshold we have not earned yet."""

    def test_report_agreement_rate(self):
        import pyarrow.parquet as pq
        import collections

        rows = pq.read_table(str(BAREC / "dev.parquet")).to_pylist()
        docs = collections.defaultdict(list)
        for r in rows:
            docs[r["Document"]].append(r["Sentence"])

        exact = total = 0
        for doc, sents in list(docs.items())[:200]:
            gold = [s.strip() for s in sents if s and s.strip()]
            if len(gold) < 2:
                continue
            recomposed = " ".join(gold)
            got = sentences(recomposed)
            total += len(gold)
            exact += sum(1 for g in gold if g in got)

        rate = 100.0 * exact / total if total else 0.0
        print(f"\ncorpus: CAMeL-Lab/BAREC-Corpus-v1.0, dev split, {len(rows)} rows read")
        print(f"        {BAREC / 'dev.parquet'}")
        print(f"        sha256[:16] of the file read = {_sha256_16(BAREC / 'dev.parquet')}")
        print(f"BAREC agreement: {exact}/{total} sentences recovered = {rate:.1f}%")
        self.assertGreater(total, 0, "no documents evaluated")


@unittest.skipUnless(BAREC_READY, SKIP_REASON)
class TestBarecStricter(unittest.TestCase):
    """Additional, stricter figures alongside the headline agreement rate.

    `g in got` above is LIST MEMBERSHIP (exact string equality against one of
    our segments), not substring containment -- so it is already a strict
    per-sentence recall. What it does NOT show is (a) how many spurious splits
    we introduce, and (b) how much of the shortfall is our fault versus the
    harness's: BAREC contains many unpunctuated headline fragments, and
    `" ".join(gold)` destroys the line breaks that alone could separate them.
    """

    def test_report_stricter_figures(self):
        docs, n_rows, digest = _load_docs()

        tp = n_pred = n_gold = 0          # internal boundary precision/recall
        docs_exact = docs_eval = 0        # whole-document exact list equality
        reachable = total = 0             # ceiling for any terminator-based rule
        recovered = 0

        for doc, sents in list(docs.items())[:200]:
            gold = [s.strip() for s in sents if s and s.strip()]
            if len(gold) < 2:
                continue
            recomposed = " ".join(gold)
            got = sentences(recomposed)

            total += len(gold)
            recovered += sum(1 for g in gold if g in got)

            docs_eval += 1
            if got == gold:
                docs_exact += 1

            # Ceiling: a gold sentence can only be isolated from the
            # space-joined text if the boundary before it and after it are both
            # marked by a terminator.
            for i, g in enumerate(gold):
                before_ok = (i == 0) or bool(gold[i - 1]) and gold[i - 1][-1] in TERMINATORS
                after_ok = (i == len(gold) - 1) or g[-1] in TERMINATORS
                if before_ok and after_ok:
                    reachable += 1

            # Internal boundaries as cumulative whitespace-token counts.
            if len(recomposed.split()) != sum(len(g.split()) for g in gold):
                continue
            if " ".join(got).split() != recomposed.split():
                continue

            def cuts(seq):
                acc, out_ = 0, []
                for s in seq[:-1]:
                    acc += len(s.split())
                    out_.append(acc)
                return set(out_)

            g_cuts, p_cuts = cuts(gold), cuts(got)
            tp += len(g_cuts & p_cuts)
            n_pred += len(p_cuts)
            n_gold += len(g_cuts)

        prec = 100.0 * tp / n_pred if n_pred else 0.0
        rec = 100.0 * tp / n_gold if n_gold else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

        print("\n--- stricter figures: BAREC-Corpus-v1.0, dev split ---")
        print(f"{n_rows} rows read, {docs_eval} documents evaluated")
        print(f"sha256[:16] of the file read = {digest}")
        print(f"sentence recall (exact string match) : {recovered}/{total} = {100.0*recovered/total:.1f}%")
        print(f"ceiling for any terminator-based rule: {reachable}/{total} = {100.0*reachable/total:.1f}%")
        print(f"recall as a share of that ceiling    : {100.0*recovered/reachable:.1f}%" if reachable else "")
        print(f"whole-document exact list equality   : {docs_exact}/{docs_eval} = {100.0*docs_exact/docs_eval:.1f}%")
        print(f"boundary precision                   : {tp}/{n_pred} = {prec:.1f}%")
        print(f"boundary recall                      : {tp}/{n_gold} = {rec:.1f}%")
        print(f"boundary F1                          : {f1:.1f}%")

        self.assertGreater(total, 0, "no documents evaluated")


class TestWordCount(unittest.TestCase):
    """The one definition of "word" that registers.json documents.

    It lives here, beside `sentences()`, because the sentence-length bands in
    assets/registers.json were measured with this rule and the checker tests
    each sentence against those bands. Were the checker to carry its own copy,
    the cap and the count could drift apart without any test noticing.
    """

    def test_a_token_needs_an_arabic_letter_to_count(self):
        # Latin token, bare number, bare punctuation: none of them is a word.
        self.assertEqual(2, word_count("Microsoft 2024 \u060C \u0643\u0644\u0645\u0629 \u0623\u062E\u0631\u0649"))

    def test_an_empty_text_counts_zero(self):
        self.assertEqual(0, word_count(""))
        self.assertEqual(0, word_count("   \n  "))

    def test_attached_punctuation_does_not_split_a_word(self):
        # "kalima," is one token and one word, not two.
        self.assertEqual(3, word_count("\u0642\u0627\u0644 \u0627\u0644\u0648\u0632\u064A\u0631\u060C \u062B\u0645."))

    def test_a_vocalised_word_still_counts_once(self):
        # The marks are not letters, but the token carries letters underneath.
        self.assertEqual(2, word_count("\u0642\u064E\u0627\u0644\u064E \u0627\u0644\u0652\u0648\u064E\u0632\u0650\u064A\u0631\u064F"))

    def test_a_diacritic_is_not_a_letter(self):
        self.assertFalse(is_arabic_letter("\u064E"))   # fatha
        self.assertFalse(is_arabic_letter("\u0670"))   # superscript alef
        self.assertFalse(is_arabic_letter("\u0661"))   # Arabic-Indic one
        self.assertTrue(is_arabic_letter("\u0642"))    # qaf
