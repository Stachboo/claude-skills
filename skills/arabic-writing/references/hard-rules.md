# Hard rules: what blocks a build, and why

This file walks every **hard** rule in `assets/rules.json` — what it catches, a wrong and a right example, the
fix, and the source quoted from the rule's own `isnad` field — so that a reader who does not read
Arabic can check a verdict against its source instead of trusting the tool. A rule's severity tracks
the strength of its chain, so the severities come first. Editions are in `sources.md`.

> **Split on 2026-10-01, as this note required.** The recommendations, and the two demotions of
> 2026-09-17 that produced two of them, moved to `recommendations.md` when `AR-ORTH-02` arrived.
> Compressing the reasoning to fit is how a reference decays into a list, and the reasoning is the
> part a reader cannot reconstruct from `assets/rules.json`.

**Labels follow `registers.md`:** `[verified]` = measured first-hand here; `[reported]` = read through
a summary or carried from research. **Inventory read from the table on 2026-10-01:** ten rules —
five `hard`, four `recommendation`, one `divergence`; `python -m unittest discover -s tests -t .` →
`Ran 170 tests … OK (skipped=2)`.

## The three severities

| severity | criterion | what the checker does |
|---|---|---|
| **`hard`** | unanimous across sources **and** decidable without context | reports, and **exits non-zero** |
| **`recommendation`** | needs judgement, or the evidence does not support blocking | reports, **never blocks** |
| **`divergence`** | the authorities genuinely disagree | never judges the spelling; checks consistency with the declared preset |

The third is unusual, and it is what makes this skill honest. Arabic has no single authority: the Cairo
Academy contradicted *itself* on where the hamza sits between its 26th and 46th sessions, Damascus
gives a third answer, and the Damascus preface states outright that no pan-Arab consensus exists
(`divergences.md`). A checker that picked a side would be wrong about half the time with the authority
of a tool. **One rule carries `divergence`: `AR-TANWIN-01`**, the placement of tanwīn al-fatḥ. It is
walked through in `divergences.md`, not here, because it never judges a text.

# The hard rules

## AR-RELIG-02 — reversed ornate parentheses

