# -*- coding: utf-8 -*-
"""arabic-writing checker: the command line the skill is enforced through.

The portable Agent Skill spec has no hooks, no model field, no effort field. A
script that exits non-zero is the only thing this skill can make happen, so
this file is the spine, not an accessory.

Exit codes, and they must stay distinguishable:
  0  no hard rule violated -- a verdict
  1  at least one hard rule violated -- a verdict
  2  the run could not happen: bad usage, unreadable input, broken rule table

2 is deliberately not a verdict. Everything that is not "I read this text and
judged it" routes there, because a crash that exits 1 would be read as a hard
finding, and a crash that exited 0 would be read as approval.

Output is English on purpose. The gap this skill exists to fill is the absence
of a tool whose judgement is legible to someone who must validate Arabic
WITHOUT reading Arabic, so every finding prints four things: the rule id, a
plain-English message, the fix, and the source. The Arabic appears only as the
excerpt -- the evidence, which the reader can hand to someone who does read it.

What this file owns, and what it does not
-----------------------------------------
It owns the ratio rules: the checks that are measurements over a whole text
rather than regexes over a span. `rules.run_rules` skips those by construction;
without the pass below, AR-DIAC-01 would be recorded, sourced, typed -- and
inert, which is what it was until this file existed.

It does NOT own the definition of a word or of an Arabic letter. That lives in
`segment.py`, next to the segmentation that produces the sentences being
counted and beside the asset whose bands were measured with it.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profiles import FIELDS, PRESET_NAMES, PRESETS, resolve, targets
from rules import load_rules, run_rules
from segment import is_arabic_letter, sentences, word_count

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "assets" / "rules.json"

EXIT_CLEAN = 0
EXIT_HARD = 1
EXIT_CANNOT_JUDGE = 2

# Diacritics: the tashkeel block, plus the superscript alef, which sits apart
# from it at U+0670 and is a mark like the rest.
DIACRITIC_FIRST = "\u064B"
DIACRITIC_LAST = "\u0652"
SUPERSCRIPT_ALEF = "\u0670"

# Cited scripture, removed before any vocalisation is measured. Full tashkil is
# REQUIRED inside these by the same 1959-60 decision that discourages it
# outside, so measuring them would make every correctly sourced religious text
# look defective -- the worst failure available in this project.
#
# U+FD3F opens and U+FD3E closes, despite their Unicode names saying the
# reverse; that is what AR-RELIG-02 is about, and it is why these are written
# as escapes here and never as literals. The negated classes stop one span from
# swallowing the prose that lies between two separate quotations.
CITATION = re.compile(
    "\uFD3F[^\uFD3F\uFD3E]*\uFD3E"      # Qur'anic verse in ornate parentheses
    "|"
    "\u00AB[^\u00AB\u00BB]*\u00BB"      # hadith or quotation in guillemets
)

# Profile values under which heavy vocalisation is the declared intent rather
# than a defect: the religious preset vocalises its citations in full, the
# children preset vocalises everything. Density says nothing about either.
VOCALISATION_BY_DESIGN = frozenset({"citations-full", "full"})


def _use_utf8(stream):
    """Make `stream` write UTF-8 and never raise on a character it cannot map.

    Measured on Windows: a child Python writing to a pipe gets
    sys.stdout.encoding == 'cp1252', and printing a single Arabic character
    raises UnicodeEncodeError. That exits 1 -- indistinguishable from a hard
    finding -- and loses the whole report along the way. A checker whose
    evidence is Arabic cannot leave its own output to the console's codepage.

    errors='replace' rather than 'strict' because losing one character from an
    excerpt is survivable and losing the verdict is not.
    """
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass                                # detached, or already reconfigured


def is_diacritic(ch):
    """True for an Arabic diacritic: the tashkeel block, or superscript alef."""
    return DIACRITIC_FIRST <= ch <= DIACRITIC_LAST or ch == SUPERSCRIPT_ALEF


def strip_citations(text):
    """Remove cited scripture, so it is measured neither as marks nor as letters.

    Replaced by a space, not by nothing, so that the words on either side of a
    quotation do not fuse into one token for any later count.

    Deliberate limit: an unclosed or reversed pair strips nothing, so such a
    text is measured whole and may report a density it did not earn. That is
    the safe direction -- reversed ornate parentheses already fire AR-RELIG-02
    as a hard finding, so the text is failing for a sourced reason first.
    """
    return CITATION.sub(" ", text)


def diacritic_density(text):
    """Diacritics per 1000 Arabic letters, cited scripture excluded.

    `per_1000` is None when nothing is left outside the citations: a text that
    is only a quoted verse has no denominator, and reporting 0 there would be
    a measurement nobody made.
    """
    body = strip_citations(text)
    letters = sum(1 for c in body if is_arabic_letter(c))
    marks = sum(1 for c in body if is_diacritic(c))
    return {
        "arabic_letters": letters,
        "diacritics": marks,
        "per_1000": None if letters == 0 else round(marks * 1000 / letters),
    }


def _diacritic_finding(rule, profile, density):
    """AR-DIAC-01: judge a measured density against the declared profile.

    Returns a finding, or None. Three ways to return None, each of them silence
    that has been earned rather than assumed:
      - no profile was declared, so nothing said which policy applies and the
        number is reported without being judged;
      - the declared profile vocalises by design;
      - nothing measurable was left outside the citations.
    """
    if profile is None or profile.get("diacritics") in VOCALISATION_BY_DESIGN:
        return None
    measured = density["per_1000"]
    if measured is None:
        return None
    try:
        threshold = rule["threshold"]["diacritics_per_1000_letters"]
    except (KeyError, TypeError):
        # A ratio rule with no threshold cannot judge anything. Raising routes
        # it to exit 2 as the packaging fault it is; letting the KeyError out
        # would exit 1 and report a broken table as a defective text.
        raise ValueError(
            "rule %s carries no threshold.diacritics_per_1000_letters; a ratio "
            "rule with no cut-off cannot produce a verdict" % (rule["id"],))
    if measured <= threshold:
        return None
    return {
        "id": rule["id"],
        "severity": rule["severity"],
        "message": "%s Measured %d diacritics per 1000 Arabic letters against "
                   "a provisional threshold of %d; cited scripture was excluded "
                   "before measuring."
                   % (rule["message"], measured, threshold),
        "fix": rule.get("fix", ""),
        "isnad": rule["isnad"],
        # A ratio has no position: it is a property of the whole text. Null
        # rather than 1:1, which would point the reader at a character that has
        # nothing in particular wrong with it.
        "line": None,
        "col": None,
        "excerpt": "",
        "measured": measured,
        "threshold": threshold,
    }


# One entry per ratio rule. A ratio rule with no entry raises rather than being
# skipped: "recorded, sourced, typed and inert" is exactly the state AR-DIAC-01
# was in before this pass existed, and silence is how it stayed there unnoticed.
RATIO_MEASUREMENTS = {"AR-DIAC-01": _diacritic_finding}


def ratio_findings(rules, profile, density):
    """Run every ratio rule in the table. Same finding shape as `run_rules`."""
    out = []
    for r in rules:
        if r.get("kind") != "ratio":
            continue
        measure_it = RATIO_MEASUREMENTS.get(r["id"])
        if measure_it is None:
            raise ValueError(
                "rule %s is kind 'ratio' but no measurement is registered for "
                "it in check.py; it would be recorded and inert" % (r["id"],))
        finding = measure_it(r, profile, density)
        if finding is not None:
            out.append(finding)
    return out


# Tanwin al-fath carried by a word-final alif, in its two printed placements.
# Marks other than U+064B may sit on either side of it (a shadda, typically);
# the lookaheads keep both patterns at the end of a word.
_OTHER_MARKS = "[ٌ-ْٰ]*"
_WORD_GOES_ON = "(?![ء-يً-ْٰ])"
TANWIN_BEFORE_ALIF = re.compile(
    "(?<=[ء-ي])" + _OTHER_MARKS + "ً" + _OTHER_MARKS + "ا"
    + _WORD_GOES_ON)
TANWIN_ON_ALIF = re.compile(
    "(?<=[ء-ي])ا" + _OTHER_MARKS + "ً" + _WORD_GOES_ON)


def tanwin_placements(text):
    """Offsets of each placement of tanwin al-fath, cited scripture excluded.

    Returns {"before": [...], "on": [...]}. Citations are blanked to spaces of
    the same length rather than removed, so the offsets still index `text`.
    """
    body = CITATION.sub(lambda m: " " * len(m.group(0)), text)
    return {
        "before": [m.start() for m in TANWIN_BEFORE_ALIF.finditer(body)],
        "on": [m.start() for m in TANWIN_ON_ALIF.finditer(body)],
    }


def _tanwin_finding(rule, text):
    """AR-TANWIN-01: report a text that uses both placements, and say nothing else.

    Points at the first occurrence of the less frequent placement -- the one a
    reader would most likely change -- and carries both counts, because the
    rule is a divergence: it may report the mix, never choose a side.
    """
    found = tanwin_placements(text)
    before, on = found["before"], found["on"]
    if not before or not on:
        return None
    pos = (before if len(before) < len(on) else on)[0]
    line = text.count("\n", 0, pos) + 1
    col = pos - (text.rfind("\n", 0, pos) + 1) + 1
    return {
        "id": rule["id"],
        "severity": rule["severity"],
        "message": "%s Counted outside cited scripture: %d before the alif, %d on "
                   "the alif." % (rule["message"], len(before), len(on)),
        "fix": rule.get("fix", ""),
        "isnad": rule["isnad"],
        "line": line,
        "col": col,
        "excerpt": text[max(0, pos - 20):pos + 20].replace("\n", " "),
        "before": len(before),
        "on": len(on),
    }


# Same discipline as RATIO_MEASUREMENTS: a consistency rule with no entry
# raises instead of sitting in the table inert.
CONSISTENCY_CHECKS = {"AR-TANWIN-01": _tanwin_finding}


def consistency_findings(rules, text):
    """Run every consistency rule in the table. Same finding shape as `run_rules`."""
    out = []
    for r in rules:
        if r.get("kind") != "consistency":
            continue
        check_it = CONSISTENCY_CHECKS.get(r["id"])
        if check_it is None:
            raise ValueError(
                "rule %s is kind 'consistency' but no check is registered for "
                "it in check.py; it would be recorded and inert" % (r["id"],))
        finding = check_it(r, text)
        if finding is not None:
            out.append(finding)
    return out


def measure(text, profile):
    """Sentence-length report against the profile's audience target.

    The cap is a ceiling tested sentence by sentence, never a mean: BAREC
    annotates a text at the level of its single most difficult element, so a
    text averaging 13 words -- the advanced median -- but carrying one 40-word
    sentence is not an advanced text, because 40 exceeds the advanced cap of
    26. What this returns is therefore the sentences that exceed the declared
    band, not a band the text has been sorted into.

    `word_count` comes from segment.py so that the count and the band it is
    compared against are one definition -- see the note at the foot of that
    module.
    """
    t = targets(profile["audience"], profile["genre"])
    cap = t["sentence_words"]["max"]
    over = []
    for s in sentences(text):
        n = word_count(s)
        if n > cap:
            over.append({"words": n, "excerpt": s[:70]})
    return {"cap": cap, "over_cap": over, "targets": t}


def parse_overrides(items, preset):
    """Turn a list of "field=value" strings into a mapping, or raise ValueError.

    Why the CLI has this at all: the seven presets are seven fixed points in a
    space `resolve()` already models as six independent fields, and the fixed
    points do not cover it. Measured on 2026-09-17: no preset pairs
    `audience: foundational` with `diacritics: functional`, so a plain-language
    text for untrained adult readers could get the foundational sentence cap or
    a vocalisation check, never both. An eighth preset would not have fixed the
    shape of the problem, only that one hole in it -- and a preset must carry a
    genre, and a genre carries a measured verbal ratio, which this project does
    not have for that audience.

    `value` is taken verbatim as a string, with one exception: where the
    preset's own value for that field is a bool, the string is required to be
    `true` or `false` and is converted. Five of the six fields are strings and
    need nothing; `italics` is a bool, and storing the string "true" there
    would be a truthy value that is not True -- inert today, because no rule
    reads the field, and a silent defect the day one does. The rule is derived
    from the asset rather than from a hardcoded list of field names, so a field
    that changes type in the asset does not leave a stale coercion here.

    Unknown FIELD names are left to `resolve()`, which owns that check and
    already explains why a typo must raise instead of passing silently.
    """
    out = {}
    for item in items:
        if "=" not in item:
            raise ValueError(
                "--set expects FIELD=VALUE, got %r. Valid fields are: %s"
                % (item, ", ".join(sorted(FIELDS)))
            )
        field, _, value = item.partition("=")
        field, value = field.strip(), value.strip()
        if isinstance(PRESETS.get(preset, {}).get(field), bool):
            low = value.lower()
            if low not in ("true", "false"):
                raise ValueError(
                    "--set %s expects true or false, got %r: this field is a "
                    "boolean, and any other string would be stored as a "
                    "truthy value that is not True." % (field, value)
                )
            value = (low == "true")
        out[field] = value
    return out


def _read(path):
    """Return the file's text, or raise ValueError carrying a message for the user.

    utf-8-sig, not utf-8: a byte-order mark left by a Windows editor would
    otherwise survive as U+FEFF at the head of the text, where it sits between
    the start of the line and the first real character and can defeat a rule
    anchored on '^'.

    UnicodeDecodeError is caught alongside OSError because it is a ValueError
    and not an OSError: a handler catching only OSError lets it escape as a
    traceback and exit 1, reporting a mis-encoded file as a hard finding. A
    file in cp1256 is the single most likely thing to be handed to an Arabic
    checker.
    """
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except OSError as e:
        raise ValueError("cannot read %s: %s" % (path, e))
    except UnicodeDecodeError:
        raise ValueError(
            "cannot read %s: it is not UTF-8. Convert it first; this checker "
            "reads UTF-8 only, and guessing an encoding would silently change "
            "which characters the rules see." % (path,))


def _print_report(report):
    """The human report. Every finding carries its id, message, fix and source."""
    path = report["file"]
    if report["preset"]:
        print("preset: %s (audience=%s, genre=%s)"
              % (report["preset"], report["profile"]["audience"],
                 report["profile"]["genre"]))
    for f in report["findings"]:
        where = path if f["line"] is None else "%s:%d:%d" % (path, f["line"], f["col"])
        print("%s  [%s] %s" % (where, f["id"], f["severity"]))
        print("    %s" % f["message"])
        if f["fix"]:
            print("    fix: %s" % f["fix"])
        print("    source: %s" % f["isnad"])
        if f["excerpt"]:
            print("    text: ...%s..." % f["excerpt"])
        print()
    length = report["length"]
    if length and length["over_cap"]:
        print("sentences over the %d-word cap for this audience:" % length["cap"])
        for s in length["over_cap"]:
            print("    %d words: %s..." % (s["words"], s["excerpt"]))
        print()
    d = report["diacritics"]
    if d["per_1000"] is None:
        print("vocalisation: not measured -- no Arabic outside cited scripture.")
    else:
        print("vocalisation: %d diacritics per 1000 Arabic letters, cited "
              "scripture excluded (this project's baseline measured 9-43 for "
              "functional prose, 770-784 for over-vocalised prose)."
              % d["per_1000"])
    counts = report["counts"]
    print("%d hard, %d recommendation, %d divergence"
          % (counts["hard"], counts["recommendation"], counts["divergence"]))


def main(argv=None):
    _use_utf8(sys.stdout)
    _use_utf8(sys.stderr)

    ap = argparse.ArgumentParser(description="Check Arabic text against sourced rules.")
    ap.add_argument("file", help="UTF-8 text file to check")
    ap.add_argument("--preset", default=None, help="one of: " + ", ".join(PRESET_NAMES))
    ap.add_argument("--set", dest="overrides", action="append", metavar="FIELD=VALUE",
                    default=None,
                    help="override one field of the preset's profile; repeatable. "
                         "Requires --preset. Fields: " + ", ".join(sorted(FIELDS)))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    # Everything that could stop this run from being a verdict is settled here,
    # and every one of them exits 2. A broken rule table is in the list on
    # purpose: it is a packaging fault, and reporting it as a clean text would
    # be the one failure mode this whole file exists to make impossible.
    try:
        if a.overrides and not a.preset:
            # Not an empty override: with no preset there is no profile to
            # override, so every field the user did not name would be unset,
            # and the length check reads `profile["audience"]` unconditionally.
            raise ValueError(
                "--set requires --preset: there is no profile to override "
                "without one. Choose a preset, then override its fields."
            )
        overrides = parse_overrides(a.overrides or [], a.preset)
        profile = resolve(a.preset, overrides) if a.preset else None
        text = _read(a.file)
        rules = load_rules(RULES_PATH)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return EXIT_CANNOT_JUDGE

    if not any(is_arabic_letter(c) for c in text):
        # "0 hard, 0 recommendation" over a file holding no Arabic is success
        # this checker has not earned: it found nothing because there was
        # nothing of its kind to find. That is a pointing error, not a verdict.
        print("%s contains no Arabic letters; nothing was checked. Check the "
              "path and the encoding." % (a.file,), file=sys.stderr)
        return EXIT_CANNOT_JUDGE

    density = diacritic_density(text)
    findings = run_rules(text, rules)
    try:
        # Appended after the positional findings rather than merged into them:
        # run_rules returns its list sorted by line and column, and a ratio
        # rule has neither, so there is no position to sort one into.
        findings = (findings + ratio_findings(rules, profile, density)
                    + consistency_findings(rules, text))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return EXIT_CANNOT_JUDGE

    counts = {s: len([f for f in findings if f["severity"] == s])
              for s in ("hard", "recommendation", "divergence")}
    # Looked up defensively: if AR-DIAC-01 is ever removed from the table, the
    # measurement is still reported, without a cut-off to compare it against.
    # Indexing [0] here would raise IndexError and exit 1 -- a missing rule
    # reported as a defective text.
    diac = next((r for r in rules if r["id"] == "AR-DIAC-01"), None)
    threshold = diac["threshold"]["diacritics_per_1000_letters"] if diac else None
    report = {
        "file": a.file,
        "preset": a.preset,
        # Recorded beside the preset name, not folded into it: a consumer that
        # read `preset: news` next to a profile that is not what `news` means
        # would have no way to tell why they disagree.
        "overrides": overrides,
        "profile": profile,
        "findings": findings,
        "length": measure(text, profile) if profile else None,
        "diacritics": dict(density, threshold=threshold),
        "counts": counts,
    }

    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        _print_report(report)
    return EXIT_HARD if counts["hard"] else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
