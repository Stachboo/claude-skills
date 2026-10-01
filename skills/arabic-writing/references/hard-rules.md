# Hard rules: what blocks a build, what only reports, and why

This file walks every rule in `assets/rules.json` — what it catches, a wrong and a right example, the
fix, and the source quoted from the rule's own `isnad` field — so that a reader who does not read
Arabic can check a verdict against its source instead of trusting the tool. A rule's severity tracks
the strength of its chain, so the severities come first. Editions are in `sources.md`.

> **This file is at its length budget. The next rule splits it; it does not squeeze it.** Compressing
> the reasoning to fit is how a reference decays into a list, and the reasoning is the part a reader
> cannot reconstruct from `assets/rules.json`.

**Labels follow `registers.md`:** `[verified]` = measured first-hand here; `[reported]` = read through
a summary or carried from research. **Inventory read from the table on 2026-10-01:** nine rules —
four `hard`, four `recommendation`, one `divergence`; `python -m unittest discover -s tests -t .` →
`Ran 158 tests … OK (skipped=2)`.

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

# The recommendations

## AR-DIAC-01 — over-vocalised running prose

Catches running prose carrying full تشكيل (*tashkīl*, the marks above and below letters for short
vowels and gemination), which belongs on Qurʾanic and hadith citations, not the prose around them. It
is the one defect the RED baseline showed occurring in machine-written Arabic.

- wrong — `إِنَّ الزَّكَاةَ رُكْنٌ مِنْ أَرْكَانِ الْإِسْلَامِ.` → **840** per 1000
- right — `إنّ الزكاة ركن من أركان الإسلام.` → **40** per 1000 — `[verified]`, `check.diacritic_density`
- **Fix:** keep shadda (gemination), madda (the long-alif mark) and hamzat qaṭʿ (the written glottal
  stop); drop the fatḥa (the a-vowel) except on wāw and yāʾ; vocalise uncommon proper names.

> Majma al-Lugha al-Arabiyya, Cairo, 'qawa'id al-shakl fi al-kutub al-madrasiyya', approved by the
> council 1959 and the conference 1960: full vocalisation for Qur'anic verses and hadith at every
> level; elsewhere 'yuhmal al-shakl bi-l-fatha' while shadda, madda and hamzat qat' remain
> obligatory. Corroborated independently by the World Bank Arabic Style Guide 2004 and the Netflix
> Arabic Style Guide, which both make diacritics functional. Measured on this project's RED baseline
> 2026-09-17: generated prose reached 784 and 770 diacritics per 1000 Arabic letters, against 9 for
> a news dispatch.

**PROVISIONAL threshold — 200 per 1000, the only figure in this table with no isnad of its own.** No
consulted source states a cut-off: the number is *inferred from measurement*, not transmitted from an
authority, and is marked provisional on purpose. Correct measurements run 9–43 and defective ones
770–784, leaving an empty band; 200 is the log-midpoint √(43 × 770) = 182 rounded up — 4.7× above the
highest correct measurement, 3.9× below the lowest defective one, rounded **up** so the residual risk
falls on the miss. **Re-measure and move it if correct, functionally vocalised prose is found above
100.**

Mechanics: `kind` is `ratio`, `pattern` is `null`, and `scripts/check.py` owns it. It measures only
**after** removing every span between the ornate parentheses and between the guillemets, since full
vocalisation is *required* inside a citation by the same decision that discourages it outside; and it
fires only where the profile declares diacritics `functional`.

## AR-ORTH-01 — hundreds written joined

Reports the numerals three to nine written joined to مائة (*miʾa*, "hundred") instead of detached.
**Demoted from `hard` on 2026-09-17 on measurement** (below) — no wrong/right framing applies, which
*is* the finding.

- reports — `في المدينة ثلاثمائة مسجد.` → the Academy's form — `في المدينة ثلاث مائة مسجد.`
- **Fix as stated:** write ثلاث مائة … تسع مائة with a space between them. (Known limitation: the
  pattern matches bare letters, so a vocalised joined form slips through.)

