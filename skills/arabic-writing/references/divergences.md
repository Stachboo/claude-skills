# Divergences: where the authorities genuinely disagree

This file lists the points on which competent Arabic authorities contradict each other. **The skill
never settles them.** It checks that a text is internally consistent with the school its author
declared through the preset, and it reports the divergence rather than a verdict. This matters most
to a reader who does not read Arabic: told that a spelling is "wrong", you would go and change it —
and half the Arab world would then consider it wrong the other way. Each entry below therefore names
the positions, the bodies that hold them, and what the checker does and does not do about it.

Labels follow `registers.md`: `[verified]` = checked first-hand here, `[reported]` = read through a
summary or carried from this project's research phase, `[unverified]` = unchecked.

## Hamza on a seat, medial and final

The hamza (ء) is the glottal-stop consonant. It is written either on its own or on a "seat" — a
waw (و), a yaʾ (ي) or an alif (ا) — and which seat it takes is the single most disputed point in
Arabic orthography. Three normative positions, all documented, all in current use:

| case | Cairo, 26th session | Cairo, 46th session | Damascus |
|---|---|---|---|
| شؤون / شئون ("affairs") | شؤون | شئون | شؤون |
| fatha after a silent medial waw | — | standalone: ضوءها | on the waw: ضوؤك |

`[reported]` — the academy decisions are carried from this project's research phase and were not
reopened while writing this file.

The Cairo Academy's 46th session derives its answers from three stated pillars:

1. Arabic writing avoids توالي الأمثال — a run of identical letter shapes in sequence;
2. a suffix counts as part of the word, while a prefix does not;
3. the vowels rank كسرة › ضمة › فتحة › سكون (*kasra* › *ḍamma* › *fatḥa* › *sukūn*, i.e. the
   i-vowel outranks the u-vowel, which outranks the a-vowel, which outranks the absence of a vowel).

Applied, those pillars yield مسئول ("responsible", "official") and شئون. The same academy's 26th
session had given شؤون. Both remain in print. The Academy of Damascus departs from the classical
usage in the *opposite* direction, writing ضوؤك where the ancients wrote a standalone hamza.

