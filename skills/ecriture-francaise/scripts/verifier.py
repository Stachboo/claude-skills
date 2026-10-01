#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérificateur d'écriture française.

Deux familles de contrôles :
  - règles DURES  : mécaniquement vérifiables, une occurrence est une faute -> exit 1
  - MESURES       : indicateurs de rythme, signalés sans bloquer

Usage :
    python verifier.py fichier.html [fichier.md ...]
    python verifier.py --json fichier.md
    cat fichier.txt | python verifier.py -

Formats acceptés : .html, .htm, .md, .markdown, .txt, texte brut sur l'entrée standard.
Le code, les feuilles de style et les blocs préformatés sont exclus de l'analyse.
"""

import argparse
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

# Une console Windows en cp1252 fait planter le moindre « → » du rapport.
# On force UTF-8 sur les flux de sortie ; si la console ne suit pas, on remplace
# le caractère au lieu d'interrompre l'analyse.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # flux redirigé ou non reconfigurable
        pass

NARROW_NBSP = " "   # espace fine insécable
NBSP = " "          # espace insécable

# ---------------------------------------------------------------------------
# Extraction du texte analysable
# ---------------------------------------------------------------------------

HTML_SKIP_TAGS = ("script", "style", "pre", "code", "samp", "kbd", "tt", "math")

# Pour la mesure de rythme uniquement : on exclut en plus tout ce qui n'est pas de la
# prose suivie. Un titre ou une cellule de tableau compte sinon comme une phrase de
# deux mots et fait exploser artificiellement la variance.
PROSE_SKIP_TAGS = HTML_SKIP_TAGS + (
    "th", "td", "caption", "h1", "h2", "h3", "h4", "h5", "h6", "dt", "figcaption",
)


def _blank(match):
    return re.sub(r"[^\n]", " ", match.group(0))


def _jeton(match):
    """Remplace un fragment par un mot factice de même longueur.

    Pour le code en ligne, blanchir produit de faux positifs : `x`. devient un
    espace avant le point, et (`x`) une parenthèse à l'espace collée. Un mot
    plein conserve les offsets sans déclencher les règles de ponctuation.
    """
    return re.sub(r"[^\n]", "x", match.group(0))


def strip_html(source: str, skip_tags=HTML_SKIP_TAGS) -> str:
    """Retire les blocs non rédactionnels puis les balises, en préservant les offsets
    de ligne (on remplace par des espaces et des retours à la ligne)."""
    blank = _blank

    for tag in skip_tags:
        source = re.sub(
            rf"<{tag}\b.*?</{tag}\s*>", blank, source, flags=re.S | re.I
        )
    source = re.sub(r"<!--.*?-->", blank, source, flags=re.S)
    source = re.sub(r"<[^>]+>", blank, source)
    # entités les plus courantes, pour ne pas les compter comme du texte
    source = source.replace("&nbsp;", NBSP).replace("&#8239;", NARROW_NBSP)
    source = re.sub(r"&[a-zA-Z#0-9]+;", lambda m: " " * len(m.group(0)), source)
    return source


def strip_markdown(source: str, prose_only: bool = False) -> str:
    blank = _blank

    if prose_only:
        source = re.sub(r"^#{1,6} .*$", blank, source, flags=re.M)   # titres
        source = re.sub(r"^\s*\|.*$", blank, source, flags=re.M)      # tableaux
    source = re.sub(r"```.*?```", blank, source, flags=re.S)
    source = re.sub(r"~~~.*?~~~", blank, source, flags=re.S)
    source = re.sub(r"`[^`\n]+`", _jeton, source)   # code en ligne : mot factice, pas du vide
    # [ \t] et non \s : \s inclut le saut de ligne, et après un bloc de code
    # (déjà blanchi en espaces) suivi d'une ligne vide, le motif traversait les
    # lignes et effaçait la première ligne de prose qui suit chaque bloc. Toutes
    # les règles étaient aveugles sur ces lignes (constaté le 2026-10-01).
    source = re.sub(r"^(?:[ ]{4,}|\t)[ \t]*\S.*$", blank, source, flags=re.M)
    source = re.sub(r"^---\n.*?\n---\n", blank, source, flags=re.S)  # front matter
    return source


def extract(source: str, suffix: str, prose_only: bool = False) -> str:
    """prose_only=True : réservé à la mesure de rythme. Exclut titres et tableaux."""
    suffix = suffix.lower()
    if suffix in (".html", ".htm", ".xhtml"):
        return strip_html(source, PROSE_SKIP_TAGS if prose_only else HTML_SKIP_TAGS)
    if suffix in (".md", ".markdown"):
        return strip_markdown(source, prose_only=prose_only)
    return source


# ---------------------------------------------------------------------------
# Règles dures
# ---------------------------------------------------------------------------
# Chaque règle : (identifiant, expression, message, fonction de filtrage optionnelle)

def _not_in_url(line: str, start: int) -> bool:
    """Écarte les faux positifs situés dans une URL ou une heure (14:30)."""
    left = line[max(0, start - 12):start + 1]
    if re.search(r"(https?|ftp|mailto|tel)$", left, re.I):
        return False
    if re.search(r"\d$", left) and re.match(r":\d", line[start:start + 2]):
        return False
    return True


HARD_RULES = [
    # --- typographie ---
    (
        "TYPO-01",
        re.compile(rf"[^\s{NARROW_NBSP}{NBSP}][;!?]"),
        "espace fine insécable (U+202F) manquante avant ; ! ou ?",
        None,
    ),
    (
        "TYPO-02",
        re.compile(rf"[ ][;!?]"),
        "espace ordinaire avant ; ! ou ? — utiliser U+202F",
        None,
    ),
    (
        "TYPO-03",
        re.compile(rf"[^\s{NBSP}{NARROW_NBSP}]:"),
        "espace insécable (U+00A0) manquante avant les deux-points",
        _not_in_url,
    ),
    (
        "TYPO-03b",
        re.compile(r"[ ]:"),
        "espace ordinaire avant les deux-points — utiliser U+00A0",
        _not_in_url,
    ),
    (
        "TYPO-04",
        re.compile(rf"«[^{NBSP}{NARROW_NBSP}]"),
        "espace insécable manquante après le guillemet ouvrant",
        None,
    ),
    (
        "TYPO-05",
        re.compile(rf"[^{NBSP}{NARROW_NBSP}]»"),
        "espace insécable manquante avant le guillemet fermant",
        None,
    ),
    (
        "TYPO-06",
        re.compile(r"[\"]"),
        "guillemets droits — utiliser les chevrons « »",
        None,
    ),
    (
        "TYPO-07",
        re.compile(r"[a-zA-ZÀ-ÿ]'"),
        "apostrophe droite — utiliser l’apostrophe typographique U+2019",
        None,
    ),
    (
        "TYPO-08",
        re.compile(r"\.\.\."),
        "trois points — utiliser le caractère … (U+2026)",
        None,
    ),
    (
        "TYPO-09",
        re.compile(r"\s+[.,](?:\s|$)"),
        "espace avant un point ou une virgule",
        None,
    ),
    (
        "TYPO-10",
        re.compile(r"\(\s|\s\)"),
        "espace collée à l’intérieur d’une parenthèse",
        None,
    ),
    (
        # Le défaut que corriger.py produisait avant le 2026-10-01 (« 1 + espace
        # + insécable + : »), invisible pour toutes les autres règles. Limité aux
        # endroits où la typographie française place une insécable : devant
        # : ; ! ? » et après «. Validé sur 93 pages HTML : hors de ces signes,
        # « &nbsp;·&nbsp; » ou « &nbsp; Livré » sont des espacements de mise en
        # page voulus, pas des fautes. « (?<=\S) » écarte aussi une balise effacée,
        # qui laisse plusieurs espaces.
        "TYPO-11",
        re.compile(rf"(?<=\S)(?:[ ][{NBSP}{NARROW_NBSP}]|[{NBSP}{NARROW_NBSP}][ ])(?=[:;!?»])"
                   rf"|(?<=«)(?:[ ][{NBSP}{NARROW_NBSP}]|[{NBSP}{NARROW_NBSP}][ ])"),
        "espace ordinaire collée à une espace insécable — n’en garder qu’une, l’insécable",
        None,
    ),
    # --- anglicismes ---
    (
        "ANGL-01",
        re.compile(r",\s+(et|ou)\s"),
        "virgule sérielle avant « et » ou « ou » — construction anglaise",
        None,
    ),
    # --- constructions ---
    (
        "CONS-01",
        re.compile(
            r"\b(ce n[’']est pas .{1,80}?, c[’']est"
            r"|il ne s[’']agit pas .{1,80}?, (mais|c[’']est)"
            r"|non pas .{1,60}? mais"
            r"|\bet non\b)",
            re.I,
        ),
        "construction par antithèse (« ce n’est pas X, c’est Y »)",
        None,
    ),
    (
        "CONS-02",
        re.compile(
            r"\b(il (convient|importe) de (noter|souligner|préciser)"
            r"|il est important de (noter|souligner)"
            r"|il (est|serait) utile de (noter|préciser)"
            r"|ce point mérite"
            r"|force est de constater"
            r"|il (est|va) sans dire)",
            re.I,
        ),
        "méta-commentaire — écrire l’idée, pas son étiquette",
        None,
    ),
    (
        "CONS-03",
        re.compile(
            r"(^|\n)\s*(en effet|par ailleurs|de plus|en outre|qui plus est|"
            r"cela (dit|étant)|ceci (dit|étant)|force est|dans un monde où|"
            r"à l[’']heure où|de nos jours)\b",
            re.I,
        ),
        "ouverture de phrase stéréotypée",
        None,
    ),
    (
        "CONS-04",
        re.compile(
            r"\b(plonge(r|ons|z)? dans"
            r"|riche (tapisserie|palette)"
            r"|véritable (mine|trésor|game.?changer)"
            r"|change(r)? la donne"
            r"|au c(œ|oe)ur de l[’'](ère|écosystème)"
            r"|paysage (numérique|technologique|concurrentiel)"
            r"|témoignage de (l[’']|la |le |son |leur ))",
            re.I,
        ),
        "calque de l’anglais (delve, tapestry, landscape, testament, game-changer)",
        None,
    ),
]

# Règles à seuil : (identifiant, expression, seuil pour mille mots, message)
DENSITY_RULES = [
    ("PONC-01", re.compile(r"—"), 1.0,
     "tirets cadratins trop fréquents — remplacer par virgule, point-virgule ou point"),
]


# ---------------------------------------------------------------------------
# Mesures de rythme
# ---------------------------------------------------------------------------

SENTENCE_END = re.compile(r"[.!?…]+[\s\"»)]*")


def sentences(text: str):
    """Découpage approximatif en phrases. Les abréviations courantes sont protégées."""
    protected = text
    for abbr in ("M.", "Mme", "Mlle", "art.", "al.", "cf.", "p.", "n°", "etc.",
                 "ex.", "éd.", "vol.", "chap.", "op. cit.", "Dr.", "St."):
        protected = protected.replace(abbr, abbr.replace(".", ""))
    parts = SENTENCE_END.split(protected)
    out = []
    for part in parts:
        cleaned = part.replace("", ".").strip()
        words = [w for w in re.split(r"\s+", cleaned) if w]
        if len(words) >= 2:
            out.append(len(words))
    return out


def rhythm(text: str):
    lengths = sentences(text)
    if len(lengths) < 8:
        return None
    mean = statistics.mean(lengths)
    stdev = statistics.pstdev(lengths)
    cv = stdev / mean if mean else 0.0
    return {
        "phrases": len(lengths),
        "longueur_moyenne": round(mean, 1),
        "ecart_type": round(stdev, 1),
        "coefficient_variation": round(cv, 3),
        "plus_courte": min(lengths),
        "plus_longue": max(lengths),
    }


CV_PLAT = 0.40
CV_VIVANT = 0.55


# ---------------------------------------------------------------------------
# Analyse
# ---------------------------------------------------------------------------

def analyse(raw: str, suffix: str):
    text = extract(raw, suffix)
    lines = text.split("\n")
    findings = []

    for rule_id, pattern, message, keep in HARD_RULES:
        for line_no, line in enumerate(lines, start=1):
            for match in pattern.finditer(line):
                if keep and not keep(line, match.start()):
                    continue
                findings.append({
                    "regle": rule_id,
                    "ligne": line_no,
                    "extrait": line[max(0, match.start() - 30):match.end() + 30].strip(),
                    "message": message,
                    "niveau": "dur",
                })

    words = len([w for w in re.split(r"\s+", text) if w])
    per_thousand = (words / 1000) or 1
    for rule_id, pattern, threshold, message in DENSITY_RULES:
        count = len(pattern.findall(text))
        rate = count / per_thousand
        if rate > threshold:
            findings.append({
                "regle": rule_id,
                "ligne": 0,
                "extrait": f"{count} occurrences pour {words} mots ({rate:.2f} ‰)",
                "message": message,
                "niveau": "dur",
            })

    mesures = rhythm(extract(raw, suffix, prose_only=True))
    if mesures:
        cv = mesures["coefficient_variation"]
        if cv < CV_PLAT:
            mesures["verdict"] = "rythme plat — signal fort"
        elif cv < CV_VIVANT:
            mesures["verdict"] = "acceptable, sans être vivant"
        else:
            mesures["verdict"] = "rythme humain"

    return findings, mesures, words


def report(path_label, findings, mesures, words):
    dur = [f for f in findings if f["niveau"] == "dur"]
    print(f"\n=== {path_label} — {words} mots ===")

    if not dur:
        print("Règles dures : aucune violation.")
    else:
        print(f"Règles dures : {len(dur)} violation(s).\n")
        groups = {}
        for f in dur:
            groups.setdefault(f["regle"], []).append(f)
        for rule_id in sorted(groups):
            items = groups[rule_id]
            print(f"  [{rule_id}] {items[0]['message']} — {len(items)} occurrence(s)")
            for item in items[:4]:
                where = f"l.{item['ligne']}" if item["ligne"] else "global"
                print(f"      {where} : {item['extrait'][:110]}")
            if len(items) > 4:
                print(f"      … et {len(items) - 4} autre(s)")
            print()

    if mesures:
        print("Rythme :")
        print(f"  phrases                 : {mesures['phrases']}")
        print(f"  longueur moyenne        : {mesures['longueur_moyenne']} mots")
        print(f"  ecart-type              : {mesures['ecart_type']}")
        print(f"  coefficient de variation: {mesures['coefficient_variation']}"
              f"  -> {mesures['verdict']}")
        print(f"  plus courte / plus longue : {mesures['plus_courte']} / {mesures['plus_longue']} mots")
    else:
        print("Rythme : texte trop court pour être mesuré (moins de 8 phrases).")

    return len(dur)


def main():
    parser = argparse.ArgumentParser(description="Vérificateur d'écriture française.")
    parser.add_argument("fichiers", nargs="+", help="fichiers à analyser, ou - pour stdin")
    parser.add_argument("--json", action="store_true", help="sortie machine")
    parser.add_argument("--type", default=".txt",
                        help="format supposé pour stdin (.html, .md, .txt)")
    args = parser.parse_args()

    total = 0
    payload = []

    for target in args.fichiers:
        if target == "-":
            raw = sys.stdin.read()
            label, suffix = "<stdin>", args.type
        else:
            path = Path(target)
            if not path.is_file():
                print(f"Fichier introuvable : {target}", file=sys.stderr)
                total += 1
                continue
            raw = path.read_text(encoding="utf-8")
            label, suffix = str(path), path.suffix

        findings, mesures, words = analyse(raw, suffix)
        if args.json:
            payload.append({
                "fichier": label,
                "mots": words,
                "violations": findings,
                "mesures": mesures,
            })
        else:
            total += report(label, findings, mesures, words)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        total = sum(len([v for v in p["violations"] if v["niveau"] == "dur"])
                    for p in payload)

    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
