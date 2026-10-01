# Sources: where every rule comes from, and how to check it yourself

This file is the skill's chain of transmission. One line per rule id in `assets/rules.json`: the work
it rests on, the edition or the place that copy lives, and what you would do to re-verify it. It
exists because the skill's only real advantage over any competent proofreader is that its verdicts
can be traced — in a language where two qualified editors diverge *legitimately*, an unsourced
verdict is worth nothing. A reader who cannot read Arabic can still audit this file: every line ends
somewhere a third party can reach.

> **The rule of this file: no rule may appear in `assets/rules.json` without a line here.** A rule
> with no line is not a rule with a missing document — it is an unsourced assertion wearing the
> authority of a checker, and `scripts/rules.py` already refuses to load one whose `isnad` field is
> empty. This file is the human half of that same guard.

**Labels follow `registers.md`, with one refinement this file needs.** `[verified]` here means the
source was handled **at first hand** — the document opened and read, or the command executed — and
it says which: *(re-run here)* for the commands below, *(research phase)* for a document read in
full during this project's research but not reopened while writing this file. `[reported]` means
read **through a tool summary**, which is a genuinely weaker link, not a formality. `[unverified]`
means nobody has checked it. The sibling files reserve `[verified]` for work redone while writing
them, so a document marked `[verified] (research phase)` here may appear as `[reported]` there;
that is the same fact under a stricter test, not a contradiction.

## Coverage check, run 2026-09-17

`[verified]` Every id in the table has a line below. Reproduce:

```
python -c "import json; print([r['id'] for r in json.load(open('assets/rules.json',encoding='utf-8'))['rules']])"
```

Output, run from the skill root on 2026-09-17:

```
['AR-TYPO-01', 'AR-TYPO-02', 'AR-TYPO-03', 'AR-ORTH-01', 'AR-SCRIPT-01', 'AR-RELIG-02', 'AR-RELIG-01', 'AR-DIAC-01', 'AR-TANWIN-01']
```

Nine ids, nine lines in the table below (re-run 2026-10-01). **No gap.**

## Rule → source