Catches a Qurʾanic citation whose ornate parentheses (﴿ ﴾, the قوسان قرآنيان, used instead of quotation
marks so Qurʾanic text is distinguishable from the author's own words) are the wrong way round. They
are *named* backwards relative to what they do, and are not mirrored, so nothing corrects the writer.

- wrong — `قال تعالى: ﴾إنا أعطيناك الكوثر﴿.` → right — `قال تعالى: ﴿إنا أعطيناك الكوثر﴾.`
- **Fix:** write U+FD3F first, U+FD3E last.

> Verified locally: `unicodedata.category(chr(0xFD3F)) == 'Ps'` (open punctuation) and
> `category(chr(0xFD3E)) == 'Pe'` (close), while `mirrored == 0` for both, so the bidi engine does
> not reorder them.

`[verified]` re-run here: `Ps Pe 0 0`. Its isnad is a command, not a document — which is why it can be
`hard` where the skill otherwise refuses to block on religion: an encoding fact, not a ruling.

## AR-TYPO-01 — space before an Arabic mark

Catches a space before a comma, semicolon, question or exclamation mark in Arabic text.

- wrong — `الشركة رائدة ، وهي كبيرة.` → right — `الشركة رائدة، وهي كبيرة.`
- **Fix:** remove the space.

> Netflix Arabic Timed Text Style Guide: 'There should be no space before commas, interrogation
> marks or exclamation marks.' No consulted source permits it. Note: this differs from French,
> where ; ? ! take a non-breaking space.

`[verified]` §21, fetched and archived 2026-09-17 (`sources.md`). **This rule passes the standing test
on both halves**: a first-hand source, and a count agreeing with it — 17 findings on an
11,888-sentence sweep, **17 true, precision 1.00**, none in 8 215 sentences of typeset Hindawi prose.

**DEFERRED, measured 2026-09-17 — read before trusting a clean result.** The left-hand side
under-detects: **recall over an annotated set was 0.62, 9 misses out of 24**. It requires an Arabic
letter or mark immediately before the space, so the rule misses whenever the preceding character is
`)`, a Latin letter, `.` or an ASCII digit — the measured example is `٩٠٠ كم٢ ، أما`. Not widened
alongside the right-hand class on purpose: the left side admits Latin and digit contexts and needs
its own false-positive sweep first. **A pass is not a guarantee of no space before a mark.**

## AR-TYPO-02 — Latin punctuation inside Arabic

Catches a Latin comma, semicolon or question mark attached to Arabic text.

- wrong — `الشركة رائدة, وهي كبيرة.` → right — `الشركة رائدة، وهي كبيرة.`
- **Fix:** replace `,` with `،` (U+060C), `;` with `؛` (U+061B), `?` with `؟` (U+061F).

> Codepoints verified locally with Python unicodedata: U+060C ARABIC COMMA, U+061B ARABIC
> SEMICOLON, U+061F ARABIC QUESTION MARK. Reproduce:
> `python -c "import unicodedata as u; print(u.name(chr(0x060C)))"`

`[verified]` re-run here: `ARABIC COMMA | ARABIC SEMICOLON | ARABIC QUESTION MARK`. The left-hand
class stops at U+065F, excluding the Arabic-Indic digits: `١,٥` is a number separator in legacy
Arabic, not sentence punctuation, and flagging it would be a false positive on a blocking rule.

**AR-TYPO-01 and AR-TYPO-02 form a repair sequence, not a composition.** One finding at a time, never
both at once: AR-TYPO-02 needs the Latin mark adjacent to an Arabic letter, so a space beside it keeps
this rule silent. Two genuine faults, surfaced one after the other as each is fixed, each carrying its
own source — and before the 2026-09-17 widening this text fell between both rules and yielded nothing
at all. `[verified]`, all three run through `run_rules` here:

- `الشركة رائدة , وهي كبيرة.` → `AR-TYPO-01`, the space (Netflix §21)
- `الشركة رائدة, وهي كبيرة.` → `AR-TYPO-02`, the glyph (`unicodedata` codepoints)
- `الشركة رائدة، وهي كبيرة.` → clean

## AR-TYPO-03 — a mark opening a line

Catches a line opening on `، ؛ . : ؟ ! » )` — marks that may never begin a line or an utterance.

- wrong — a break after `الشركة رائدة`, next line starting `، وهي كبيرة.`
- right — the comma stays behind: `الشركة رائدة،` then `وهي كبيرة.`
- **Fix:** move the mark to the end of the previous line.

> Ahmad Zaki Pasha, al-Tarqim wa-alamatuh fi al-lugha al-arabiyya (1912), section 1: 'min hadhihi
> al-alamat ma la yajuz wad'uhu mutlaqan, la fi awwal al-satr wa-la fi awwal al-kalam'. Full text:
> safahat.org/books/82047270/1/

("Among these marks are some that may not be placed at all, neither at the head of a line nor at the
head of an utterance.") **Scope limit, from the rule's own note:** Zakī's rule is about the
*typographic* line; the pattern sees only the *source* line, a paragraph in a plain-text or Markdown
file. It errs safe: a paragraph opening on a comma is wrong under any line breaking.

## AR-ORTH-02 — hamzat qaṭʿ or madda left off

Catches one of 22 words written with a bare alif where the hamza (ء on the alif) or the madda (آ)
belongs: `الى` for `إلى`, `اذا` for `إذا`, `او` for `أو`, `ان` for `أن`/`إن`, `الان` for `الآن`, `الاف`
for `آلاف`… The list is closed on purpose: every bare form on it is a misspelling and never another
word, which is what makes the rule decidable without a morphological analyser.

- wrong — `ذهب الولد الى المدرسة.` → right — `ذهب الولد إلى المدرسة.`
- **not flagged** — `واحد` (*wāḥid*, "one", not و + احد), `فان` (*fānin*, "perishing", Q 55:26),
  `عقد القران` (*al-qirān*, the marriage contract, which is why القرآن is not on the list).
- **Fix:** write the hamza above the alif with fatḥa or ḍamma, below it with kasra; write آ where a
  hamza is followed by a long alif.

> Majma al-Lugha al-Arabiyya, Damascus, Qawa'id al-imla, bab 1, 'al-hamza fi awwal al-kalima': the
> hamza of qat' is written and the hamza of wasl is not; it sits above the alif with fatha or damma and
> below it with kasra; a hamza followed by a long alif is written as one alif carrying the madda.
> Harun, Qawa'id al-imla wa-alamat al-tarqim: 'tursam hamzat al-qat' fi awwal al-kalima alifan ma'a
> wad' alamat al-qat' (hamza) fawqaha fi halat al-fath wa-l-damm, wa-tahtaha fi halat al-kasr'.

**Why it is `hard`: both halves of the criterion hold.** The source half: two normative works, read
in the project's library, and no consulted source permits leaving the hamza off. These are rules of
orthography for all writing — not the 1959–60 school-book vocalisation decision, which is a different
text with a narrower scope. The count half, on BAREC v1.0, functional prose, 2026-10-01 `[verified]`:
the hamza is written on **25 636 of 26 061** occurrences of the listed words (98.4%) — Hindawi omits
it on 0 of 7 943, Green Library on 0 of 1 483, Wikipedia on 0.2%. The omissions come from typed and
pasted text: constitutions 11.4%, exam questions 8.0%, subtitles 15.4%, song lyrics 38.8% — exactly
the legacy and CMS copy this checker exists for. **Precision, read by hand: 53 of 53** — 40 random
hits and every hit in the professional publishers.

**Three false positives were found and fixed before it shipped**, all by reading hits rather than
counting them. A prefix made a real word (`واحد` read as و + احد: "ahd" measured 30% missing until
prefixes were allowed word by word). A bare form was another word (`القران` in `عقد القران`). And a
word boundary that only knew U+0621–U+064A found `ان` inside `طغیان` written with the Farsi yeh U+06CC,
and inside quoted Persian. The boundary now covers the whole Arabic script.

**Known limit:** only the 22 listed words are checked. The rule under-detects by design.

# Counter-rule: a missing shadda is not a fault

**The skill must not flag a missing shadda (ّ, gemination) in functional prose.** On BAREC v1.0,
functional prose, 2026-10-01 `[verified]`, the shadda is absent on **95.5%** of 10 218 words that
always carry a geminated consonant (ثم، كل، مرة، قوة، خاصة…) — and the professional publishers are
no exception: Hindawi 89.8%, Wikipedia 93.9%, Majed 100%. Leaving it off is how published Arabic is
written.

The 1959–60 Cairo decision does say «يُلتزم وضع الشدة، والمدة، وهمزة القطع». **Read its scope before
quoting it:** that clause belongs to the *middle-school* tier of a decision about textbooks, in a
regime where word endings are vocalised. For the secondary tier — the nearest to an adult reader — the
same decision says the opposite: vocalise only where the pupil is expected to err. Madda and hamzat
qaṭʿ are another matter: they are letters (آ أ إ, U+0622, U+0623, U+0625), governed by orthography,
and `AR-ORTH-02` checks them. The shadda is a mark, and in functional prose it is written where its
absence would mislead — the Netflix and World Bank principle — not everywhere.

# Counter-rule: the dash — الشرطة — is legitimate Arabic

**The skill must not flag the dash used for a parenthetical.** It is recorded here as part of the
table although it blocks nothing, because it is a correction, not an omission. The sources name the
mark الشرطة, "the dash", and **none of them states a width**; the attested example below uses U+2013.

- legitimate, do not flag — `أعلن أحمد الشربيني – مؤلف هذا الكتاب – أنه لم يقصد ذلك المعنى.`

`[verified]` run through `run_rules` here: clean, no finding. The chain, three sources deep:

- **Aḥmad Zakī Bāšā, 1912** — the founding treatise of modern Arabic punctuation — lists الشرطة (the
  dash) among his ten marks and gives it exactly **two** uses: separating the turns of a dialogue,
  and **opening and closing a parenthetical** (جملة معترضة) that itself contains a comma or another.
- **Hārūn** confirms the parenthetical and adds two more uses: after the number of a listed item at
  the head of a line (`أولًا -`), and between the two pillars of a sentence when the first is long.
- **The World Bank Arabic Style Guide (2004)** gives the worked example above verbatim. All three
  `[reported]` — read first-hand during the research phase, not reopened here.

**Why this is here.** A measured baseline on 2026-09-17 caught an agent reviewing Arabic *without*
this skill and condemning that dash in these words: "Em dashes used as parenthetical brackets. This
is an English/French typographic convention imported into Arabic; standard Arabic uses parentheses or
commas for a parenthetical clause." That is false — the usage is attested since the birth certificate
of Arabic punctuation — and it **carried no source, nor did any of its other fourteen claims**
(`[verified]`, `tests/baseline/results-red.md`). That agent found nearly every real defect in the
degraded text, as a good model does; what it *also* did was **invent a rule and state it with
authority**, indistinguishable to a reader who cannot read the Arabic. **Inventing a rule is the
failure this file exists to prevent, and the counter-rule is how: by writing into the table itself
the things that must not be flagged.**
