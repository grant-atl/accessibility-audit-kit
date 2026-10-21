"""Accuracy of the WCAG contrast calculator."""

import filecmp
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/accessibility-audit/scripts/contrast.py"
spec = importlib.util.spec_from_file_location("contrast", SCRIPT)
contrast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contrast)


def checks(result):
    return {(c["criterion"], c["applies_to"]): c["pass"] for c in result["checks"]}


class ContrastTests(unittest.TestCase):
    def test_reference_values(self):
        cases = {("#000", "#fff"): 21.0, ("#fff", "#fff"): 1.0, ("#767676", "#ffffff"): 4.54, ("#777777", "#ffffff"): 4.48}
        for (fg, bg), expected in cases.items():
            self.assertAlmostEqual(contrast.evaluate(fg, bg)["ratio_exact"], expected, places=2, msg=(fg, bg))

    def test_threshold_is_not_rounded_up(self):
        result = contrast.evaluate("#777777", "#ffffff")
        self.assertLess(result["ratio_exact"], 4.5)
        self.assertFalse(checks(result)[("1.4.3", "normal text")])
        self.assertTrue(checks(result)[("1.4.3", "large text")])

    def test_json_ratio_is_truncated_not_rounded(self):
        for fg, bg, shown in (("#101010", "#7b7b7b", 4.49), ("#1b1b1b", "#666666", 2.99)):
            result = contrast.evaluate(fg, bg)
            self.assertEqual(result["ratio"], shown, (fg, bg))
            self.assertLess(result["ratio_exact"], round(result["ratio_exact"], 2))

    def test_target_must_be_a_real_ratio(self):
        for target in ("0", "nan", "1", "22"):
            result = subprocess.run([sys.executable, str(SCRIPT), "#777", "#fff", "--target", target], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, target)

    def test_formats_agree(self):
        expected = contrast.evaluate("#336699", "#fafafa")["ratio_exact"]
        for fg in ("336699", "#369", "rgb(51, 102, 153)", "rgb(51 102 153 / 100%)", "rgba(20%, 40%, 60%, 1)"):
            self.assertAlmostEqual(contrast.evaluate(fg, "#fafafa")["ratio_exact"], expected, places=6, msg=fg)

    def test_alpha_compositing(self):
        half = contrast.evaluate("rgba(0,0,0,.5)", "#ffffff")
        self.assertEqual(half["foreground"], "#808080")
        self.assertTrue(half["notes"])
        overlay = contrast.evaluate("#000000", "rgba(0,0,0,0.4)", base_text="#ffffff")
        self.assertEqual(overlay["background"], "#999999")

    def test_suggestions_reach_target_in_both_directions(self):
        for fg, bg in (("#999999", "#ffffff"), ("#555555", "#222222"), ("#e07a5f", "#f4f1de")):
            tip = contrast.evaluate(fg, bg, target=4.5)["suggestion"]
            self.assertGreaterEqual(contrast.evaluate(tip["color"], bg)["ratio_exact"], 4.5, (fg, bg))
        self.assertIsNone(contrast.evaluate("#777", "#808080", target=7)["suggestion"])

    def test_invalid_input_exits_2(self):
        for args in (["chartreuse", "#fff"], ["#12", "#fff"], ["rgb(300,0,0)", "#fff"], ["#000", "#fff", "--base", "#0000"]):
            result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, args)

    def test_skill_copies_are_identical(self):
        self.assertTrue(filecmp.cmp(SCRIPT, ROOT / "skills/accessibility-fix/scripts/contrast.py", shallow=False))


if __name__ == "__main__":
    unittest.main()
