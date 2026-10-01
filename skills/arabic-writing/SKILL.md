---
name: arabic-writing
description: Reviews and writes Modern Standard Arabic. Checks punctuation, orthography and encoding against sourced academy decisions, and targets sentence length, nominal/verbal ratio and vocabulary level to a declared audience (news, legal, religious, literary). Use when writing, editing or validating Arabic text, including when you do not read Arabic yourself.
license: MIT
compatibility: Requires Python 3.8+ (standard library only)
metadata:
  version: "0.1.0"
---

# Arabic Writing

## Read this before deciding the skill has nothing for you

On 2026-09-17 five agents were given Arabic tasks **without** this skill, and their output was
measured (`tests/baseline/results-red.md`). **Not one mechanical check fired on any of the four
generated texts.** The model wrote `أُمُّ سَلَمَةَ` rather than "Umm Salama", wrapped a Qurʾanic
verse in `﴿ ﴾` and a hadith in `« »`, used `ﷺ`, and produced no Latin punctuation at all. Zero
findings across seven checks.

So this skill is **not** here to find your typos. A capable model already finds those. It is here
for the three things the same measurement showed going wrong:

1. **Over-vocalisation.** The generated prose ran at **784 and 770 diacritics per 1000 Arabic
   letters** — fully vocalised — against **9** for a news dispatch. The model reaches for تشكيل
   (*tashkīl*, the vowel and gemination marks) the moment it senses an elevated register. This is
   the one defect that reliably occurs, and it is invisible to a reviewer who does not read Arabic.
2. **The confident invented rule.** The reviewing agent found nearly every real defect in a
   deliberately degraded text — and then wrote: *"Em dashes used as parenthetical brackets. This is
   an English/French typographic convention imported into Arabic."* **That is false** (see
   "Do not invent rules" below). **None of its fifteen observations carried a source.** To a reader
   who cannot read Arabic, an invented rule and a real one look identical.
3. **The audience is never asked.** No agent asked who it was writing for. One targeting "readers
   with no religious training" produced 24-word sentences, well over the foundational cap of 15.

**The value here is preventing the unsourced ruling, and supplying the register targeting the model
does not do on its own.** Everything below serves that. The checker is the floor, not the ceiling.

## Quick start

One command, from the skill directory:

```
python scripts/check.py FILE --preset news
```

Seven presets: `news`, `magazine`, `literary`, `legal`, `reference`, `religious`, `children`.
One word resolves six fields — school, digits, italics, diacritics policy, audience and genre
(`assets/profiles.json`). **The design principle is one choice, not seven.** Pick the preset whose
genre matches the text; do not put six questions to an author who has no basis to answer them.

Run without `--preset` and the pattern rules still run, but nothing needing a declared profile does:
no length cap is applied, and the vocalisation figure is reported without being judged. **A run with
no preset is a weaker run.** Declare one.

### When no preset fits: `--set`

The seven presets are seven points in a space of six independent fields, and they do not cover it.
The case that forced this: a plain-language text for **adult** readers with no training. `children`
is the only preset with `audience: foundational`, and it declares `diacritics: full`, which switches
`AR-DIAC-01` off — so you could have the right sentence cap or a vocalisation check, never both.

```
python scripts/check.py FILE --preset children --set diacritics=functional
```

Repeatable, and it requires `--preset`: it overrides a profile, it does not build one. A misspelt
field exits 2 rather than passing silently — `--set audiance=foundational` would otherwise leave
`audience` at its preset value while looking as though you had set it, and the audience is what
selects the sentence cap.

**Reach for a preset first.** `--set` is for the text the seven genres do not describe, not a way
around picking one. There is no eighth preset because a preset carries a genre, a genre carries a
measured verbal ratio, and this project has not measured one for that audience — and it does not
publish numbers it cannot name a source and a count for.

Real output, run here on a clean literary fixture against a news preset:

```
$ python scripts/check.py tests/fixtures/clean/01.txt --preset news
preset: news (audience=advanced, genre=news)
sentences over the 26-word cap for this audience:
    43 words: وَلَّيتُ بصري صوبَ المُنحدَرات العالية المحيطة بذلك الوادي الضيق الذي ...
    ...
vocalisation: 74 diacritics per 1000 Arabic letters, cited scripture excluded (this
project's baseline measured 9-43 for functional prose, 770-784 for over-vocalised prose).
0 hard, 0 recommendation, 0 divergence
```