| rule | the work | edition / where it lives | how to re-verify |
|---|---|---|---|
| **AR-TYPO-01** | Netflix, *Arabic Timed Text Style Guide*, **§21 Punctuation** | `partnerhelp.netflixstudios.com/hc/en-us/articles/215517947`, retrieved 2026-09-17, HTTP 200, 169 121 bytes; archived at `skills-chantier/ecriture-arabe/bibliotheque/netflix-arabic-timed-text-style-guide.html`, sha256 `4b184282ff82fc5e…` | read §21: **"There should be no space before commas, interrogation marks or exclamation marks."** `[verified]` (first-hand, 2026-09-17) — page fetched and read, not summarised. **Source and count both hold:** the sweep measured 17 findings, 17 true, **precision 1.00**, and **zero** in 8 215 sentences of professionally typeset Hindawi prose |
| **AR-TYPO-02** | Unicode Character Database | Python `unicodedata`, stdlib | `python -c "import unicodedata as u; print(u.name(chr(0x060C)))"` → `ARABIC COMMA`; likewise `0x061B`, `0x061F`. `[verified]` (re-run here) |
| **AR-TYPO-03** | Aḥmad Zakī Bāšā, *al-Tarqīm wa-ʿalāmātuh fī al-lugha al-ʿarabiyya* (1912), section 1 | Hindawi / Safahat edition, full text at `safahat.org/books/82047270/1/`; PDF and EPUB at `downloads.hindawi.org/books/82047270` | read section 1 and find «من هذه العلامات ما لا يجوز وضعه مطلقًا، لا في أول السطر ولا في أول الكلام». `[verified]` (research phase) — full text, not a summary |
| **AR-ORTH-01** | Decision of مجمع اللغة العربية, Cairo, *في كتابة الأعداد*; reproduced by ʿAbd al-Salām Muḥammad Hārūn, *Qawāʿid al-imlāʾ wa-ʿalāmāt al-tarqīm* | Academy: *جملة قرارات مجمع اللغة العربية بالقاهرة*, PDF 83 pp., المكتبة الشاملة digitisation. Hārūn: Internet Archive item **`a476n`** | find the decision detaching ثلاث…تسع from مائة and its four motives. **Then count**: the corpus measurement below is what governs the severity. `[verified]` (research phase) — both documents read in full |
| **AR-SCRIPT-01** | Decision of مجمع اللغة العربية, Cairo, *قرارات كتابة الأعلام الأعجمية بحروف عربية*, rule 1; Netflix **§5 Character Names** converging | same Academy collection as above; Netflix archive as for AR-TYPO-01 | find rule 1 (write the foreign name per its pronunciation, Latin form in parentheses in scholarly works); Netflix §5: **"Proper names should be transliterated."** `[verified]` (research phase) Academy; `[verified]` (first-hand) Netflix |
| **AR-RELIG-02** | Unicode Character Database | Python `unicodedata`, stdlib | `python -c "import unicodedata as u; print(u.category(chr(0xFD3F)), u.category(chr(0xFD3E)))"` → `Ps Pe`; `u.mirrored` is 0 for both. `[verified]` (re-run here) |
| **AR-RELIG-01** | Dār al-Iftāʾ al-Miṣriyya fatwa **19288**; Ibn Bāz fatwas **13605** and **7369**; Jordanian Iftāʾ **3607** | not held locally; only fatwa numbers are recorded | **PENDING FIRST-HAND VERIFICATION.** Open each fatwa at its issuing body and read it. Until that is done the rule stays a recommendation. `[reported]` |
| **AR-DIAC-01** | Decision of مجمع اللغة العربية, Cairo, *قواعد الشكل في الكتب المدرسية* (council 1959, conference 1960); corroborated by the World Bank and Netflix guides | Academy collection and Hārūn `a476n` carry the same text independently; World Bank PDF at `meridianlinguistics.com/wp-content/uploads/2019/07/Arabic-World-Bank-Translation-Style-Guide.pdf` | find «يُهمل الشكل بالفتحة» and the obligation on shadda, madda, hamzat qaṭʿ; Netflix **§22 Diacritics**: **"The use of Arabic diacritics (Al Harakat) is required if their absence changes the meaning of the word."** **The 200/1000 threshold is in none of them** — see below. `[verified]` (research phase) Academy, Hārūn, World Bank; `[verified]` (first-hand) Netflix |
| **AR-TANWIN-01** | Netflix, *Arabic Timed Text Style Guide*, **§22 Diacritics**; BAREC Corpus v1.0 (CAMeL Lab) | Netflix archive as for AR-TYPO-01; BAREC on HuggingFace, `CAMeL-Lab/BAREC-Corpus-v1.0`, sha256[:16] of the files read: train `8ff5b1c1202a5993`, dev `e918a2f8e8839081`, test `fa92c19698a60da8` | Netflix §22: tanwīn on the letter before the alif "due to line heights that create overlapping in many cases" — a house rule. Then `python tools/barec_tanwin.py DIR`: before the alif 1 905, on it 418, **7 publishers to 6**. No Arabic-language normative source naming the placement was found, which is why the severity is `divergence`. `[verified]` (first-hand) Netflix; `[verified]` (measured here, 2026-10-01) BAREC |

## The one number with no document behind it

`AR-DIAC-01`'s threshold of **200 diacritics per 1000 Arabic letters is not transmitted from any
authority.** No consulted source states a cut-off. It is inferred from two measurements, is marked
`PROVISIONAL` in the table, and is the only figure in the whole rule set without an isnad of its
own. It is listed here rather than quietly omitted, because a file whose purpose is the chain must
name the one place the chain stops. The reasoning and the numbers are in `hard-rules.md`.

## Claims verified locally by execution

These are not documents but commands. They are the strongest links in the table, because anyone can
re-run them in one line and get the same answer — no library, no download, no account.

