# -*- coding: utf-8 -*-
"""Preset resolution. Standard library only.

The user makes ONE choice: a preset name. Every other setting follows from it.
Field-by-field override stays possible but is never required -- a beginner
chooses once, an expert can still tune.

Why a declared profile exists at all: the Arabic language academies contradict
each other (Cairo gave `shu'un` one way at its 26th session and another at its
46th; Damascus gives a third answer and says in its own preface that no
pan-Arab consensus exists). So nothing here imposes a spelling. The profile
records which school the author declared, and the checks test the text for
consistency with THAT declaration.

Pure module by design: no CLI, no printing, no side effect beyond reading its
own asset. `resolve()` is the only entry point; `PRESETS` and `PRESET_NAMES`
are exported for callers that need to show the list.

The asset is read at import time on purpose -- see the comment on that read.
"""
import copy
import json
from pathlib import Path

_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def _load(name):
    """Read one of the skill's own JSON assets."""
    return json.loads((_ASSETS / name).read_text(encoding="utf-8"))


# Both assets are read once, at import. They ship with the skill, so a missing
# or malformed one is a packaging error, not a runtime condition: failing here
# reports it once, at one place, instead of deep inside a later check, and a
# half-loaded asset set is a broken install rather than a degraded mode worth
# limping along in. (`PRESET_NAMES` also has to be a module-level constant by
# contract, which forces profiles.json to be read at import in any case;
# registers.json has no such constant, and is read here for coherence and
# fail-fast -- one extra small read at import, no caller that benefits from
# deferring it.)
_DATA = _load("profiles.json")
_REG = _load("registers.json")

PRESETS = _DATA["presets"]
PRESET_NAMES = sorted(PRESETS)
if not PRESET_NAMES:
    raise ValueError(
        "%s defines no presets; the skill ships at least seven." % (_ASSETS / "profiles.json")
    )

# The audiences registers.json measures. Closed set: it is what `targets`
# accepts, and every preset must declare one of these or the skill ships
# broken -- the loop below proves that at import rather than at first use.
AUDIENCES = frozenset(_REG["audience"])

# The settable fields, taken from the presets themselves rather than hardcoded,
# so the asset stays the single source of truth. Every preset carries the same
# six keys; the loop below fails loudly at import if one ever drifts.
FIELDS = frozenset(PRESETS[PRESET_NAMES[0]])
for _name in PRESET_NAMES:
    if frozenset(PRESETS[_name]) != FIELDS:
        raise ValueError(
            "Preset %r does not carry the same fields as the others: %s"
            % (_name, ", ".join(sorted(FIELDS)))
        )
    if PRESETS[_name]["audience"] not in AUDIENCES:
        raise ValueError(
            "Preset %r declares audience %r, which registers.json does not measure. "
            "Measured audiences: %s"
            % (_name, PRESETS[_name]["audience"], ", ".join(sorted(AUDIENCES)))
        )


def resolve(preset, overrides=None):
    """Return the full profile for `preset`, with optional per-field overrides.

    `overrides` is a mapping (or pair-iterable) whose keys must be real profile
    fields. An unknown key raises rather than passing silently: a typo such as
    `{"audiance": "advanced"}` would otherwise leave the real `audience` at its
    preset value while looking as if it had been set, and a wrong audience
    silently changes which sentence-length cap applies.

    Override VALUES are not checked here. The set of legitimate values is open
    -- more schools will be declared than the two the presets happen to use,
    and `italics: True` is legitimate although no preset sets it -- so deriving
    an allowed set from the presets would reject valid input. Value meaning is
    the business of whichever check consumes the field.
    """
    if preset not in PRESETS:
        raise ValueError(
            "Unknown preset %r. Choose one of: %s" % (preset, ", ".join(PRESET_NAMES))
        )
    profile = dict(PRESETS[preset])
    if overrides:
        overrides = dict(overrides)
        unknown = sorted(set(overrides) - FIELDS)
        if unknown:
            raise ValueError(
                "Unknown override field(s): %s. Valid fields are: %s"
                % (", ".join(repr(k) for k in unknown), ", ".join(sorted(FIELDS)))
            )
        profile.update(overrides)
    return profile


def targets(audience, genre):
    """Return the measured writing targets for an audience and genre.

    `sentence_words` is a band over SINGLE sentences, and `max` is a ceiling to
    test sentence by sentence -- not an average to compare a text's mean
    against. BAREC annotates a text at the level of its single most difficult
    element, so a text averaging 13 words -- the advanced median -- but carrying
    one 40-word sentence is not an advanced text, because 40 exceeds the
    advanced cap of 26. Checks built on this must walk sentences, not means,
    and report what exceeds the declared band rather than sorting a text into
    one.

    `verbal_ratio` is guidance for the writing side, not something this skill
    verifies: measuring it needs a part-of-speech tagger, which this
    standard-library-only pack does not ship. It is `None` when no figure has
    been measured for the genre; the key is always present, so a caller can
    tell "unmeasured" from a measured value -- and must test `is None`, never
    truthiness, because a genuine 0.0 is falsy too.

    An unknown audience raises, an unknown genre does not. The asymmetry is
    deliberate and is the same one `resolve` draws between keys and values: the
    audience set is closed by registers.json and drives a real cap, so an
    unmatched audience can only be a mistake; the genre space is open -- an
    author may declare a genre nobody has measured -- so a typo cannot be told
    apart from a legitimate new genre, and raising would reject the legitimate
    case to catch the other.

    The result is a deep copy: the band is nested, so handing back a shallow
    copy would let one caller rewrite every later caller's cap.
    """
    if audience not in _REG["audience"]:
        raise ValueError(
            "Unknown audience %r. Choose one of: %s"
            % (audience, ", ".join(sorted(AUDIENCES)))
        )
    out = copy.deepcopy(_REG["audience"][audience])
    out["verbal_ratio"] = _REG["genre_verbal_ratio"].get(genre)
    return out