Exit 0, seven sentences over cap — which is what long-form narrative looks like measured against a
news cap, and exactly why the preset is a declaration, not a detector.

## What the exit code means

The portable Agent Skill spec has no hooks, no `model` field, no `effort` field. **A script exiting
non-zero is the only thing this skill can enforce.** Everything else in this file is prose you may
ignore; the exit code is not.

| code | meaning |
|---|---|
| **0** | the text was judged, and no hard rule was violated |
| **1** | the text was judged, and **at least one hard rule was violated** |
| **2** | **the run could not happen** — unreadable file, not UTF-8, unknown preset, no Arabic in the file, broken rule table |

**Exit 2 is not a verdict.** It never means "clean" and never means "failed". Verified here:
`--preset newspaper` prints `Unknown preset 'newspaper'. Choose one of: children, legal, literary,
magazine, news, reference, religious` and exits 2. A file holding no Arabic letters also exits 2
rather than reporting `0 hard, 0 recommendation` — finding nothing in a file that contained nothing
of your kind is a pointing error, not success. **On exit 2, fix the input and re-run. Never report
the result.**

Recommendations and divergences print but never change the exit code. `--json` gives the same report
machine-readably.

## Reviewing an existing text

The order matters, and each step exists because doing it later corrupts the step before it.

**1. Isolate cited scripture first.** Aḥmad Zakī Bāšā, who founded modern Arabic punctuation in
1912, **excluded the Qurʾan from his own system**: «لا موجب لاستعمال هذه العلامات في كتابة القرآن
الكريم» — there is no call for these marks in writing the Noble Qurʾan, because the reciters' pause
marks already do that work. Two consequences. A quoted verse is **not governed by the punctuation
rules that govern the prose around it**, so a missing comma inside a verse is not a finding. And any
density measured over a cited verse reports noise: one fully vocalised verse drags a whole-text
diacritic ratio into the wrong band. `check.py` strips `﴿ … ﴾` and `« … »` before measuring
vocalisation; **you must do the same by eye for anything you judge yourself.** Details in
[references/religious-register.md](references/religious-register.md).

**2. Run the checker.** Encoding and typography, mechanically, with a source printed under every
finding. This is the cheap pass and it comes before reading, because a reversed `﴾ … ﴿` or a cp1256
file makes everything you infer afterwards wrong. If the exit code is 2, stop and fix the input.

**3. Read each finding against its source, not against the tool.** Every one prints its rule id, a
plain-English message, the fix, and the isnad. `AR-DIAC-01`'s threshold is the one number in the
table with **no document behind it** — inferred from measurement, marked provisional
([references/sources.md](references/sources.md)). Treat that one as a prompt to look, not a verdict.

**4. Then length, against the declared audience — and only then.** A cap means nothing until you
know who the text is for. Step 1 matters here too: a long quoted verse counted as one of the
author's own sentences reports a fault the author did not commit.

**5. Report what you could not check.** Say which rules ran, and say what the checker does not cover
(see the last section). A reviewer who does not read Arabic needs the shape of the hole, not only
the findings.

**The checker's real target is human-written, legacy, translated and CMS-pasted Arabic** — degraded
web copy, the case that prompted this skill. Run it on freshly generated Arabic if you like; expect
it to come back clean, and do not read that as a quality signal.

## Writing Arabic

**Ask who the text is for before writing a word.** The baseline says no agent does this unprompted.
One question, or one preset name, settles it.

### Sentence length — caps, not averages

Measured on the BAREC Corpus v1.0, 68 677 prose sentences, classical poetry excluded (`[verified]`,
reproduced 2026-09-17 — [references/registers.md](references/registers.md)):

| audience | median | **cap** |
|---|---|---|
| foundational | 6 | **15** |
| advanced | 13 | **26** |
| specialized | 20 | **37** |

**These are per-sentence ceilings, not averages, and that distinction is the whole rule.** BAREC
annotates a passage at the level of its single most difficult element. A text averaging 13 words —
the advanced median — that carries one 40-word sentence **is not an advanced text**, because 40
exceeds the advanced cap of 26. Averaging over a document hides exactly the sentence the reader will
trip on. The check reports the sentences that exceed the declared band; it never sorts a text into a
band.

Two limits travel with the number. Above BAREC level 14, median length *falls* — the hardest Arabic
is not the longest, and a short line of rare vocabulary can be the hardest thing on the page, which
no length check can see. And the segmenter protects precision (87.8%) over recall on purpose:
under-splitting yields a false FAIL a human can dismiss, over-splitting yields a false PASS nobody
notices.

