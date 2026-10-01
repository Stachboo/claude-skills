"""Hamzat qat', madda and shadda in BAREC v1.0: written or left out.

Each probe below has exactly one correct spelling, and its bare form is not
another word, so "is the hamza / madda / shadda missing?" is decidable
without a morphological analyser.

Usage:  python tools/barec_hamza_madda_shadda.py DIR
DIR holds train.parquet, dev.parquet and test.parquet from
CAMeL-Lab/BAREC-Corpus-v1.0 (see tools/barec_tanwin.py). Needs pyarrow.
"""
import collections, re, sys
from pathlib import Path

import pyarrow.parquet as pq

DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

HARAKAT = {chr(c) for c in range(0x064B, 0x0653)} | {"ٰ", "ـ"}  # + tatweel
SHADDA = "ّ"

# bare spelling -> correct spelling (letters only). Whole tokens, optional
# prefix wa-/fa-. Every bare form here is a misspelling, never another word.
HAMZA = {
    "الى": "إلى", "اذا": "إذا", "او": "أو", "ايضا": "أيضا", "اكثر": "أكثر",
    "اول": "أول", "امام": "أمام", "اخرى": "أخرى", "انه": None, "ان": None,
    "احد": "أحد", "اصبح": "أصبح", "اطار": "إطار", "اسلام": "إسلام",
    "الاسلام": "الإسلام", "الانسان": "الإنسان", "اذ": "إذ", "اما": None,
}
# None: two correct spellings (an/in, annahu/innahu, amma/imma) -- the bare
# form is wrong either way, so it still counts as hamza missing.
MADDA = {"الان": "الآن", "القران": "القرآن", "الاف": "آلاف", "الاخرة": "الآخرة",
         "الاخرين": "الآخرين", "اخرين": "آخرين"}
# Words whose second-to-last or middle consonant is geminated in every
# reading: checked for a shadda anywhere in the token.
SHADDA_PROBES = {"ثم", "مرة", "قوة", "مدة", "خاصة", "عامة", "حق", "كل", "اي", "أي",
                 "إن", "لكن", "الله"}


def letters(tok):
    return "".join(c for c in tok if c not in HARAKAT)


def arabic_letters(s):
    return sum(1 for c in s if 0x0621 <= ord(c) <= 0x064A)


def strip_prefix(sk, table):
    if sk in table:
        return sk
    if sk[:1] in ("و", "ف") and sk[1:] in table:
        return sk[1:]
    return None


# Prefixes wa-/fa- are accepted only where prefix + bare form is not itself a
# word: wa+ahd = wahid "one", fa+an = fanin "perishing", wa+ila = wala (verb),
# wa+aw = waw, fa+aw = Fao. Measured first without this guard: "ahd" came out
# 30% missing, almost all of it wahid.
PREFIXABLE = {"انه", "اذا", "اما", "ايضا", "اكثر", "اول", "امام", "اخرى",
              "اصبح", "اذ"}


def hamza_key(sk):
    """Map a hamzated or bare probe token to its bare key, or None."""
    for bare, good in HAMZA.items():
        for p in (("", "و", "ف") if bare in PREFIXABLE else ("",)):
            if sk == p + bare:
                return bare, "missing"
            goods = [good] if good else {
                "انه": ["أنه", "إنه"], "ان": ["أن", "إن"], "اما": ["أما", "إما"]}[bare]
            if any(sk == p + g for g in goods):
                return bare, "written"
    return None


def madda_key(sk):
    for bare, good in MADDA.items():
        for p in ("",):
            if sk == p + bare:
                return bare, "missing"
            if sk == p + good:
                return bare, "written"
    return None


rows = []
for split in ("train", "dev", "test"):
    rows += pq.read_table(str(DIR / f"{split}.parquet"),
                          columns=["Sentence", "Source"]).to_pylist()
rows = [r for r in rows if r["Source"] != "Hanging Odes"]
print("sentences (poetry excluded):", len(rows))

tot = {k: collections.Counter() for k in ("hamza", "madda", "shadda")}
src = {k: collections.defaultdict(collections.Counter) for k in tot}
word = {k: collections.defaultdict(collections.Counter) for k in ("hamza", "madda")}

for r in rows:
    s = r["Sentence"] or ""
    n = arabic_letters(s)
    if not n:
        continue
    marks = sum(1 for c in s if c in HARAKAT and c != "ـ")
    if 1000 * marks / n >= 200:
        continue                      # functional prose only, as for AR-DIAC-01
    for tok in re.findall(r"[؀-ۿ]+", s):
        sk = letters(tok)
        h = hamza_key(sk)
        if h:
            tot["hamza"][h[1]] += 1
            src["hamza"][r["Source"]][h[1]] += 1
            word["hamza"][h[0]][h[1]] += 1
        m = madda_key(sk)
        if m:
            tot["madda"][m[1]] += 1
            src["madda"][r["Source"]][m[1]] += 1
            word["madda"][m[0]][m[1]] += 1
        base = strip_prefix(sk, SHADDA_PROBES)
        if base:
            k = "written" if SHADDA in tok else "missing"
            tot["shadda"][k] += 1
            src["shadda"][r["Source"]][k] += 1

for k in ("hamza", "madda", "shadda"):
    c = tot[k]
    n = c["missing"] + c["written"]
    print(f"\n[{k}] functional prose, n={n}: missing={c['missing']} "
          f"({100*c['missing']/n:.1f}%)  written={c['written']}")
    if k in word:
        for w, cc in sorted(word[k].items(), key=lambda x: -sum(x[1].values())):
            m = sum(cc.values())
            print(f"    {w:10} n={m:6}  missing={100*cc['missing']/m:5.1f}%")
    print("  per source (n>=20): missing%")
    for s_, cc in sorted(src[k].items()):
        m = cc["missing"] + cc["written"]
        if m >= 20:
            print(f"    {s_[:38]:38} n={m:6}  missing={100*cc['missing']/m:5.1f}%")
