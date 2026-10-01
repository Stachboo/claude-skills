# The religious register: citation, vocalisation, and what must not be judged here

Arabic prose that quotes scripture obeys conventions that do not apply to the prose around it:
different quotation marks, different vocalisation, and a different relationship to punctuation
altogether. This file documents those conventions, their sources, one encoding trap that silently
reverses a citation, and the measurement defect this skill exists to catch. It is written for a
reader who may not read Arabic, so every Arabic term is explained on first use. Everything here is
typographic and editorial. **Nothing here is a religious ruling** — see the gate at the end.

Labels follow `registers.md`: `[verified]` = checked or measured first-hand while writing this file,
`[reported]` = read through a summary or carried from this project's research phase, `[unverified]`
= unchecked.

## Citation marks

ʿAbd al-Salām Muḥammad Hārūn, *Qawāʿid al-imlāʾ wa-ʿalāmāt al-tarqīm* ("Rules of orthography and
punctuation marks"; Internet Archive item `a476n`), states it directly: `[reported]`

| what is quoted | mark | note |
|---|---|---|
| a Qurʾanic verse | ornate parentheses ﴿ ﴾ | the قوسان قرآنيان, "the two Qurʾanic parentheses", used *instead of* quotation marks so that Qurʾanic text is distinguishable from everything else |
| a hadith (a saying of the Prophet) | guillemets « » | |
| an addition not present in the original | square brackets [ ] | "غالبًا ما يستخدمهما محققو التراث، وهدفهما تفادي الخلط" — "editors of classical texts use them most often; their purpose is to avoid confusion" |

The point of the first row is functional: the ornate parentheses are a *class marker*, not a
decoration. A reader who sees them knows, before reading a word, that what follows is not the
author's own sentence.

## A Unicode trap, verified locally

The two ornate parentheses are named backwards relative to what they do.

- `﴿` is **U+FD3F**, named ORNATE RIGHT PARENTHESIS, and it **opens**.
- `﴾` is **U+FD3E**, named ORNATE LEFT PARENTHESIS, and it **closes**.

`[verified]` re-checked on 2026-09-17 against Unicode 15.0.0: `unicodedata.category(chr(0xFD3F))` is
`'Ps'` (open punctuation) and `category(chr(0xFD3E))` is `'Pe'` (close punctuation), while
`mirrored == 0` for both. Reproduce:

```
python -c "import unicodedata as u; print(u.category(chr(0xFD3F)), u.category(chr(0xFD3E)))"
```

`mirrored == 0` is the part that bites. Ordinary parentheses are mirrored characters: the bidi
engine swaps them for you when text runs right to left, so a writer cannot easily get them
backwards. These two are not mirrored, so **nothing corrects the writer**. Anyone who trusts the
Unicode names, or who reasons "Arabic runs right to left, so the left one must open", produces a
reversed citation that renders as an obvious error to an Arabic reader and as nothing at all to
everyone else. The rule table carries a hard check for exactly this reversal.

## Isolate citations before measuring anything

Aḥmad Zakī Bāšā, who founded modern Arabic punctuation with *al-Tarqīm wa-ʿalāmātuh fī al-lugha
al-ʿarabiyya* (1912), excluded the Qurʾan from his own system:
"لا موجب لاستعمال هذه العلامات في كتابة القرآن الكريم" — "there is no call for using these marks in
writing the Noble Qurʾan" — because the reciters' pause marks (عَلامات الوقف, the signs that tell a
reciter where he may stop and where he may not) already do that work. He said the same was
"probably" right for hadith. `[reported]` — full text at `safahat.org/books/82047270/1/`.

Two consequences, both operational:

1. A quoted verse is **not governed by the punctuation rules that govern the prose around it**.
   Reporting a missing comma inside a verse is reporting an error that does not exist.
2. Any measurement of punctuation density, sentence length or diacritic density must **exclude cited
   scripture before measuring**, or it reports noise. A single fully vocalised verse inside an
   otherwise bare paragraph will drag a whole-text diacritic ratio into the wrong band.

