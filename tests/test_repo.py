"""Structural checks for manifests, skills, references, and links."""

import collections
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise AssertionError(f"{path} has no frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        if line.startswith(" "):
            continue  # nested metadata values
        key, _, value = line.partition(":")
        value = value.strip()
        if value and not value.startswith('"') and ": " in value:
            raise AssertionError(f"{path}: unquoted ': ' in {key} breaks YAML")
        fields[key] = value.strip('"')
    return fields


class ManifestTests(unittest.TestCase):
    def test_versions_agree(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        version = plugin["version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertEqual(market["metadata"]["version"], version)
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(entry["version"], version)
        for skill in SKILLS:
            text = (skill / "SKILL.md").read_text()
            self.assertIn(f'version: "{version}"', text, skill.name)
        self.assertIn(f"## [{version}]", (ROOT / "CHANGELOG.md").read_text())

    def test_hook_targets_existing_script(self):
        hooks = json.loads((ROOT / "hooks/hooks.json").read_text())
        for groups in hooks["hooks"].values():
            for group in groups:
                for hook in group["hooks"]:
                    script = re.search(r"\$CLAUDE_PLUGIN_ROOT/([^\"]+)", hook["command"]).group(1)
                    self.assertTrue((ROOT / script).is_file(), script)

    def test_agents_have_frontmatter(self):
        agents = list((ROOT / "agents").glob("*.md"))
        self.assertTrue(agents)
        for agent in agents:
            fields = frontmatter(agent)
            self.assertEqual(fields["name"], agent.stem)
            self.assertTrue(fields["description"])


class SkillTests(unittest.TestCase):
    def test_expected_skills_present(self):
        self.assertEqual([s.name for s in SKILLS], [
            "accessibility-audit", "accessibility-checks", "accessibility-fix",
            "accessibility-standards", "healthcare-accessibility",
        ])

    def test_frontmatter(self):
        for skill in SKILLS:
            fields = frontmatter(skill / "SKILL.md")
            self.assertEqual(fields["name"], skill.name)
            self.assertRegex(fields["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertTrue(20 <= len(fields["description"]) <= 1024, skill.name)
            self.assertEqual(fields["license"], "MIT")
            if "compatibility" in fields:
                self.assertLessEqual(len(fields["compatibility"]), 500)


class ReferenceTests(unittest.TestCase):
    def test_matrix_counts_and_links(self):
        rows = []
        for line in (ROOT / "skills/accessibility-audit/references/wcag-22-matrix.md").read_text().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 5 and re.fullmatch(r"\d+\.\d+\.\d+", cells[0]):
                rows.append(cells)
        self.assertEqual(collections.Counter(r[1] for r in rows), {"A": 31, "AA": 24, "AAA": 31})
        self.assertNotIn("4.1.1", [r[0] for r in rows])
        for number, _, _, test, _ in rows:
            guide = re.search(r"\[Guide\]\(([^)]+)\)", test)
            self.assertIsNotNone(guide, number)
            self.assertRegex(guide.group(1), r"^https://www\.w3\.org/WAI/WCAG22/Understanding/[a-z0-9-]+\.html$", number)

    def test_relative_markdown_links_resolve(self):
        for doc in ROOT.rglob("*.md"):
            if ".git" in doc.parts:
                continue
            for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", doc.read_text()):
                if re.match(r"^[a-z]+:", target):
                    continue
                self.assertTrue((doc.parent / target).exists(), f"{doc.relative_to(ROOT)} -> {target}")

    def test_json_assets_parse(self):
        for asset in ROOT.glob("skills/*/assets/*.json"):
            json.loads(asset.read_text())


class EvalTests(unittest.TestCase):
    def test_every_skill_has_evals(self):
        for skill in SKILLS:
            folder = ROOT / "evals" / skill.name
            triggers = json.loads((folder / "triggers.json").read_text())
            self.assertTrue(all(set(item) == {"query", "should_trigger"} for item in triggers), skill.name)
            self.assertGreaterEqual(sum(item["should_trigger"] for item in triggers), 5, skill.name)
            self.assertGreaterEqual(sum(not item["should_trigger"] for item in triggers), 4, skill.name)
            behavior = json.loads((folder / "evals.json").read_text())
            self.assertEqual(behavior["skill_name"], skill.name)
            ids = [item["id"] for item in behavior["evals"]]
            self.assertEqual(len(ids), len(set(ids)))
            for item in behavior["evals"]:
                self.assertTrue(item["prompt"] and item["expectations"], (skill.name, item["id"]))
                for path in item.get("files", []):
                    self.assertTrue((ROOT / path).exists(), path)


class SnippetTests(unittest.TestCase):
    SNIPPETS = ROOT / "skills/accessibility-audit/assets/browser"

    def test_snippets_are_self_contained_expressions(self):
        names = sorted(p.name for p in self.SNIPPETS.glob("*.js"))
        self.assertEqual(names, ["page-inventory.js", "reflow.js", "target-size.js", "text-spacing.js"])
        for snippet in self.SNIPPETS.glob("*.js"):
            code = snippet.read_text()
            self.assertNotRegex(code, r"\b(fetch|XMLHttpRequest|sendBeacon|WebSocket)\b", snippet.name)
            self.assertNotRegex(code, r"^\s*(import|export)\b", snippet.name)
            self.assertTrue(code.rstrip().endswith("})();"), snippet.name)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_snippets_parse(self):
        for snippet in self.SNIPPETS.glob("*.js"):
            result = subprocess.run(["node", "--check", str(snippet)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


class ExampleTests(unittest.TestCase):
    def test_live_audit_ledger_validates(self):
        example = ROOT / "examples/live-audit-w3c-demo"
        result = subprocess.run(
            ["python3", str(ROOT / "skills/accessibility-audit/scripts/coverage.py"), "--scope", str(example / "scope.json"),
             "--target", "AA", "--summary", str(example / "coverage.csv")], capture_output=True, text=True)
        # 1 means a complete, valid ledger with failures; 2 would mean the ledger no longer matches the matrix.
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("fail=18", result.stdout)


if __name__ == "__main__":
    unittest.main()
