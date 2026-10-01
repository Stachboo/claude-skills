import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).split("\n"):
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


class TestFrontmatter(unittest.TestCase):
    def setUp(self):
        self.fm = frontmatter(SKILL.read_text(encoding="utf-8"))

    def test_frontmatter_exists(self):
        self.assertIsNotNone(self.fm, "SKILL.md must start with YAML frontmatter")

    def test_name_matches_directory(self):
        self.assertEqual(self.fm["name"], SKILL.parent.name)

    def test_name_is_spec_compliant(self):
        name = self.fm["name"]
        self.assertTrue(1 <= len(name) <= 64)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_description_length(self):
        d = self.fm["description"]
        self.assertTrue(1 <= len(d) <= 1024, f"description is {len(d)} chars")

    def test_body_under_500_lines(self):
        body = SKILL.read_text(encoding="utf-8").split("---\n", 2)[-1]
        self.assertLess(len(body.split("\n")), 500)

    def test_no_claude_code_only_fields(self):
        """The skill must stay portable across Agent Skills hosts.

        hooks:, model: and effort: are Claude Code proprietary extensions and are
        not in the agentskills.io specification. A skill using them stops being
        portable to Cursor, Gemini CLI, Codex and the other ~30 conforming hosts.
        """
        for field in ("hooks", "model", "effort", "disable-model-invocation", "user-invocable"):
            self.assertNotIn(field, self.fm, f"{field} is not in the portable spec")

    def test_only_spec_fields_present(self):
        # Note on the "version" exclusion: frontmatter() above skips indented
        # lines, so the nested `  version:` under `metadata:` is NOT parsed and
        # does not appear as a sibling key (metadata maps to ""). The exclusion
        # is therefore a no-op today; it is kept as a guard in case the nesting
        # is ever flattened or written inline. Verified 2026-09-17.
        allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
        extra = set(self.fm) - allowed - {"version"}
        self.assertEqual(extra, set(), f"non-spec frontmatter fields: {extra}")
