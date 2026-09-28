"""Tests for skills/notation-check/scripts/symbols.py. Run: python3 -m unittest discover tests"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "notation-check", "scripts"))
import symbols  # noqa: E402

THESIS = os.path.join(ROOT, "samples", "thesis")
CH2 = os.path.join(THESIS, "ch2-background.tex")
CH3 = os.path.join(THESIS, "ch3-desks.tex")


def uses(path):
    out = {}
    for symbol, line, context, is_def, keep in symbols.scan(path):
        out.setdefault(symbol, []).append((line, is_def, keep))
    return out


class Symbols(unittest.TestCase):
    def test_every_symbol_of_the_sample_thesis(self):
        found = set(uses(CH2)) | set(uses(CH3))
        self.assertEqual(found, {"\\lambda", "\\mu", "N", "\\rho", "P_w", "W", "W_q", "\\Lambda"})

    def test_the_clash_shows_as_two_definitions(self):
        n_defs = [line for line, is_def, _ in uses(CH3)["N"] if is_def]
        self.assertEqual(len(n_defs), 2)  # N = lambda W, and N = 0.67

    def test_the_variant_is_found_once_in_its_equation(self):
        report = symbols.report([CH2, CH3], "\\Lambda")
        self.assertIn("\\Lambda: 1 use(s)", report)
        self.assertIn("(eq:saturday)", report)

    def test_first_use_of_w_comes_before_its_definition(self):
        w = uses(CH3)["W"]
        first = w[0][0]
        defined = [line for line, is_def, _ in w if is_def][0]
        self.assertLess(first, defined)

    def test_keep_light_uses_are_marked(self):
        marks = {keep for _, _, keep in uses(CH3)["\\lambda"]}
        self.assertIn("keep light", marks)

    def test_text_and_labels_and_comments_are_not_symbols(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.tex")
            with open(path, "w", encoding="utf-8") as f:
                f.write("% a comment with $z$ in it\n"
                        "The rate is \\(x = 2\\ \\text{per hour}\\).\n"
                        "\\begin{equation}\n  y = \\hat{\\theta} x_{i} \\label{eq:y}\n\\end{equation}\n"
                        "It costs \\$5 and \\$10.\n")
            found = uses(path)
        self.assertEqual(set(found), {"x", "y", "\\hat{\\theta}", "x_i"})

    def test_markdown_money_is_not_math(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("It cost $5 and then $10.\n\nThe rate $\\lambda$ holds.\n\n$$\nq = \\lambda t\n$$\n")
            found = uses(path)
        self.assertEqual(set(found), {"\\lambda", "q", "t"})


if __name__ == "__main__":
    unittest.main()
