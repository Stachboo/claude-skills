# Registers: what to aim for, and what the numbers do not mean

This file gives the writing targets this skill checks against — sentence length by audience, and
sentence type by genre — together with where each number came from and where it stops being valid.
It is written for a reader who may not read Arabic: the targets are counts and ratios, not
judgements of style. Read it before trusting a length verdict, and read the caveats before
reporting one to an author.

**Labels.** `[verified]` marks something measured or reproduced first-hand while writing this file,
with the command to redo it. `[reported]` marks something taken from a source read through a
summary, or from this project's earlier research phase rather than reopened here. `[unverified]`
marks a claim nobody has checked. Documentary citations carry their work and edition inline so a
reader can promote them to `[verified]` independently.

## Sentence length by audience

Measured on the BAREC Corpus v1.0 (CAMeL Lab), train + dev + test, 68 677 prose sentences,
classical poetry excluded. "Words" means tokens containing at least one Arabic letter; punctuation
and bare numbers are not counted.

| audience | p25 | median | p75 | cap (p90) |
|---|---|---|---|---|
| foundational | 3 | 6 | 10 | **15** |
| advanced | 7 | 13 | 20 | **26** |
| specialized | 13 | 20 | 28 | **37** |

`[verified]` Reproduced exactly on 2026-09-17. The three audiences are BAREC's own
`Readability_Level_3` column (values 1, 2, 3), **not** its `Text_Class` column — those are different
groupings, and `Text_Class` yields different numbers. "Classical poetry excluded" means dropping the
764 rows whose `Source` is `Hanging Odes` (the المعلقات, the pre-Islamic odes): 69 441 rows minus
764 leaves exactly the 68 677 above. Reproduce over the three parquet files:

```python
# a word = a whitespace token containing at least one Arabic letter
sum(1 for t in sentence.split()
    if any(0x0600 <= ord(c) <= 0x06FF and unicodedata.category(c) == 'Lo' for c in t))
# then numpy.percentile([...], [25, 50, 75, 90]) per Readability_Level_3 band
```

BAREC's own `Word_Count` field was not used: it counts punctuation as tokens and disagrees with a
whitespace split in 76% of rows (`assets/registers.json`, field `word_definition`).

## Caveat 1 — these are caps to watch sentence by sentence, not averages

BAREC's annotation rule is that a passage takes the level of its single most difficult element. A
text averaging 13 words — the advanced median — that contains one 40-word sentence is not an
advanced text, because 40 exceeds the advanced cap of 26. So the cap column is a per-sentence
ceiling, tested sentence by sentence, and it is stated as a negative on purpose: the check does not
sort a text into a band, it reports the sentences that exceed the band the author declared.
Averaging over a document hides exactly the sentence the reader will trip on: a text can sit
comfortably under the mean while failing every reader it was written for.

## Caveat 2 — above level 14, length stops indicating difficulty

On BAREC's finer 19-level scale, median sentence length climbs to level 14 and then falls:

| level | 10 | 11 | 12 | 13 | **14** | 15 | 16 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|---|---|---|---|
| median words | 10 | 15 | 12 | 15 | **20** | 18 | 18 | 11 | 9 | 9 |

`[verified]` measured over train + dev + test with the same word definition. At the top of the scale
the `Hanging Odes` are the largest single source — 199 of 480 rows at level 17 (41%), 77 of 103 at
level 18 (75%), 89 of 116 at level 19 (77%). These are short verses with rare vocabulary. Level 17
also carries the highest lexical diversity of any level large enough to compare: type-token ratio
0.761 on a fixed 2 000-token sample, against about 0.73 for levels 12–16. Levels 18 and 19 hold too
few tokens (1 222 and 1 085) to compare at that sample size, so their diversity is `[unverified]`.

The practical consequence: **the hardest Arabic is not the longest.** A short line can be the
hardest thing in a document. A length check cannot see that, and must never be reported as if it
could.

## Caveat 3 — the diacritic rate measures the source, not the register

Diacritics (تشكيل, *tashkīl*: the small marks written above and below letters for short vowels and
gemination) are optional in most modern Arabic prose. It is tempting to read a high rate as a sign
of an elevated register. In BAREC that reading is simply wrong.

`[verified]` Mean diacritics per Arabic letter, over train + dev + test:

