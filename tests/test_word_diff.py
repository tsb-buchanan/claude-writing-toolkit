"""Tests for shared/word_diff.py. Run: python3 -m unittest discover tests"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared"))
import word_diff  # noqa: E402


class WordDiff(unittest.TestCase):
    def test_changed_words_are_marked(self):
        out = word_diff.diff("One.\nIt ran for twelve weeks.\nThree.\n", "One.\nIt ran for 12 weeks.\nThree.\n")
        self.assertEqual(out, "@@ new line 2\nIt ran for [-twelve-] {+12+} weeks.")

    def test_unchanged_text_is_left_out(self):
        self.assertEqual(word_diff.diff("Same.\n", "Same.\n"), "no changes")

    def test_removed_and_added_lines(self):
        out = word_diff.diff("A.\nCut me.\nB.\n", "A.\nB.\nNew line.\n")
        self.assertIn("[-Cut me.-]", out)
        self.assertIn("{+New line.+}", out)

    def test_very_different_text_shows_old_then_new(self):
        out = word_diff.diff("x\nthe cat sat on the mat today\n", "x\nprices rose sharply in every region\n")
        self.assertIn("[-the cat sat on the mat today-]\n{+prices rose sharply in every region+}", out)

    def test_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = os.path.join(tmp, "a.tex"), os.path.join(tmp, "b.tex")
            with open(a, "w", encoding="utf-8") as f:
                f.write("We assume $\\Lambda$ here.\n")
            with open(b, "w", encoding="utf-8") as f:
                f.write("We assume $\\lambda$ here.\n")
            run = subprocess.run([sys.executable, os.path.join(ROOT, "shared", "word_diff.py"), a, b],
                                 stdout=subprocess.PIPE, text=True)
        self.assertEqual(run.returncode, 0)
        self.assertIn("[-$\\Lambda$-] {+$\\lambda$+}", run.stdout)


if __name__ == "__main__":
    unittest.main()
