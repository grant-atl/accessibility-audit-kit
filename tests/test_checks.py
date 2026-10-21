"""Behavior of the opt-in project check runner and its Claude Code hook mode."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parent.parent / "skills/accessibility-checks"
SCRIPT = SKILL / "scripts/checks.py"
CLEAN_ENV = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


@unittest.skipUnless(os.name == "posix", "runner supports POSIX only")
class ChecksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, env=CLEAN_ENV)

    def tearDown(self):
        self.tmp.cleanup()

    def configure(self, exit_code=0, claude=False, timeout=30, sleep=0):
        code = f"import sys, time; time.sleep({sleep}); sys.exit({exit_code})"
        config = {"command": [sys.executable, "-c", code], "timeout_seconds": timeout, "claude": claude}
        (self.root / ".accessibility-checks.json").write_text(json.dumps(config))

    def cli(self, action):
        return subprocess.run([sys.executable, str(SCRIPT), action, "--project", str(self.root)],
                              capture_output=True, text=True, env=CLEAN_ENV)

    def hook(self, tool="Edit"):
        event = {"hook_event_name": "PostToolUse", "tool_name": tool, "cwd": str(self.root),
                 "tool_input": {"file_path": str(self.root / "index.html")}}
        return subprocess.run([sys.executable, str(SCRIPT), "claude"], input=json.dumps(event),
                              capture_output=True, text=True, env=CLEAN_ENV)

    def test_run_requires_config(self):
        self.assertEqual(self.cli("run").returncode, 1)

    def test_run_propagates_status(self):
        self.configure(0)
        self.assertEqual(self.cli("run").returncode, 0)
        self.configure(3)
        self.assertEqual(self.cli("run").returncode, 3)

    def test_timeout_is_not_a_pass(self):
        self.configure(0, timeout=1, sleep=5)
        result = self.cli("run")
        self.assertEqual(result.returncode, 1)
        self.assertIn("timed out", result.stderr)

    def test_shell_string_and_unknown_keys_rejected(self):
        config = self.root / ".accessibility-checks.json"
        config.write_text(json.dumps({"command": "npm test"}))
        self.assertEqual(self.cli("run").returncode, 1)
        config.write_text(json.dumps({"command": ["true"], "extra": 1}))
        self.assertEqual(self.cli("run").returncode, 1)

    def test_hook_is_noop_without_trust(self):
        self.configure(1, claude=True)
        self.assertEqual(self.hook().returncode, 0)

    def test_hook_ignores_other_tools(self):
        self.configure(1, claude=True)
        self.cli("trust")
        self.assertEqual(self.hook("Bash").returncode, 0)

    def test_trust_requires_claude_flag(self):
        self.configure(0, claude=False)
        self.assertEqual(self.cli("trust").returncode, 1)

    def test_trusted_hook_reports_failure_then_revoke(self):
        self.configure(1, claude=True)
        self.assertEqual(self.cli("trust").returncode, 0)
        result = self.hook()
        self.assertEqual(result.returncode, 2)
        self.assertIn("edit was saved", result.stderr)
        self.assertEqual(self.cli("revoke").returncode, 0)
        self.assertEqual(self.hook().returncode, 0)

    def test_config_change_invalidates_trust(self):
        self.configure(0, claude=True)
        self.cli("trust")
        self.assertEqual(self.hook().returncode, 0)
        self.configure(0, claude=True, timeout=31)
        result = self.hook()
        self.assertEqual(result.returncode, 2)
        self.assertIn("changed", result.stderr)

    def test_pre_commit_template_blocks_and_allows_commits(self):
        """Install the bundled hook exactly as setup.md describes, then commit for real."""
        import shutil
        hooks = self.root / ".githooks"
        hooks.mkdir()
        shutil.copy(SKILL / "assets/pre-commit", hooks / "pre-commit")
        (hooks / "pre-commit").chmod(0o755)
        (self.root / "scripts").mkdir()
        shutil.copy(SCRIPT, self.root / "scripts/accessibility-checks.py")
        git = ["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git + ["config", "--local", "core.hooksPath", ".githooks"], check=True, env=CLEAN_ENV)

        def commit(message):
            (self.root / "page.html").write_text(message)
            subprocess.run(git + ["add", "-A"], check=True, env=CLEAN_ENV)
            return subprocess.run(git + ["commit", "-q", "-m", message], capture_output=True, text=True, env=CLEAN_ENV)

        self.configure(1)
        self.assertNotEqual(commit("failing check").returncode, 0)
        self.configure(0)
        self.assertEqual(commit("passing check").returncode, 0)
        log = subprocess.run(git + ["log", "--format=%s"], capture_output=True, text=True, env=CLEAN_ENV).stdout
        self.assertEqual(log.split(), ["passing", "check"])


if __name__ == "__main__":
    unittest.main()