- across the three register bands: **0.181 / 0.179 / 0.153** — essentially flat;
- inside the *advanced* band alone, by source: Emarati Curriculum 0.456, Hindawi 0.151, Wikipedia
  0.025, Green Library 0.015, Kalima 0.008, Majed 0.007, ArabicMMLU 0.004, Constitutions 0.003.

That is a spread of more than a hundredfold **within one register band**, against no meaningful
movement **between** bands. At corpus level, five sources are effectively fully vocalised (Quran
0.832, WikiNews 0.828, Hadith 0.824, Old and New Testament ≈ 0.80) and eleven sit below 0.01. The
rate is a property of where a text was published, not of how hard it is.

**Never use the diacritic rate as a register signal.** It is a useful check against over-application
— see `religious-register.md` for the decision that governs vocalisation, and for what an unassisted
model actually produces — but it says nothing about audience level.

## Verbal-sentence ratio by genre

Arabic sentences divide into verbal (جملة فعلية, opening on a verb) and nominal (جملة اسمية,
opening on a noun). The proportion between them is a genre marker: news leans verbal, analysis and
law lean nominal.

| genre | news | religious | children | reference | literary | legal | magazine |
|---|---|---|---|---|---|---|---|
| verbal ratio | 0.69 | 0.62 | 0.61 | 0.51 | 0.50 | 0.45 | 0.41 |

`[reported]` Measured with CAMeL Tools part-of-speech tagging over the same corpus during this
project's research phase; not reproducible from this repository, which ships no tagger. The same
research found the ratio moves only about 2.5 points across the whole readability scale (45.2% to
47.8%) while moving more than forty points across genres — so it tracks genre, not difficulty
(`assets/registers.json`, field `verbal_ratio_rule`).

**Limitation, stated plainly: the free skill cannot measure this.** Deciding whether a sentence is
verbal or nominal requires a part-of-speech tagger, which lives in a separate paid pack. The ratios
above are guidance for the writing side. `check.py` does not verify them, and no report should imply
that it did.

## Segmenter agreement — the provenance record

Every length figure depends on where sentences are cut. Here is what the cutter actually achieves,
published in full rather than summarised:

```
corpus: CAMeL-Lab/BAREC-Corpus-v1.0, dev split, 7310 rows read
        data/dev-00000-of-00001.parquet
        sha256[:16] of the file read = e918a2f8e8839081
sentence recall (exact string match) : 2296/7310 = 31.4%
ceiling for any terminator-based rule: 2769/7310 = 37.9%
recall as a share of that ceiling    : 82.9%
boundary precision                   : 3349/3816 = 87.8%
boundary recall                      : 3349/7116 = 47.1%
boundary F1                          : 61.3%
```

`[verified]` Re-run on 2026-09-17: every figure identical, including the file hash. Reproduce with
`BAREC_DIR=... python -m unittest tests.test_segment` — the harness expects the downloaded file
placed in that directory under the name `dev.parquet`.

### Frame the 31.4% correctly, or it misleads

Alone, "31.4% recall" reads as a broken segmenter. It is not.

Only **52.2%** of BAREC's gold "sentences" end in any terminator at all (3 817 of 7 310 on the dev
split — `[verified]`, measured in the same run). The rest are headlines, bylines, dates and exercise
fragments. The measurement harness joins a document's sentences with spaces, which destroys the line
breaks that are the only signal separating those unpunctuated fragments. Hence the 37.9% ceiling: no
punctuation-based rule of any kind can beat that on such input. We reach 82.9% of it.

The honest reading is therefore: on prose that is actually punctuated, the cutter does most of what
punctuation permits; on headline-like fragments it cannot find a boundary that the input no longer
contains.

## Error direction: protect precision, not recall

The two ways a segmenter can be wrong are not symmetric, and the asymmetry decides which number to
defend.

- **Under-splitting** merges two sentences into one. The measured length is then too long and the
  cap fires on a text that was fine — a **false FAIL**. Conservative and safe: a human looks, and
  sees that nothing is wrong.
- **Over-splitting** cuts one sentence into two. Each half comes in under the cap, and a genuinely
  over-long sentence passes unnoticed — a **false PASS**. The check silently fails to do its job.

Precision (87.8%) is therefore the number to protect. Raising recall at its expense would make every
length cap in this file quietly permissive — the failure mode a reader cannot detect, because
nothing is reported.