### Verbal and nominal sentences — guidance, not a check

Arabic sentences divide into جملة فعلية (*jumla fiʿliyya*, verbal — opening on a verb) and جملة
اسمية (*jumla ismiyya*, nominal — opening on a noun). The proportion is a genre marker: it moves
more than forty points across genres while moving about 2.5 points across the whole readability
scale.

| genre | news | religious | children | reference | literary | legal | magazine |
|---|---|---|---|---|---|---|---|
| verbal ratio | 0.69 | 0.62 | 0.61 | 0.51 | 0.50 | 0.45 | 0.41 |

News and narrative lean verbal; legal and magazine analysis lean nominal.

> **This skill cannot measure that ratio.** Deciding whether a sentence is verbal or nominal needs a
> part-of-speech tagger, and this pack ships none. The figures are `[reported]` and are guidance for
> the writing side only. `check.py` does not verify them, and **no report may imply that it did.**

The same honesty covers three profile fields: `school`, `digits` and `italics` are **declared by the
preset and consumed by no rule today** (verified against `assets/rules.json`). They record the
author's choice; they are not yet enforced. Do not tell an author their digits were checked.

## Diacritics — the one defect that actually occurs

**Policy: full vocalisation on Qurʾanic verses and hadith; functional everywhere else.**

Functional means, precisely: keep **shadda** (gemination), **madda** (the long-alif mark) and
**hamzat qaṭʿ** (the written glottal stop) — these stay obligatory; drop the **fatḥa** (the a-vowel)
except where it falls on a wāw (و) or a yāʾ (ي); vocalise uncommon proper names. Write a diacritic
where its absence would change the meaning, and nowhere else.

> Source: مجمع اللغة العربية, Cairo, *قواعد الشكل في الكتب المدرسية*, approved by the council in
> **1959** and the conference in **1960** — «يُهمل الشكل بالفتحة», with shadda, madda and hamzat qaṭʿ
> obligatory. The text appears independently in the Academy's collected decisions and in Hārūn.
> Corroborated from a different direction by the Netflix and World Bank style guides, which both
> make diacritics functional rather than ornamental.

`AR-DIAC-01` reports prose above **200 per 1000**, measured after stripping citations, and only
where the profile declares diacritics `functional` — the `religious` and `children` presets vocalise
by design, so density says nothing about them. **That 200 is provisional and unsourced**: correct
prose measures 9–43, defective prose 770–784, and 200 sits in the empty band between. It is the only
figure in the rule set without an isnad of its own, and it is labelled as such rather than quietly
passed off as transmitted.

**Never read a high diacritic rate as a sign of an elevated register.** In BAREC the rate is flat
across register bands (0.181 / 0.179 / 0.153) and varies more than a hundredfold *within* a single
band by publisher. It measures where a text was published, not how hard it is.

## The three severities

| severity | criterion | what happens |
|---|---|---|
| **`hard`** | unanimous across sources **and** decidable without context | reports, **exits 1** |
| **`recommendation`** | needs judgement, or the evidence does not support blocking | reports, never blocks |
| **`divergence`** | the authorities genuinely disagree | never judges; checks consistency with the declared preset |

**Severity tracks the strength of the chain, never anyone's confidence.** Two rules were demoted on
2026-09-17 for exactly that reason — one on reasoning, one on a corpus count that contradicted an
otherwise impeccable source. The full walkthrough, with a wrong and a right example per rule, is in
[references/hard-rules.md](references/hard-rules.md).

The third severity is what makes this skill honest. Arabic has no single authority: the Cairo
Academy contradicted *itself* on where the hamza sits between its 26th and 46th sessions, Damascus
gives a third answer, and the Damascus preface states outright that no pan-Arab consensus exists.
**A checker that picked a side would be wrong about half the time with the authority of a tool** —
the most expensive kind of wrong for a reader who cannot check the Arabic. No rule carries
`divergence` yet; the engine already supports one.

## Do not invent rules

**This is the section the baseline says matters most.** The failure mode is not missing a defect.
It is stating a rule that does not exist, with authority, to someone who cannot check it.

> **If you cannot name the source, say you are unsure instead of ruling.**
> "I am not certain this is an error; I could not find a source either way" is a correct and useful
> answer. A confident fabricated rule is not.

Every finding you report carries its source, or it carries the word "unsure". There is no third
option.

### The counter-list: things that look like errors and are not

