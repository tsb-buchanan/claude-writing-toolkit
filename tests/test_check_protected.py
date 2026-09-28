"""Tests for shared/check_protected.py. Run: python3 -m unittest discover tests"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared"))
import check_protected as cp  # noqa: E402


class CheckProtected(unittest.TestCase):
    def check(self, before, after, fmt="text"):
        report = cp.compare(before, after, fmt)
        return cp.changed(report), report

    def test_number_format_changes_pass(self):
        changed, report = self.check("It ran for twelve weeks with 3 staff.", "It ran for 12 weeks with three staff.")
        self.assertFalse(changed)
        self.assertIn(("twelve", "12"), report["numbers"]["format_changes"])
        self.assertIn(("3", "three"), report["numbers"]["format_changes"])

    def test_changed_value_is_caught(self):
        changed, report = self.check("It handled 18,400 orders.", "It handled 18,900 orders.")
        self.assertTrue(changed)
        self.assertEqual(report["numbers"]["removed"], ["18,400"])
        self.assertEqual(report["numbers"]["gone"], ["18,400"])

    def test_percent_and_money_keep_their_kind(self):
        changed, _ = self.check("It fell by 31% to $0.98.", "It fell by 31 to $0.98.")
        self.assertTrue(changed)

    def test_markdown_money_is_not_math(self):
        changed, report = self.check("It fell from $1.42 to $0.98, or 31%.", "It fell from $1.42 to $0.98 (31% less).", "markdown")
        self.assertFalse(changed)
        self.assertEqual(cp.extract("from $1.42 to $0.98", "markdown")["math"], [])

    def test_latex_prose_may_change_around_protected_content(self):
        before = (r"as shown in the very well known result \cite{example2021}, which gives "
                  r"\begin{equation} W_q = \frac{P_w}{N\mu - \lambda}, \label{eq:wq} \end{equation} "
                  r"see Section~\ref{sec:logs}.")
        after = (r"as shown in \cite{example2021}. This gives "
                 r"\begin{equation} W_q = \frac{P_w}{N\mu - \lambda}, \label{eq:wq} \end{equation} "
                 r"See Section~\ref{sec:logs}.")
        changed, _ = self.check(before, after, "latex")
        self.assertFalse(changed)

    def test_symbol_change_inside_math_is_caught(self):
        changed, report = self.check("about $N = 0.67$ borrowers", "about $L = 0.67$ borrowers", "latex")
        self.assertTrue(changed)
        self.assertEqual(report["math"]["removed"], ["$N = 0.67$"])

    def test_dropped_citation_is_caught(self):
        changed, report = self.check(r"as shown \cite{example2021}.", "as shown.", "latex")
        self.assertTrue(changed)
        self.assertEqual(report["citations"]["removed"], [r"\cite{example2021}"])

    def test_text_citations(self):
        changed, _ = self.check("as found before (Sample, 2019) and [12].", "as found before [12].")
        self.assertTrue(changed)

    def test_quotation_change_is_caught(self):
        before = 'Clause 7.2 reads: "The Supplier shall replace any crate within twenty-four months."'
        after = 'Clause 7.2 reads: "The Supplier shall replace any crate within 24 months."'
        changed, report = self.check(before, after)
        self.assertTrue(changed)
        self.assertTrue(report["quotations"]["removed"])

    def test_keep_marks_must_stay(self):
        changed, _ = self.check("<!-- keep -->\nText.\n<!-- end keep -->", "Text.", "markdown")
        self.assertTrue(changed)
        changed, _ = self.check("% keep light: from a paper\nText.\n% end keep", "Text.", "latex")
        self.assertTrue(changed)

    def test_range_written_with_to_passes(self):
        changed, _ = self.check("ran at 16--22 per hour from 14:00", "ran at 16 to 22 per hour from 14:00", "latex")
        self.assertFalse(changed)

    def test_command_line_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b, c = (os.path.join(tmp, n) for n in ("a.md", "b.md", "c.md"))
            for path, text in ((a, "It handled 18,400 orders."), (b, "It handled 18,400 orders in all."),
                               (c, "It handled 18,900 orders.")):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
            script = os.path.join(ROOT, "shared", "check_protected.py")
            self.assertEqual(subprocess.run([sys.executable, script, a, b], stdout=subprocess.DEVNULL).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, script, a, c], stdout=subprocess.DEVNULL).returncode, 1)


if __name__ == "__main__":
    unittest.main()
