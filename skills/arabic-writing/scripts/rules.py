# -*- coding: utf-8 -*-
"""Rule loading and matching. Pure functions: no I/O beyond reading the table.

Pure module by design: no CLI, no printing, no global state. `check.py` imports
`load_rules` and `run_rules`; nothing here decides what to do with a finding.

Every rule carries its own isnad -- the chain back to a source a third party can
check -- and `load_rules` refuses a rule that does not. That is not decoration:
the whole point of this table is that a reader can re-verify any rule it fires,
so a rule with no chain would be an unsourced assertion wearing the authority of
a checker. The RED baseline caught a model doing exactly that (it condemned the
parenthetical em dash, which Zaki 1912 and Harun both attest), and that failure
is what this table exists to prevent.

Two kinds of rule
-----------------
`kind: "pattern"`     -- a regex, evaluated here.
`kind: "ratio"`       -- a measurement over the whole text, NOT evaluated here.
`kind: "consistency"` -- the text checked against itself, NOT evaluated here.

`run_rules` skips every non-pattern rule and leaves it to the passes in
`check.py`, which select them by kind.
A non-pattern rule stores `pattern: null`, never `""`: an empty regex matches at
every position in the text, so an empty pattern would make a rule fire once per
character. `load_rules` rejects both that and a pattern on a non-pattern rule.

Three severities
----------------
`hard`           -- unanimous across sources AND decidable without context.
`recommendation` -- needs judgement; reported, never blocking.
`divergence`     -- the authorities genuinely disagree. The Cairo Academy
                    contradicted itself on hamza between its 26th and 46th
                    sessions, Damascus gives a third answer, and the Damascus
                    preface states outright that no pan-Arab consensus exists.
                    On these the checker must never judge the spelling; it
                    checks the text against itself for consistency instead.
                    AR-TANWIN-01 is the first `divergence` rule: two placements
                    of tanwin al-fath, both in print, never judged -- only
                    reported when one text uses both.
"""
import json
import re

SEVERITIES = ("hard", "recommendation", "divergence")

PATTERN_KIND = "pattern"
NON_PATTERN_KINDS = ("ratio", "consistency")
KINDS = (PATTERN_KIND,) + NON_PATTERN_KINDS


def load_rules(path):
    """Load the rule table, validate it, and compile each pattern once.

    Raises ValueError on a malformed table rather than loading it degraded. The
    failure modes guarded here are all silent ones: an empty pattern that
    matches everywhere, a mistyped severity that `run_rules` would filter out so
    the rule never fires, a duplicate id that makes findings unattributable, a
    missing isnad that turns the rule into an unsourced claim.
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    rules = data["rules"]
    seen = set()
    for r in rules:
        rid = r.get("id")
        if not rid:
            raise ValueError("a rule in %s has no id" % (path,))
        if rid in seen:
            raise ValueError("duplicate rule id: %s" % (rid,))
        seen.add(rid)
        if r.get("severity") not in SEVERITIES:
            raise ValueError("rule %s has severity %r, expected one of %s"
                             % (rid, r.get("severity"), SEVERITIES))
        if not str(r.get("isnad") or "").strip():
            raise ValueError("rule %s carries no isnad; a rule without a "
                             "verifiable source does not belong in the table"
                             % (rid,))
        kind = r.setdefault("kind", PATTERN_KIND)
        if kind == PATTERN_KIND:
            pattern = r.get("pattern")
            if not isinstance(pattern, str) or not pattern:
                raise ValueError(
                    "rule %s is kind 'pattern' but its pattern is %r; an empty "
                    "pattern matches at every position" % (rid, pattern))
            r["_re"] = re.compile(pattern)
        elif kind in NON_PATTERN_KINDS:
            if r.get("pattern") is not None:
                raise ValueError("rule %s is kind %r and must carry a null "
                                 "pattern, not %r" % (rid, kind, r.get("pattern")))
            r["_re"] = None
        else:
            raise ValueError("rule %s has unknown kind %r, expected one of %s"
                             % (rid, kind, KINDS))
    return rules


def run_rules(text, rules, severities=None):
    """Return a list of findings: {id, severity, message, fix, isnad, line, col, excerpt}.

    Findings are sorted by position. Non-pattern rules are skipped; see the
    module docstring. `severities` restricts which rules are evaluated, so a
    caller that only wants blocking defects passes `["hard"]`.
    """
    # `None` means every severity; an explicit list means exactly that list.
    # Testing truthiness instead would make `severities=[]` -- "report nothing"
    # -- silently report everything, which is the worst direction for a filter
    # whose whole job is deciding what blocks a build.
    wanted = set(SEVERITIES) if severities is None else set(severities)
    findings = []
    for r in rules:
        if "_re" not in r:
            raise ValueError("rule %s was not loaded through load_rules()"
                             % (r.get("id"),))
        if r["severity"] not in wanted:
            continue
        if r["_re"] is None:
            continue
        for m in r["_re"].finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            col = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
            findings.append({
                "id": r["id"],
                "severity": r["severity"],
                "message": r["message"],
                "fix": r.get("fix", ""),
                "isnad": r["isnad"],
                "line": line,
                "col": col,
                "excerpt": text[max(0, m.start() - 20):m.end() + 20].replace("\n", " "),
            })
    findings.sort(key=lambda f: (f["line"], f["col"]))
    return findings