**The dash used for a parenthetical — الشرطة — is legitimate Arabic. Do not flag it.**

```
أعلن أحمد الشربيني – مؤلف هذا الكتاب – أنه لم يقصد ذلك المعنى.
```

Three sources deep. **Aḥmad Zakī Bāšā, 1912**, the founding treatise of modern Arabic punctuation,
lists الشرطة among his ten marks and gives it exactly two uses — separating the turns of a dialogue,
and **opening and closing a parenthetical** (جملة معترضة). **Hārūn** confirms the parenthetical and
adds two further uses. **The World Bank Arabic Style Guide (2004)** gives the example above verbatim.
An agent without this skill called that an English/French import; it is attested from the birth
certificate of Arabic punctuation.

**Joined hundreds — ثلاثمائة — are not an error to correct silently.** The Cairo Academy decided for
the detached ثلاث مائة, with four stated motives. Then it was counted: across all thirty sources of
BAREC the joined form outnumbers the detached **60 to 3**, so the Academy's form is roughly
**5 per cent** of published usage. `AR-ORTH-01` reports it; it does not fail a build. A sourced rule
and an observed rule are not the same thing.

**Digit convention is regional, not a matter of correctness.** Arabic-Indic ٠١٢٣٤٥٦٧٨٩ predominate
in the Machrek, European 0123456789 in the Maghreb. The presets' per-genre assignment is **an
arbitrary project default with no source behind it** — no authority ties a digit set to a genre. It
exists only so that one preset resolves a whole profile. Override it for the reader's region.

**Italics are forbidden by one professional guide and prescribed by another.** Netflix: "Do not use
italics at all in Arabic" — slanting distorts the ductus, the connected stroke joining letters
within a word, and hurts legibility at subtitle sizes. The World Bank recommends them for
subheadings. Neither is wrong: Arabic has no capital letters, so the device other scripts use for
emphasis is simply missing, and the two guides fill the gap differently.

**Hamza seating is the single most disputed point in Arabic orthography.** شؤون (Cairo 26th session,
and Damascus) against شئون (Cairo 46th session). Both are in print. Report the divergence and the
declared school. Never "correct" one into the other.

More, with the positions and the bodies that hold them, in
[references/divergences.md](references/divergences.md).

## What this skill does NOT do

- **It is not a spell checker.** It checks punctuation, encoding, vocalisation density and sentence
  length. It does not know whether a word is misspelled.
- **It does not rule on fiqh, and never overrides a qualified human on scripture.** Every finding
  touching religion here is typographic or editorial. `AR-RELIG-02` (reversed ornate parentheses) is
  `hard` only because it is an *encoding* fact verified in one command; `AR-RELIG-01` (the
  abbreviated prayer on the Prophet) stays a **recommendation** because its four converging fatwas
  were read through a tool summary, not at source. **This project does not fail a text on a
  second-hand religious source.** Text quoting scripture goes to a qualified human before publication.
- **It does not settle where the academies disagree.** See above. That is a feature, not a gap.
- **It does not measure the verbal/nominal ratio, and does not check school, digits or italics.** No
  tagger ships here, and no rule consumes those three fields.
- **It does not try to defeat AI-text detectors.** Over-vocalisation happens to be the most reliable
  tell that Arabic was machine-written, but fixing it is a correctness goal the 1959–60 decision
  already required, not a concealment goal.
- **It is aimed at human-written, legacy, translated and CMS-pasted Arabic**, not at freshly
  generated text — which, measured, already passes its mechanical checks.

## Reference files

- [references/hard-rules.md](references/hard-rules.md) — every rule: what it catches, a wrong and a
  right example, the fix, the source, and why each severity is what it is.
- [references/divergences.md](references/divergences.md) — where the authorities genuinely
  contradict each other, and what the checker does instead of choosing.
- [references/registers.md](references/registers.md) — the length caps and genre ratios, with the
  corpus method, the three caveats, and the segmenter's measured precision.
- [references/religious-register.md](references/religious-register.md) — citation marks, the
  ornate-parenthesis encoding trap, the vocalisation decision, and the human-review gate.
- [references/sources.md](references/sources.md) — one line per rule: the work, the edition, and the
  command or locator to re-verify it yourself.

**Take a rule id, find its line in `sources.md`, follow the locator, read the source. If the source
does not say what the rule says it says, the rule is wrong and should be changed.** That has already
happened three times, and not all in the same direction. The chain is the product.