| claim | command | result, 2026-09-17 |
|---|---|---|
| Arabic punctuation codepoints | `python -c "import unicodedata as u; print(u.name(chr(0x060C)), u.name(chr(0x061B)), u.name(chr(0x061F)))"` | `ARABIC COMMA ARABIC SEMICOLON ARABIC QUESTION MARK` |
| Ornate parentheses open/close | `python -c "import unicodedata as u; print(u.category(chr(0xFD3F)), u.category(chr(0xFD3E)), u.mirrored(chr(0xFD3F)))"` | `Ps Pe 0` — U+FD3F opens, despite its name |
| Rule table loads and all 139 tests pass | `python -m unittest discover -s tests -t .` | `Ran 139 tests … OK` |
| Diacritic density of a text | `check.diacritic_density(text)` in `scripts/check.py` | 840 per 1000 fully vocalised, 80 reduced to its shadda |
| Hard rules stay inside their false-positive budget | `python -m unittest tests.test_false_positives` | `OK`, `1 hard / 143 sentences = 0.007` against a budget of 0.02 — the one finding a true positive |

`[verified]` (re-run here) — all five executed while writing this file. **The 11,888-sentence
population sweep that demoted AR-ORTH-01 (17 findings, 0 true positives, precision 0.00) is not one
of these:** it was run once, in 2026-09-17, over a corpus this repository does not ship, and it is
recorded in the docstring of `tests/test_false_positives.py`. Re-running it means downloading BAREC
again. `[reported]` until somebody does.

## Corpus measurements

**BAREC Corpus v1.0**, CAMeL Lab, on HuggingFace as `CAMeL-Lab/BAREC-Corpus-v1.0`; splits `train`,
`dev`, `test`; 69 441 sentences, thirty sources. `[verified]` (research phase) — downloaded and
measured first-hand, not taken from a published paper.

It carries three of this skill's load-bearing numbers, and each is a *count*, not an opinion:

- the sentence-length caps by audience in `registers.md` (68 677 prose sentences, poetry excluded);
- the **60 to 3** ratio of joined to detached hundreds across all thirty sources, which demoted
  `AR-ORTH-01`;
- the near-binary split of vocalisation by source — a source is either near 0 % or near 100 %
  vocalised — which, with this project's RED baseline, produced the empty band the AR-DIAC-01
  threshold sits in.

The **false-positive sweep** ran the hard rules over the 443-document Hindawi + Wikipedia
population, 11,888 sentences. `[verified]`, recorded in `tests/test_false_positives.py`. The
**RED baseline** of 2026-09-17 — five scenarios run by agents without this skill — is in
`tests/baseline/results-red.md` and supplies the 784 / 770 / 43 / 9 per-1000 diacritic figures and
the invented-dash incident behind the counter-rule in `hard-rules.md`.

## Primary sources behind the skill as a whole

### Read at first hand `[verified]` (research phase)

- **Aḥmad Zakī Bāšā, *al-Tarqīm wa-ʿalāmātuh fī al-lugha al-ʿarabiyya* (1912).** The founding text
  of modern Arabic punctuation, written at the request of the Egyptian Minister of Public
  Instruction. Zakī states his own method: cross the classical treatises on الوقف والابتداء (where a
  Qurʾan reciter may pause) with European typographic usage, and keep only the overlap — so the
  system rests on Arabic recitation, not on a French model. He names the ten marks and classes them
  by *degree of pause*, not by shape. Full text: `safahat.org/books/82047270/1/`.
- **ʿAbd al-Salām Muḥammad Hārūn, *Qawāʿid al-imlāʾ wa-ʿalāmāt al-tarqīm*.** Internet Archive item
  **`a476n`** (DjVu OCR text and page images). Hārūn is the editor who established the text of
  Sībawayh's *Kitāb* and of al-Jāḥiẓ; when he states a punctuation rule he states it from the most
  demanding editorial practice in the language. He also reproduces the Academy decisions on
  punctuation (1932) and on vocalisation (1959–60). **OCR caveat, recorded during research:** parts
  of the scan are poor and the tables are partly destroyed, so any quotation must be re-checked
  against the page images before it is published as verbatim.
- **مجمع اللغة العربية, Cairo — *جملة قرارات***. PDF, 83 pp., المكتبة الشاملة digitisation, read
  through in full during research and segmented into 244 decisions. The collection is ordered
  alphabetically, which is what allowed the segmentation to be checked independently.
