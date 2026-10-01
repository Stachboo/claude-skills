# arabic-writing

An [Agent Skill](https://agentskills.io) for reviewing and writing Modern Standard Arabic, with a
checker that exits non-zero when a sourced hard rule is broken.

It is built for one situation in particular: **you have to approve Arabic text and you do not read
Arabic.** Every finding prints in English — the rule, the fix, and the source — and the Arabic
appears only as the excerpt, which is the evidence you hand to someone who does read it.

**Beginner guides:** [Français](GUIDE.fr.md) · [العربية](GUIDE.ar.md)

## What makes it different from asking a model to "check my Arabic"

We measured that. Five agents were given Arabic tasks without this skill and their output was
scored ([`tests/baseline/results-red.md`](tests/baseline/results-red.md)). **Not one mechanical
check fired on any generated text** — a capable model already writes clean Arabic punctuation.

What it did instead was invent a rule. Asked to review a degraded text, an agent declared that the
dash used for a parenthetical is "an English/French typographic convention imported into Arabic".
That is false: the dash has that exact use in Aḥmad Zakī Bāšā's 1912 treatise that founded Arabic
punctuation, is confirmed by Hārūn, and is exemplified verbatim in the World Bank's Arabic style
guide. Fifteen observations, **not one carrying a source**.

With the skill, the same scenario returns ten observations, **all of them labelled** — seven
carrying a chain to a source, three explicitly marked as not established — plus a section that
names the dash claim and refutes it
([`tests/baseline/results-green.md`](tests/baseline/results-green.md)).

**The skill is not here to find your typos. It is here to stop confident invention.**

## Install

A skill is just a directory. Copy this one into wherever your agent looks for skills, keeping the
directory name `arabic-writing`.

Paths below were verified at each vendor's documentation on 2026-09-17.

| host | user-level directory |
|---|---|
| **Claude Code** | `~/.claude/skills/arabic-writing/` |
| **Cursor** | `~/.agents/skills/` or `~/.cursor/skills/` (also reads `~/.claude/skills/`) |
| **Codex / ChatGPT** | `$HOME/.agents/skills/arabic-writing/` |
| **Gemini CLI** | `~/.agents/skills/` or `~/.gemini/skills/` (the `.agents` alias wins) |

**`~/.agents/skills/` is the emerging cross-host convention** — Cursor, Codex and Gemini CLI all
read it, so one copy there serves all three. Claude Code reads `~/.claude/skills/`.

The skill lives in the `skills/arabic-writing/` folder of
[Stachboo/claude-skills](https://github.com/Stachboo/claude-skills). Clone the repository once,
then copy that one folder:

```bash
git clone https://github.com/Stachboo/claude-skills.git
mkdir -p ~/.agents/skills ~/.claude/skills
cp -r claude-skills/skills/arabic-writing ~/.agents/skills/
# and, for Claude Code:
cp -r claude-skills/skills/arabic-writing ~/.claude/skills/
```

On Windows (PowerShell):

```powershell
git clone https://github.com/Stachboo/claude-skills.git
New-Item -ItemType Directory -Force "$HOME\.agents\skills", "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse claude-skills\skills\arabic-writing "$HOME\.agents\skills\"
Copy-Item -Recurse claude-skills\skills\arabic-writing "$HOME\.claude\skills\"
```

No git? Download the repository as a ZIP from its GitHub page (**Code → Download ZIP**), unzip it,
and copy the `skills/arabic-writing` folder to the same places.

In Claude Code you can also install it with every other skill of the repository through the plugin
marketplace: `/plugin marketplace add Stachboo/claude-skills`, then
`/plugin install stachboo-skills@stachboo-skills`.

For a project rather than a user, drop the leading `~/` — `.agents/skills/`, `.claude/skills/`.

Forty-six products were listed as implementing the format on 2026-09-17, including Copilot, VS Code,
OpenCode, Goose, Amp, Roo Code and Kiro. See the
[client showcase](https://agentskills.io/clients) for where each one looks for skills.

**Requirements: Python 3.8+, standard library only.** No pip install, no model downloads, no
network. The checker reads a UTF-8 file and prints.

### Which Python command?

Every example below says `python`. The name of that command depends on your system:

| system | command | if it is missing |
|---|---|---|
| **Windows** | `python` (or `py`) | install from [python.org](https://www.python.org/downloads/) and tick **Add python.exe to PATH** |
| **macOS** | `python3` | run `xcode-select --install`, or install from python.org |
| **Linux** | `python3` | `sudo apt install python3` (Debian/Ubuntu) or your distribution's package |

Check with `python --version` or `python3 --version`: anything from 3.8 up works. On macOS and Linux,
type `python3` wherever this page says `python`. An AI agent running the skill adapts on its own;
this table is for when you run the checker yourself.

## Use it

```bash
cd arabic-writing
python scripts/check.py FILE --preset news
```

Seven presets — `news`, `magazine`, `literary`, `legal`, `reference`, `religious`, `children` — each
resolving six fields from one word. Use `--set FIELD=VALUE` when no preset fits.

| exit | meaning |
|---|---|
| **0** | judged, no hard rule violated |
| **1** | judged, **a hard rule was violated** |
| **2** | **the run could not happen** — unreadable, not UTF-8, unknown preset, no Arabic in the file |

**Exit 2 is not a verdict.** It never means clean and never means failed. Fix the input and re-run.

Full instructions are in [`SKILL.md`](SKILL.md); your agent reads it on its own.

## How a rule earns its severity

Three severities, and the gate between them is the point of the project.

- **`hard`** — exits 1. A rule reaches this only with **a source and a corpus count**. Unanimous
  across consulted authorities, and context-free: no genre, school or register makes it acceptable.
  There are four.
- **`recommendation`** — reports, never blocks. Real editorial preferences that published Arabic
  does not follow unanimously.
- **`divergence`** — never judges spelling. Where the academies genuinely contradict each other, the
  checker measures consistency against the profile you declared and refuses to pick a winner.
  The first one, `AR-TANWIN-01`, reports a text that places tanwīn al-fatḥ both ways (`أيضًا` and
  `أيضاً`): published Arabic splits 7 publishers to 6 on it, so neither is called wrong.

`AR-ORTH-01` shows the gate working. The Cairo Academy decided the numerals three to nine are
written detached from *miʾa*, with four stated motives. Then it was counted: across all thirty
sources of BAREC the joined form outnumbers the detached **60 to 3**, and a sweep of 11,888
sentences gave 17 findings and **0 true positives — precision 0.00**. The pattern was correct and
the *severity* was wrong. It was demoted, and the reasoning ships with it.

**Every rule carries its chain.** See [`references/sources.md`](references/sources.md), where each
source is marked `[verified]` (read first-hand), `[reported]` (read through a summary) or still
pending — including the ones that are not good enough yet.

## What it does not do

It is not a spell checker. It does not rule on fiqh and never overrides a qualified human on
scripture. It does not settle where the academies disagree. It does not measure the verbal/nominal
ratio and does not check the `school`, `digits` or `italics` fields — no tagger ships here and no
rule consumes those three. It is aimed at **human-written, legacy, translated and CMS-pasted
Arabic**, not at freshly generated text, which measurably already passes its mechanical checks.

One number in it has no source: `AR-DIAC-01`'s threshold of 200 diacritics per 1000 letters is
**provisional**, and says so where it is defined.

## Tests

```bash
python -m unittest discover -s tests -t .
```

158 tests. They include a false-positive budget measured over a clean corpus, because the risk this
project actually runs is not missing an error — it is inventing one.

## Licence

MIT for the code, assets and documentation — see [`LICENSE`](LICENSE).

The twelve Arabic fixtures under `tests/fixtures/clean/` are excerpts from the **BAREC Corpus v1.0**
and keep its **CC BY-SA 4.0** licence. Each file carries its own attribution on its first line, and
[`NOTICE`](NOTICE) explains the split, why it does not make the rest of the skill ShareAlike, and
what you lose if you delete them.

> Elmadani, Habash & Taha-Thomure, *A Large and Balanced Corpus for Fine-grained Arabic Readability
> Assessment*, Findings of ACL 2025. <https://barec.camel-lab.com>