Damascus says so in its own preface: each Arab country has its own orthographic practice —
"فأهل المغرب لهم قواعد إملائية يختصون بها، ولأهل مصر قواعدهم، ولأهل الشام قواعدهم" ("the people of
the Maghreb have orthographic rules of their own, the people of Egypt have theirs, and the people of
the Levant theirs") — and, of the modern attempts to unify them, "لم نجد بينها طريقة واحدة صالحة
لأن يقع عليها الإجماع" ("we found among them no single method fit to command consensus").

A checker that picked one of these would be wrong about half the time. This one does not pick. The
profile records a declared school — `assets/profiles.json` assigns `cairo-46` to the `legal` and
`religious` presets and `modern-usage` to `news`, `magazine`, `literary`, `reference` and `children`
— and the checks test the text for consistency with **that** declaration. The set of school values
is deliberately open: `scripts/profiles.py` accepts a declared school it has never seen rather than
rejecting one that is legitimate but unlisted.

## Digits — read this one carefully

Arabic is written with two digit sets: the Arabic-Indic digits ٠١٢٣٤٥٦٧٨٩ and the European digits
0123456789 (which are themselves of Arabic origin). Arabic-Indic digits predominate in the Machrek
— the eastern Arab world — and European digits in the Maghreb (W3C, *Arabic & Persian Layout
Requirements*). `[reported]`

**This is a REGIONAL divergence, not a generic one.** It follows the reader's country, not the genre
of the text.

The `arabic-writing` presets nonetheless assign a digit convention per genre: `assets/profiles.json`
gives Arabic-Indic to `literary`, `religious` and `children`, and European to `news`, `magazine`,
`legal` and `reference`. `[verified]` — read from the asset.

**That assignment is an arbitrary project default with no source behind it.** No authority ties a
digit set to a genre. It exists only so that choosing one preset resolves a complete profile without
the author having to answer a question they may have no basis to answer, and it is meant to be
overridden: an author publishing for a Moroccan readership should set `digits` explicitly, whatever
the genre. The checker verifies that a text is consistent with whatever was declared. It never
judges the choice itself, and nothing in this file should be read as a recommendation of one digit
set over the other.

## Italics

Two professional style guides, opposite instructions:

- Netflix, *Arabic Timed Text Style Guide*: "Do not use italics at all in Arabic." `[reported]`
- The World Bank, *Arabic Style Guide* (2004): italics are "a new formatting tool used to emphasize
  a word or phrase", with bold recommended for names and italics for subheadings. `[reported]`

The real disagreement underneath is not typographic taste. Arabic has no capital letters, so one of
the devices other scripts use to mark emphasis and proper names is simply missing. The World Bank
imports a replacement from Latin typography; Netflix refuses it because slanting distorts the Arabic
ductus — the connected stroke that joins letters within a word — and degrades legibility, especially
on screen at subtitle sizes.

Neither is wrong. The profile carries an `italics` field; every shipped preset sets it to `false`,
and `scripts/profiles.py` notes explicitly that `italics: true` is a legitimate value although no
preset uses it. `[verified]` — read from `assets/profiles.json` and `scripts/profiles.py`.

## Diacritics in running prose

How much تشكيل (*tashkīl*, the vowel marks) belongs in ordinary prose is also contested, but the
contest there runs through religious citation practice and is documented, with its sources and its
measured baseline, in `religious-register.md`. It is not duplicated here.

## Tanwīn al-fatḥ: where the mark sits, and whether it is written — `AR-TANWIN-01`

The indefinite accusative ending in an alif — أيضا، جدا، شهرا — can carry the double fatḥa
(تنوين الفتح, U+064B). Two questions, and they are not settled the same way.

**Where it sits.** Two byte sequences, almost identical on screen, both in print:

| placement | bytes | example |
|---|---|---|
| on the letter **before** the alif | letter + U+064B + U+0627 | `أيضًا` |
| on the **alif** | letter + U+0627 + U+064B | `أيضاً` |

- **Netflix**, *Arabic Timed Text Style Guide* §22, puts it before the alif "due to line heights that
  create overlapping in many cases" — a typesetting reason, not a grammatical one. `[verified]`
  (first-hand, archived copy; see `sources.md`).
- **No Arabic-language normative source naming the placement was found.**
- **Measured usage**, BAREC v1.0, 68 677 prose sentences, 2026-10-01 `[verified]`: over 33 adverbials
  that are always indefinite accusatives, the mark sits before the alif in 1 905 occurrences and on it
  in 418 — but by publisher the split is **7 sources to 6**, and Arabian Nights, the Arabic Learner
  Corpus, BTEC and the Constitutions never put it before the alif. A count by occurrences mostly
  measures Hindawi (806 of the 1 905).

**What the checker does:** `AR-TANWIN-01`, severity `divergence`. It never says which placement is
right. It reports a text that uses **both**, outside cited scripture, once, with both counts, pointed
at the first occurrence of the rarer placement. It never changes the exit code. In BAREC it fires on
14.3% of the documents carrying at least two marks; a random sample of 50 matched words held 50 real
tanwīn.

**Whether it is written at all.** In the same functional prose the mark is written on **79.4%** of the
probe words and omitted on **20.6%**; 4 publishers out of 15 omit it in majority (Zayed bilingual and
the subtitles at 100%). The Cairo Academy's 1959–60 decision on school-book vocalisation drops the
fatḥa family outside scripture («يُهمل الشكل بالفتحة»), and Damascus describes the tanwīn as what
writers "have taken to drawing" («جرى الكاتبون»). So **omitting it is attested usage, not an error —
but it is the minority usage.** None of these sources names the tanwīn in adult prose.

**What the checker does:** nothing. Deciding which words *need* the mark takes a morphological
analyser, which this pack does not ship. Do not tell an author a missing tanwīn is a fault, and do not
tell them it is the norm.

Reproduce every figure in this section, per-source table included:
`python tools/barec_tanwin.py DIR`, where `DIR` holds the three BAREC parquet files (download
instructions at the top of the script; it needs `pyarrow`, the checker does not).