- **مجمع اللغة العربية, Damascus — قواعد الإملاء.** Source of the third position on the hamza and of
  the preface conceding that no pan-Arab orthographic consensus exists. Used in `divergences.md`.
- **The World Bank, *Translation Style Guide, Arabic Edition*, v1.0, June 2004, 24 pp.** PDF at
  `meridianlinguistics.com/wp-content/uploads/2019/07/Arabic-World-Bank-Translation-Style-Guide.pdf`.
  Text extracted and read. Supplies the worked parenthetical-dash example, the functional-diacritics
  corroboration, and the italics position in `divergences.md`.
- **Netflix, *Arabic Timed Text Style Guide*.** `partnerhelp.netflixstudios.com/hc/en-us/articles/215517947`,
  retrieved 2026-09-17, HTTP 200, 169 121 bytes; archived at
  `skills-chantier/ecriture-arabe/bibliotheque/netflix-arabic-timed-text-style-guide.html`
  (sha256 `4b184282ff82fc5e…`) so the claims survive the page changing. **Promoted from
  `[reported]` to first-hand on 2026-09-17**, which is what allows AR-TYPO-01 to stand at `hard` on
  a documentary source rather than on a summary of one. Four sections are load-bearing, each read in
  the archived copy: **§5** "Proper names should be transliterated." (AR-SCRIPT-01); **§12**
  "Do not use italics at all in Arabic." (the divergence with the World Bank in `divergences.md`);
  **§21** the no-space-before-marks sentence (AR-TYPO-01); **§22** "The use of Arabic diacritics
  (Al Harakat) is required if their absence changes the meaning of the word." (AR-DIAC-01). §22 also
  gives the reason behind a detail this project had recorded only as "technical considerations":
  Netflix places tanwīn on the letter *before* the alif "due to line heights that create overlapping
  in many cases" — a house decision with a typesetting motive, not a grammatical ruling.

### Read only through a tool summary `[reported]`

**Treat everything in this section as unverified detail on a probably-sound claim** — and treat any
*codepoint* in it as wrong until re-checked. That is not caution in the abstract: a summariser
rendered the ellipsis as "U+2086", and local verification showed U+2086 is SUBSCRIPT SIX. The
summariser in question was the one used on the two style guides; the Netflix guide has since been
read at source, so that caution now attaches to the W3C document alone.

- **W3C, *Arabic & Persian Layout Requirements* (ALReQ)**, `w3.org/TR/alreq/`. Source of the
  Machrek / Maghreb digit-set divergence in `divergences.md`. Still summary-read.
- **The four fatwas behind AR-RELIG-01** — Dār al-Iftāʾ al-Miṣriyya 19288, Ibn Bāz 13605 and 7369,
  Jordanian Iftāʾ 3607. **Their isnad in the rule table reads `PENDING FIRST-HAND VERIFICATION`, and
  that status must not be upgraded until somebody opens the four fatwas at source.** It is the whole
  reason AR-RELIG-01 is a recommendation and not a hard rule: this project does not fail a text on a
  second-hand religious source. Four converging fatwas would meet the unanimity half of the `hard`
  criterion — if they had been read.
- **Dār al-Iftāʾ al-Miṣriyya fatwa 12390 and IslamWeb fatwa 30196**, on writing isolated verses
  outside a muṣḥaf (a printed copy of the Qurʾan itself) in standard orthography. Quoted in `religious-register.md`, same reservation.

## What a reader should do with a finding

Take the rule id, find its line in the table above, follow the locator, and read the source. If the
source does not say what the rule says it says, the rule is wrong and should be changed — that
outcome is the point of publishing this file, not an embarrassment to be avoided. It has already
happened three times on 2026-09-17, and not all in the same direction: `AR-ORTH-01` and
`AR-SCRIPT-01` were **demoted** after exactly this kind of re-examination, while `AR-TYPO-01`'s
source was **strengthened** — fetched, read and archived — so that a rule already at `hard` finally
rested on a document somebody had opened. Re-examination is not a demotion procedure. It is the
procedure; the direction is whatever the source turns out to say. The reasoning is in
`hard-rules.md`.