> Decision of Majma al-Lugha al-Arabiyya, Cairo, 'fi kitabat al-a'dad: fasl thalath ila tis' an
> mi'a', four motives given (joined form is obscure; detachment attested in al-Tabari; the case
> ending falls on the first word; easier for learners). Reproduced verbatim by Abd al-Salam Muhammad
> Harun, Qawa'id al-imla wa-alamat al-tarqim. Archive.org item a476n.

## AR-RELIG-01 — the abbreviated prayer on the Prophet

Reports `(ص)` or `(صلعم)` in place of the full formula.

- reports — `قال النبي (ص) في الحديث.` → preferred — `قال النبي ﷺ في الحديث.` (U+FDFA), or the
  formula written out in full
- **Fix:** replace with ﷺ or the full formula. The trailing `\s*\)` keeps a page citation out of
  range: `(ص ١٢)` does not match.

> PENDING FIRST-HAND VERIFICATION. Convergence reported by Dar al-Ifta al-Misriyya fatwa 19288, Ibn
> Baz fatwas 13605 and 7369, and Jordanian Ifta 3607 - but these were read via tool summary, not at
> source. Deliberately kept a recommendation, not a hard rule, until read directly: this project
> does not fail a text on a second-hand religious source.

**Do not upgrade that status.** Four converging fatwas would satisfy the unanimity half of `hard` if
they had been read; they have not been. Severity tracks the chain, not the confidence — and see the
human-review gate in `religious-register.md`: nothing here is a religious ruling.

## AR-SCRIPT-01 — bare Latin script inside an Arabic sentence

Reports a run of Latin script with Arabic on both sides. **Demoted from `hard` on 2026-09-17 on reasoning** (below).

- reports, correctly — `كتبت Umm Salama رسالة طويلة.` → `كتبت أم سلمة رسالة طويلة.`
- reports, and should not — `تعمل شركة Microsoft العالمية في المدينة.`
- **Fix:** write the name in Arabic script; the Latin original may follow in parentheses.
- `[verified]` both lines were run through `run_rules` here; both fire. The second is the false
  positive that cost the rule its `hard` severity.

> Majma al-Lugha al-Arabiyya, Cairo, 'qararat kitabat al-a'lam al-a'jamiyya bi-huruf arabiyya', rule
> 1: write the foreign name per its pronunciation, with the Latin form between parentheses in
> scholarly works, e.g. Bordeaux. Netflix Arabic Style Guide converges: 'Proper names should be
> transliterated.'

# The two demotions of 2026-09-17, and the lesson

Both kept their patterns — neither was wrong about what it matched — and both lost `hard`, on
**different halves of the criterion**, which is why both are recorded.

**AR-SCRIPT-01, on reasoning.** The case the rule was written for — a name of Arabic origin romanised
and left in Latin script inside Arabic prose, `Umm Salama` where أم سلمة was meant — **is not
mechanically distinguishable from a legitimate foreign brand name**, as `شركة Microsoft العالمية`
shows above. Bare Latin brand names in contemporary Arabic web copy are a usage the Academy decision
predates, so unanimity fails. The RED baseline added a second reason: models already transliterate
Arabic-origin names unprompted, so as a hard rule it would fire almost only on legacy web copy, where
a false positive costs more than a miss.

**AR-ORTH-01, on measurement.** Its source is excellent by every criterion but one: a Cairo Academy
decision, four motives stated, reproduced verbatim by the reference editor of the Arabic heritage.
Then it was counted. Across all thirty sources of BAREC the joined form outnumbers the detached
**60 to 3** — **95 per cent of published usage**, spread over literature, children's publishing,
classical narrative and encyclopedia, so not one register's quirk. A sweep of **11,888 sentences**
returned **17 findings, 0 true positives, precision 0.00**. The decision is an *argued reform*, not a
report of settled usage; a reform publishing ignores 95 per cent of the time fails the unanimity half
of `hard`. It still reports; it no longer fails a build.

> **The lesson, and it governs every future rule: a sourced rule and an observed rule are not the
> same thing. A rule reaches `hard` only with a source AND a corpus count.** AR-ORTH-01 is the case
> where they come apart with the source impeccable; AR-TYPO-01 is the case where they agree.

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
