"""Tanwin al-fath on alif in BAREC v1.0: written or not, and where.

Reproduces the figures behind AR-TANWIN-01 (references/divergences.md).

Probe words are adverbials that are ALWAYS indefinite accusatives ending in
alif, so "should it carry fathatan?" is decidable without a POS tagger.

Usage:  python tools/barec_tanwin.py DIR
DIR holds train.parquet, dev.parquet and test.parquet, downloaded from
CAMeL-Lab/BAREC-Corpus-v1.0 on HuggingFace (data/*-00000-of-00001.parquet,
renamed). Needs pyarrow, which the skill itself does not.
"""
import collections, re, sys
from pathlib import Path

import pyarrow.parquet as pq

DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

PROBES = set("""أيضا جدا دائما غالبا أحيانا سابقا حاليا تقريبا أبدا مثلا فضلا شكرا
كثيرا قليلا جميعا معا أولا ثانيا ثالثا أخيرا مجددا فورا حقا طبعا خصوصا عموما
سريعا ليلا نهارا صباحا أصلا إطلاقا""".split())

FATHATAN = "ً"
HARAKAT = {chr(c) for c in range(0x064B, 0x0653)} | {"ٰ"}
ALIF = "ا"


def skeleton(tok):
    return "".join(c for c in tok if c not in HARAKAT)


def arabic_letters(s):
    return sum(1 for c in s if 0x0621 <= ord(c) <= 0x064A)


def classify(tok):
    """'none' | 'before' (letter+ً+ا) | 'on' (ا+ً)."""
    core = tok.rstrip()
    if core.endswith(ALIF + FATHATAN):
        return "on"
    # strip trailing alif, then look at the marks sitting on the letter before it
    if core.endswith(ALIF):
        i = len(core) - 2
        while i >= 0 and core[i] in HARAKAT:
            if core[i] == FATHATAN:
                return "before"
            i -= 1
    return "none"


rows = []
for split in ("train", "dev", "test"):
    rows += pq.read_table(str(DIR / f"{split}.parquet"),
                          columns=["Sentence", "Source", "Readability_Level_3"]).to_pylist()
rows = [r for r in rows if r["Source"] != "Hanging Odes"]
print("sentences (poetry excluded):", len(rows))

by_band = collections.defaultdict(collections.Counter)   # functional/vocalised -> class
by_source = collections.defaultdict(collections.Counter)
by_level = collections.defaultdict(collections.Counter)
examples = {}

for r in rows:
    s = r["Sentence"] or ""
    letters = arabic_letters(s)
    if not letters:
        continue
    marks = sum(1 for c in s if c in HARAKAT)
    band = "vocalised" if 1000 * marks / letters >= 200 else "functional"
    for tok in re.findall(r"[؀-ۿ]+", s):
        sk = skeleton(tok)
        if sk[:1] in ("و", "ف") and sk[1:] in PROBES:
            sk = sk[1:]
        if sk not in PROBES:
            continue
        k = classify(tok)
        by_band[band][k] += 1
        by_source[r["Source"]][(band, k)] += 1
        by_level[r["Readability_Level_3"]][(band, k)] += 1
        examples.setdefault(k, tok)


def line(c, keys=("none", "before", "on")):
    n = sum(c[k] for k in keys)
    return n, "  ".join(f"{k}={c[k]} ({100*c[k]/n:.1f}%)" if n else f"{k}=0" for k in keys)


for band in ("functional", "vocalised"):
    n, txt = line(by_band[band])
    print(f"\n[{band}] n={n}\n  {txt}")

print("\nexamples:", {k: v for k, v in examples.items()})

print("\nper Readability_Level_3, functional prose only:")
for lvl in sorted(by_level):
    c = collections.Counter({k: v for (b, k), v in by_level[lvl].items() if b == "functional"})
    n, txt = line(c)
    print(f"  level {lvl}: n={n}  {txt}")

print("\nper source, functional prose only (n>=10):")
for src, c0 in sorted(by_source.items()):
    c = collections.Counter({k: v for (b, k), v in c0.items() if b == "functional"})
    n = sum(c.values())
    if n < 10:
        continue
    w = c["before"] + c["on"]
    print(f"  {src[:38]:38} n={n:5}  none={100*c['none']/n:5.1f}%  written={100*w/n:5.1f}%"
          f"  before={c['before']:4} on={c['on']:4}")
