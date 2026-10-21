"""Behavior of the WCAG 2.2 coverage ledger utility."""

import csv
import json
import os
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent.parent / "skills/accessibility-audit/scripts/coverage.py"


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.scope = self.dir / "scope.json"
        self.scope.write_text(json.dumps([{"location": "https://private.test/account", "states": ["initial", "error"]}]))
        self.ledger = self.dir / "coverage.csv"

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--scope", str(self.scope), *args],
                              capture_output=True, text=True)

    def rows(self):
        with self.ledger.open(newline="") as stream:
            return list(csv.DictReader(stream))

    def write(self, rows):
        with self.ledger.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def test_create_generates_every_row_and_refuses_overwrite(self):
        self.assertEqual(self.run_script("--output", str(self.ledger)).returncode, 0)
        rows = self.rows()
        self.assertEqual(len(rows), 2 * 86)
        self.assertEqual({r["status"] for r in rows}, {"not-tested"})
        self.assertEqual(sum(r["required"] == "yes" for r in rows), 2 * 55)
        self.assertEqual(self.run_script("--output", str(self.ledger)).returncode, 2)

    def test_summary_exit_codes(self):
        self.run_script("--output", str(self.ledger))
        self.assertEqual(self.run_script("--summary", str(self.ledger)).returncode, 1)
        rows = self.rows()
        for row in rows:
            if row["required"] == "yes":
                row["status"], row["evidence"] = "pass", "observed in Safari 19"
        self.write(rows)
        self.assertEqual(self.run_script("--summary", str(self.ledger)).returncode, 0)

    def test_finished_rows_need_evidence(self):
        self.run_script("--output", str(self.ledger))
        rows = self.rows()
        rows[0]["status"] = "pass"
        self.write(rows)
        result = self.run_script("--summary", str(self.ledger))
        self.assertEqual(result.returncode, 2)
        self.assertIn("evidence", result.stderr)

    def test_dropped_row_is_rejected(self):
        self.run_script("--output", str(self.ledger))
        self.write(self.rows()[1:])
        self.assertEqual(self.run_script("--summary", str(self.ledger)).returncode, 2)

    def test_report_names_criteria_but_not_locations(self):
        self.run_script("--output", str(self.ledger))
        rows = self.rows()
        rows[0]["status"], rows[0]["evidence"] = "fail", "missing alt on hero"
        self.write(rows)
        report = self.dir / "summary.md"
        result = self.run_script("--summary", str(self.ledger), "--report", str(report))
        self.assertEqual(result.returncode, 1)
        text = report.read_text()
        self.assertIn("| 1.1.1 | A | Non-text Content | 1 |", text)
        self.assertNotIn("private.test", text)
        self.assertNotIn("missing alt", text)
        self.assertNotIn("private.test", result.stdout + result.stderr)
        self.assertEqual(self.run_script("--summary", str(self.ledger), "--report", str(report)).returncode, 2)

    def test_report_requires_summary(self):
        self.assertNotEqual(self.run_script("--output", str(self.ledger), "--report", "x.md").returncode, 0)

    def test_spreadsheet_formula_prefix_rejected(self):
        self.scope.write_text(json.dumps([{"location": "=HYPERLINK(1)", "states": ["initial"]}]))
        self.assertEqual(self.run_script("--output", str(self.ledger)).returncode, 2)

    def write_slice(self, name, rows):
        path = self.dir / name
        with path.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["location", "state", "criterion", "status", "evidence", "environment", "notes"])
            writer.writerows(rows)
        return path

    def test_merge_fills_rows_from_slices(self):
        self.run_script("--output", str(self.ledger))
        loc = "https://private.test/account"
        a = self.write_slice("a.csv", [[loc, "initial", "1.1.1", "fail", "hero img has no alt", "Safari 19", ""]])
        b = self.write_slice("b.csv", [[loc, "error", "1.4.3", "pass", "=4.6:1 measured", "Safari 19", "-ok"]])
        result = self.run_script("--merge", str(self.ledger), "--input", str(a), str(b))
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = {(r["state"], r["criterion"]): r for r in self.rows()}
        self.assertEqual(rows[("initial", "1.1.1")]["status"], "fail")
        self.assertEqual(rows[("error", "1.4.3")]["evidence"], "'=4.6:1 measured")
        self.assertEqual(rows[("error", "1.4.3")]["notes"], "'-ok")
        self.assertEqual(rows[("error", "1.1.1")]["status"], "not-tested")
        # Re-merging identical data is idempotent; conflicting data is refused without writing.
        self.assertEqual(self.run_script("--merge", str(self.ledger), "--input", str(a)).returncode, 0)
        before = self.ledger.read_text()
        c = self.write_slice("c.csv", [[loc, "initial", "1.1.1", "pass", "alt present", "Safari 19", ""]])
        self.assertEqual(self.run_script("--merge", str(self.ledger), "--input", str(c)).returncode, 2)
        self.assertEqual(self.ledger.read_text(), before)

    def test_merge_neutralizes_space_prefixed_formulas_and_keeps_mode(self):
        self.run_script("--output", str(self.ledger))
        os.chmod(self.ledger, 0o644)
        loc = "https://private.test/account"
        a = self.write_slice("a.csv", [[loc, "initial", "1.1.1", "fail", '  =HYPERLINK("http://evil")', "", ""]])
        self.assertEqual(self.run_script("--merge", str(self.ledger), "--input", str(a)).returncode, 0)
        row = next(r for r in self.rows() if r["state"] == "initial" and r["criterion"] == "1.1.1")
        self.assertTrue(row["evidence"].startswith("'"))
        self.assertEqual(stat.S_IMODE(os.stat(self.ledger).st_mode), 0o644)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir() if p.name.startswith("tmp")), [])

    def test_merge_refuses_symlinked_ledger(self):
        self.run_script("--output", str(self.ledger))
        link = self.dir / "link.csv"
        link.symlink_to(self.ledger)
        a = self.write_slice("a.csv", [["https://private.test/account", "initial", "1.1.1", "fail", "x", "", ""]])
        self.assertEqual(self.run_script("--merge", str(link), "--input", str(a)).returncode, 2)
        self.assertTrue(link.is_symlink())

    def test_merge_rejects_bad_slices(self):
        self.run_script("--output", str(self.ledger))
        loc = "https://private.test/account"
        bad = [
            [[loc, "initial", "4.1.1", "pass", "x", "", ""]],
            [["https://elsewhere.test", "initial", "1.1.1", "pass", "x", "", ""]],
            [[loc, "initial", "1.1.1", "pass", "", "", ""]],
            [[loc, "initial", "1.1.1", "fail", "x", "", ""], [loc, "initial", "1.1.1", "fail", "x", "", ""]],
        ]
        for i, rows in enumerate(bad):
            path = self.write_slice(f"bad{i}.csv", rows)
            result = self.run_script("--merge", str(self.ledger), "--input", str(path))
            self.assertEqual(result.returncode, 2, i)
            self.assertNotIn("private.test", result.stderr)
        self.assertNotEqual(self.run_script("--merge", str(self.ledger)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