## Vocalisation

Vocalisation means writing the تشكيل (*tashkīl*) — the marks above and below the letters that
supply short vowels, gemination and the glottal stop. Modern Arabic prose normally omits most of
them; the reader supplies them from context.

The Cairo Academy's rules for vocalising schoolbooks (قواعد الشكل في الكتب المدرسية), approved by
its council in 1959 and its conference in 1960: `[reported]`

- **full vocalisation of Qurʾanic verses and hadith, at every level of education**;
- elsewhere "يُهمل الشكل بالفتحة" — the fatha (the a-vowel mark) is dropped — **except** when it
  falls on a wāw (و) or a yāʾ (ي);
- **shadda** (gemination), **madda** (the long-alif mark) and **hamzat qaṭʿ** (the written glottal
  stop) remain **obligatory**;
- **uncommon proper names are vocalised**.

This text appears both in the Academy's own collected decisions and, independently, in Hārūn — two
sources carrying the same text.

Corroborated from a different direction by two professional style guides: `[reported]`

- Netflix, *Arabic Timed Text Style Guide*: "The use of Arabic diacritics is required if their
  absence changes the meaning of the word."
- The World Bank, *Arabic Style Guide* (2004): shadda advisable where its absence causes ambiguity;
  damma on passive verbs.

Three independent bodies, one principle: **diacritics are functional, not ornamental.** They are
written where they do work, and omitted where they do not.

## The defect this skill exists to catch

`[verified]` In a baseline run on 2026-09-17, an agent writing Arabic *without* this skill produced
**running prose** — not citations — at **784 and 770 diacritics per 1000 Arabic letters**, i.e.
fully vocalised, against **9 per 1000** for a news dispatch. The measurement and its two extremes
are recorded in the rule table's diacritic rule (`assets/rules.json`).

Models over-apply tashkīl the moment they sense an elevated register. They reach for it as a marker
of solemnity, which is precisely the ornamental use all three sources above rule out. It is the most
reliable tell that Arabic was machine-written, and it is invisible to a reviewer who does not read
Arabic — which is the gap this skill was built for.

No threshold is published here. The two ends of the range are measured; no consulted source states a
cut-off, and inventing one would put an unsourced number next to a sourced rule.

## Quoting scripture outside a muṣḥaf

A muṣḥaf — a printed copy of the Qurʾan itself — must follow the رسم عثماني (*rasm ʿuthmānī*), the
codified consonantal spelling of the ʿUthmānic codex, which differs in places from ordinary modern
orthography. The separate question is what to do with isolated verses quoted in a book, an article
or a web page.

Two fatwas address that case: `[reported]`

- Dār al-Iftāʾ al-Miṣriyya, fatwa 12390, titled precisely
  "حكم كتابة الآيات المفردة خارج المصحف بالرسم الإملائي" ("the ruling on writing isolated verses
  outside the muṣḥaf in standard orthography"), permits standard orthography — "فلا حرج فيه"
  ("there is no harm in it") — citing al-Bāqillānī.
- IslamWeb, fatwa 30196, concurs more narrowly, citing al-Zarkashī and al-Suyūṭī.

**Both are marked `[reported]` deliberately:** they were read through a tool summary, not at source.
This project does not treat a second-hand religious source as established, and neither should a
reader of this file.

## The human-review gate

> This skill does not rule on fiqh. Every finding in this file is a typographic and editorial
> observation, never a religious ruling. Text quoting scripture must be reviewed by a qualified
> human before publication.
>
> The rule flagging the abbreviated prayer on the Prophet — `(ص)` and `(صلعم)` in place of the full
> formula — is deliberately a **recommendation, not a hard rule**, because its sources have not yet
> been read at first hand. This project does not fail a text on a second-hand religious source.

That gate is not a disclaimer bolted on at the end. It is why the ornate-parenthesis reversal is a
hard rule (an encoding fact, verified in one command) while the abbreviation is a recommendation
(a religious judgement, read through a summary). The severity of a rule in this skill tracks the
strength of its chain, not the strength of anyone's opinion.
