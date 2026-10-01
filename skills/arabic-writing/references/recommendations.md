# Recommendations: what reports and never blocks, and why

The four rules of `assets/rules.json` at severity `recommendation`, walked the same way as
`hard-rules.md` walks the blocking ones: what each catches, a wrong and a right example, the fix, and
the source quoted from the rule's own `isnad`. Each is here because its evidence does not support
blocking — two of them were `hard` until 2026-09-17, and the last section says why they were demoted.

Split out of `hard-rules.md` on 2026-10-01, unchanged.

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

