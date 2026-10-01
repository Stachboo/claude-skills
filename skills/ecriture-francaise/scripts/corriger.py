#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correcteur typographique français.

Ne corrige que ce qui est mécanique et sans risque de sens : espaces insécables,
guillemets, apostrophes, points de suspension, espaces parasites.

Ne touche PAS aux virgules sérielles ni aux constructions par antithèse : leur
correction dépend du sens et reste à la charge du rédacteur. Le vérificateur les
signale.

Sur du HTML, le contenu des balises (attributs), les feuilles de style, les scripts et
les blocs préformatés sont protégés.

Usage :
    python corriger.py fichier.html              # écrit sur la sortie standard
    python corriger.py fichier.html --ecrire     # remplace le fichier
    python corriger.py fichier.md --diff         # nombre de modifications par règle
"""

import argparse
import re
import sys
from pathlib import Path

# Console Windows en cp1252 : on force UTF-8 sur les flux de sortie plutôt que
# de laisser un caractère non représentable interrompre la correction.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # flux redirigé ou non reconfigurable
        pass

NARROW = " "   # espace fine insécable
NBSP = " "     # espace insécable

PROTECTED_BLOCKS = ("style", "script", "pre", "code", "samp", "kbd", "tt", "math")

ESPACES = f"[ {NBSP}{NARROW}]*"

REGLES = [
    ("apostrophe",
     re.compile(r"(?<=[A-Za-zÀ-ÿ])'"), "’"),

    ("ellipse",
     re.compile(r"\.\.\.+"), "…"),

    ("espace-avant-ponctuation-double",
     re.compile(rf"{ESPACES}([;!?])"), NARROW + r"\1"),

    # La garde des chiffres ne protège que l'heure ou le ratio collés (12:30,
    # 3:1). Placée devant les espaces, elle laissait le motif démarrer après
    # l'espace de « Étape 1 : » et rendait « 1 + espace + insécable + : ».
    # Le motif part donc après la dernière lettre : soit il prend toutes les
    # espaces, soit il n'y en a aucune et le caractère précédent n'est pas
    # un chiffre.
    ("espace-avant-deux-points",
     re.compile(rf"(?<![ {NBSP}{NARROW}])(?:[ {NBSP}{NARROW}]+|(?<![0-9])):(?![0-9/])"),
     NBSP + ":"),

    ("guillemet-ouvrant",
     re.compile(rf"«{ESPACES}"), "«" + NBSP),

    ("guillemet-fermant",
     re.compile(rf"{ESPACES}»"), NBSP + "»"),

    ("espace-avant-point-virgule",
     re.compile(r"[ ]+([.,])(?=\s|$)"), r"\1"),

    ("parenthese-ouvrante",
     re.compile(r"\([ ]+"), "("),

    ("parenthese-fermante",
     re.compile(r"[ ]+\)"), ")"),
]


def corriger_texte(fragment: str, compteur: dict) -> str:
    # Les motifs acceptent « zéro espace ou plus », donc un passage déjà conforme
    # se re-remplace par lui-même. Ne compter que les substitutions qui changent
    # réellement le texte, sans quoi le décompte gonfle et ne mesure plus rien.
    for nom, motif, remplacement in REGLES:
        def remplacer(match, nom=nom, remplacement=remplacement):
            nouveau = match.expand(remplacement)
            if nouveau != match.group(0):
                compteur[nom] = compteur.get(nom, 0) + 1
            return nouveau

        fragment = motif.sub(remplacer, fragment)
    return fragment


def corriger_html(source: str, compteur: dict) -> str:
    # 1. mettre à l'abri les blocs non rédactionnels
    coffre = []

    def ranger(match):
        coffre.append(match.group(0))
        return f"\x00{len(coffre) - 1}\x00"

    for tag in PROTECTED_BLOCKS:
        source = re.sub(rf"<{tag}\b.*?</{tag}\s*>", ranger, source,
                        flags=re.S | re.I)
    source = re.sub(r"<!--.*?-->", ranger, source, flags=re.S)

    # Les entités se terminent par un point-virgule. Sans cette protection, la
    # règle « espace fine avant ; » s'applique à &nbsp; et rend « &nbsp ; »,
    # qui n'est plus une entité : le balisage est corrompu et s'affiche en clair.
    source = re.sub(r"&(?:[a-zA-Z][a-zA-Z0-9]{1,31}|#\d{1,7}|#[xX][0-9a-fA-F]{1,6});",
                    ranger, source)

    # 2. ne traiter que les nœuds de texte, jamais l'intérieur des balises
    morceaux = re.split(r"(<[^>]+>)", source)
    for i in range(0, len(morceaux), 2):
        morceaux[i] = corriger_texte(morceaux[i], compteur)
    resultat = "".join(morceaux)

    # 3. remettre les blocs protégés
    def sortir(match):
        return coffre[int(match.group(1))]

    return re.sub(r"\x00(\d+)\x00", sortir, resultat)


def corriger_markdown(source: str, compteur: dict) -> str:
    coffre = []

    def ranger(match):
        coffre.append(match.group(0))
        return f"\x00{len(coffre) - 1}\x00"

    source = re.sub(r"```.*?```", ranger, source, flags=re.S)
    source = re.sub(r"~~~.*?~~~", ranger, source, flags=re.S)
    source = re.sub(r"`[^`\n]+`", ranger, source)
    source = re.sub(r"\]\([^)]+\)", ranger, source)   # cibles de liens

    source = corriger_texte(source, compteur)

    def sortir(match):
        return coffre[int(match.group(1))]

    return re.sub(r"\x00(\d+)\x00", sortir, source)


def corriger(source: str, suffix: str, compteur: dict) -> str:
    suffix = suffix.lower()
    if suffix in (".html", ".htm", ".xhtml"):
        return corriger_html(source, compteur)
    if suffix in (".md", ".markdown"):
        return corriger_markdown(source, compteur)
    return corriger_texte(source, compteur)


def main():
    parser = argparse.ArgumentParser(description="Correcteur typographique français.")
    parser.add_argument("fichier")
    parser.add_argument("--ecrire", action="store_true",
                        help="remplace le fichier au lieu d'écrire sur la sortie")
    parser.add_argument("--diff", action="store_true",
                        help="n'affiche que le décompte des corrections")
    args = parser.parse_args()

    chemin = Path(args.fichier)
    if not chemin.is_file():
        print(f"Fichier introuvable : {chemin}", file=sys.stderr)
        sys.exit(2)

    source = chemin.read_text(encoding="utf-8")
    compteur = {}
    resultat = corriger(source, chemin.suffix, compteur)

    total = sum(compteur.values())

    if args.ecrire:
        chemin.write_text(resultat, encoding="utf-8")
        print(f"{chemin} : {total} correction(s) appliquée(s).", file=sys.stderr)
    elif not args.diff:
        sys.stdout.write(resultat)

    if args.diff:
        if not total:
            print("Aucune correction nécessaire.", file=sys.stderr)
        else:
            print(f"{total} correction(s) :", file=sys.stderr)
            for nom in sorted(compteur, key=lambda k: -compteur[k]):
                print(f"  {compteur[nom]:>5}  {nom}", file=sys.stderr)


if __name__ == "__main__":
    main()
