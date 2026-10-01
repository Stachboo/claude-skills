# -*- coding: utf-8 -*-
"""Sentence segmentation for Arabic text. Standard library only.

Arabic punctuates sparsely, so a naive split on '.' over-segments. The rules
below were chosen against BAREC, whose sentences are human-annotated; see
tests/test_segment.py::TestBarecAgreement for the measured agreement rate.

Pure module by design: no I/O, no CLI, no printing. `sentences()` is the only
public entry point; `TERMINATORS` and `CLOSERS` are exported for callers that
need to reason about the same punctuation set.
"""
import re
import unicodedata

TERMINATORS = ".؟!?"
# Closers must be listed exhaustively: a terminator followed by a closer we do
# not know about fails the `(?=\s|$)` lookahead below, so the sentence is not
# split at all. BAREC only exercises « » and the straight quote, but curly
# quotes are common in real prose. U+FD3E is kept from the original rule set;
# BAREC has 3 of each ornate parenthesis and none at a boundary, so the corpus
# cannot settle which of U+FD3E/U+FD3F closes in logical order -- left as is
# rather than guessed at, since the measured impact either way is zero.
CLOSERS = "»\"')]}”’›﴾"

# A terminator ends a sentence unless it is part of a run (ellipsis). The
# trailing `(?=\s|$)` is also what keeps decimals intact: in "3.5" the dot is
# followed by a digit, so it never becomes a candidate boundary at all.
_BOUNDARY = re.compile(
    r"(?<![" + re.escape(TERMINATORS) + r"])"      # not preceded by a terminator
    r"([" + re.escape(TERMINATORS) + r"])"          # the terminator
    r"(?![" + re.escape(TERMINATORS) + r"])"        # not followed by a terminator
    r"([" + re.escape(CLOSERS) + r"]*)"             # trailing closers stay attached
    r"(?=\s|$)"                                     # boundary must be followed by space or end
)


def _prev_base(text, i):
    """Index of the base character at or before `i`, skipping tashkeel.

    Arabic diacritics are combining marks and tatweel is a stretch glyph;
    neither is part of the letter sequence we want to inspect. Without this,
    a diacritized word like "الدَّرْسِ." looks like a one-letter token and the
    abbreviation guard below misfires (measured: it cost 2 points of recall).
    """
    while i >= 0 and (unicodedata.combining(text[i]) or text[i] == "ـ"):
        i -= 1
    return i


def _is_initial_dot(line, i):
    """True if the '.' at `line[i]` closes a one-letter token, not a sentence.

    Covers Latin initials ("J. C. R. Licklider") and the Arabic single-letter
    abbreviations that really occur in prose: "ص. ب." (P.O. box), "ق. م." (BCE).
    Arabic has no one-letter word that can legitimately end a sentence, so this
    is safe. Deliberately restricted to letters: a trailing digit ("الدرس 2.")
    is left alone, because a sentence may genuinely end in a number.
    """
    j = _prev_base(line, i - 1)
    if j < 0 or not line[j].isalpha():
        return False
    k = _prev_base(line, j - 1)
    return k < 0 or not line[k].isalnum()


def sentences(text):
    """Split `text` into sentences. Returns a list of stripped strings."""
    if not text or not text.strip():
        return []
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        start = 0
        for m in _BOUNDARY.finditer(line):
            i = m.start(1)
            if line[i] == "." and _is_initial_dot(line, i):
                continue
            end = m.end(2)
            chunk = line[start:end].strip()
            if chunk:
                out.append(chunk)
            start = end
        tail = line[start:].strip()
        if tail:
            out.append(tail)
    return out


# --------------------------------------------------------------------------
# What counts as a word, and as a letter.
#
# assets/registers.json states the definition in prose -- "a word is a token
# containing at least one Arabic letter; punctuation and bare numbers are not
# counted" -- and the BAREC sentence-length bands in that same asset were
# measured with it. The cap a checker tests against and the count it tests are
# therefore the same definition, so it is implemented once, here.
#
# Here rather than in check.py because this module already owns the question
# "how is this text cut up", and because the sentences being counted come out
# of `sentences()` just above. Two copies of a definition that must agree,
# living in two files, is how they come to disagree.
#
# The letter range is U+0621-U+064A: Arabic letters proper. It excludes the
# tashkeel block above it (marks, not letters), the Arabic-Indic digits
# U+0660-U+0669 (a bare number is not a word), and the extended ranges from
# U+066E up, which carry Persian and Urdu letters BAREC does not contain.
# --------------------------------------------------------------------------

LETTER_FIRST = "\u0621"
LETTER_LAST = "\u064A"


def is_arabic_letter(ch):
    """True for an Arabic letter proper -- not a diacritic, not a digit."""
    return LETTER_FIRST <= ch <= LETTER_LAST


def words(text):
    """The Arabic-bearing tokens of `text`, in order.

    A token qualifies on containing at least one Arabic letter, so a token that
    is only punctuation, only digits or only Latin does not count. Splitting on
    whitespace is what registers.json documents; the corpus's own Word_Count
    field counts punctuation as tokens and was not used.
    """
    return [t for t in text.split() if any(is_arabic_letter(c) for c in t)]


def word_count(text):
    """Number of Arabic words in `text`. See `words`."""
    return len(words(text))
