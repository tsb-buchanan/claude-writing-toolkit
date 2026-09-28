"""Tests for shared/docx_tool.py, on the sample report. Run: python3 -m unittest discover tests"""

import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared"))
import docx_tool  # noqa: E402

REPORT = os.path.join(ROOT, "samples", "report", "built", "report.docx")


def accepted(path):
    doc = docx_tool.Doc(path)
    return docx_tool.view_texts(doc.paras, "accepted")


class DocxTool(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def apply(self, changes):
        spec = os.path.join(self.tmp, "changes.json")
        out = os.path.join(self.tmp, "out.docx")
        with open(spec, "w", encoding="utf-8") as f:
            json.dump({"author": "Claude", "changes": changes}, f)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = docx_tool.cmd_apply(REPORT, spec, out)
        return code, buf.getvalue(), out

    # ------------------------------------------------------------ reading

    def test_check_protected_reads_a_tracked_copy(self):
        script = os.path.join(ROOT, "shared", "check_protected.py")
        p18 = accepted(REPORT)[17]
        code, _, out = self.apply([{"op": "replace", "para": 18, "text": p18.replace("twelve weeks", "12 weeks")}])
        self.assertEqual(code, 0)
        run = subprocess.run([sys.executable, script, REPORT, out], stdout=subprocess.PIPE, text=True)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn('"twelve" to "12"', run.stdout)
        self.apply([{"op": "replace", "para": 18, "text": p18.replace("225 orders", "250 orders")}])
        run = subprocess.run([sys.executable, script, REPORT, out], stdout=subprocess.PIPE, text=True)
        self.assertEqual(run.returncode, 1, run.stdout)

    def test_apply_never_overwrites_without_replace(self):
        script = os.path.join(ROOT, "shared", "docx_tool.py")
        spec = os.path.join(self.tmp, "c.json")
        out = os.path.join(self.tmp, "out.docx")
        with open(spec, "w", encoding="utf-8") as f:
            json.dump({"changes": [{"op": "delete", "para": 17}]}, f)
        run = lambda *extra: subprocess.run([sys.executable, script, "apply", REPORT, spec, out] + list(extra),
                                            stdout=subprocess.PIPE, text=True)
        self.assertEqual(run().returncode, 0)
        second = run()
        self.assertEqual(second.returncode, 2)
        self.assertIn("already exists", second.stdout)
        self.assertEqual(run("--replace").returncode, 0)
        same = subprocess.run([sys.executable, script, "apply", REPORT, spec, REPORT, "--replace"],
                              stdout=subprocess.PIPE, text=True)
        self.assertEqual(same.returncode, 2)

    def test_structure(self):
        doc = docx_tool.Doc(REPORT)
        self.assertEqual(len(doc.paras), 71)
        self.assertEqual(len(doc.comments), 2)
        self.assertEqual(doc.keep, {19: "keep"})
        self.assertEqual(doc.label(0), "Title")
        self.assertEqual(doc.label(2), "H1")
        self.assertEqual(doc.label(26), "H2")
        self.assertEqual(doc.label(28), "table")

    def test_sections_by_name_and_number(self):
        doc = docx_tool.Doc(REPORT)
        self.assertEqual(doc.section("Results"), (25, 55))
        self.assertEqual(doc.section("results"), (25, 55))
        self.assertEqual(doc.section("3"), (15, 24))
        self.assertEqual(doc.section("4.2"), (45, 48))
        with self.assertRaises(docx_tool.ToolError):
            doc.section("No such heading")

    def test_outline_is_short(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            docx_tool.cmd_outline(REPORT)
        text = buf.getvalue()
        self.assertIn("p29-p43 [table: 15 cells]", text)
        self.assertIn("p20 [body]", text)
        self.assertIn("{keep}", text)
        self.assertIn("keep mark on p20", text)
        self.assertIn("note on p65", text)
        self.assertLess(len(text.split()), 900)

    # ------------------------------------------------------------ writing

    def test_replace_keeps_every_check(self):
        new = ("The depot delivered 18,900 orders in crates over the 12 weeks. The packaging cost per order "
               "fell from $1.42 with boxes to $0.98 with crates, a fall of 31%. The crate figure includes "
               "washing, the station lease, lost and damaged crates, and the price of the crates over their life.")
        code, out, path = self.apply([{"op": "replace", "para": 28, "expect": "Over the 12 weeks", "text": new}])
        self.assertEqual(code, 0, out)
        self.assertIn("check, reject all gives the original text: yes", out)
        self.assertIn("check, accept all gives the requested text: yes", out)
        self.assertEqual(accepted(path)[27], new)
        self.assertNotIn("protected content", out)

    def test_replace_reports_a_changed_number(self):
        code, out, _ = self.apply([{"op": "replace", "para": 5, "text": "The pilot handled 18,900 orders in 12 weeks."}])
        self.assertEqual(code, 0, out)
        self.assertIn("protected content", out)
        self.assertIn("18,400", out)

    def test_refusals(self):
        code, out, _ = self.apply([
            {"op": "replace", "para": 33, "text": "x"},
            {"op": "replace", "para": 20, "text": "x"},
            {"op": "replace", "para": 19, "text": "x"},
            {"op": "delete", "para": 45, "expect": "Wrong opening words"},
        ])
        self.assertIn("applied: 0 of 4 changes", out)
        self.assertIn("table cell", out)
        self.assertIn("marked keep", out)
        self.assertIn("footnote", out)
        self.assertIn("does not start with", out)

    def test_comment_on_a_whole_paragraph_survives_a_rewrite(self):
        code, out, path = self.apply([{"op": "replace", "para": 65, "text": "Options we did not choose"}])
        self.assertEqual(code, 0, out)
        doc = docx_tool.Doc(path)
        self.assertEqual(len(doc.comments), 2)
        note = [cid for cid, (a, t) in doc.comments.items() if t.startswith("Note")][0]
        self.assertEqual(doc.comment_paras[note], (64, 64))

    def test_delete(self):
        before = accepted(REPORT)
        code, out, path = self.apply([{"op": "delete", "para": 48, "expect": "Drivers collected"}])
        self.assertEqual(code, 0, out)
        after = accepted(path)
        self.assertEqual(after, before[:47] + before[48:])

    def test_move(self):
        before = accepted(REPORT)
        code, out, path = self.apply([{"op": "move", "paras": [68, 68], "after": 3, "expect": "We recommend"}])
        self.assertEqual(code, 0, out)
        after = accepted(path)
        self.assertEqual(after[3], before[67])
        self.assertEqual(after, before[:3] + [before[67]] + before[3:67] + before[68:])

    def test_insert_heading_and_insert_after_a_table(self):
        before = accepted(REPORT)
        code, out, path = self.apply([
            {"op": "insert_after", "para": 3, "text": "[NEW] The board is asked to approve $304,000."},
            {"op": "insert_after", "para": 40, "text": "What the table shows", "style": "Heading2"},
        ])
        self.assertEqual(code, 0, out)
        after = accepted(path)
        self.assertEqual(after[3], "[NEW] The board is asked to approve $304,000.")
        self.assertEqual(after[44], "What the table shows")
        self.assertEqual(after, before[:3] + [after[3]] + before[3:43] + [after[44]] + before[43:])
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        self.assertTrue(re.search(r"</w:tbl><w:p><w:pPr><w:pStyle w:val=\"Heading2\"/>", xml))

    def test_unknown_style_is_refused(self):
        code, out, _ = self.apply([{"op": "insert_after", "para": 3, "text": "x", "style": "Heading9"}])
        self.assertIn("no paragraph style", out)

    def test_from_text(self):
        src = os.path.join(self.tmp, "pasted.txt")
        with open(src, "w", encoding="utf-8") as f:
            f.write("# A heading\n\nFirst paragraph,\nstill the first.\n\n## A subheading\n\nSecond paragraph.\n")
        out = os.path.join(self.tmp, "pasted.docx")
        with contextlib.redirect_stdout(io.StringIO()):
            docx_tool.cmd_from_text(src, out)
        doc = docx_tool.Doc(out)
        self.assertEqual([doc.label(i) for i in range(len(doc.paras))], ["H1", "body", "H2", "body"])
        self.assertEqual(docx_tool.para_text(doc.paras[1]), "First paragraph, still the first.")

    @unittest.skipUnless(shutil.which("soffice"), "LibreOffice is not installed")
    def test_libreoffice_opens_the_result(self):
        code, out, path = self.apply([
            {"op": "replace", "para": 17, "text": "The pilot tested crates, the deposit, collection and washing."},
            {"op": "delete", "para": 48},
            {"op": "move", "paras": [68, 68], "after": 3},
        ])
        self.assertEqual(code, 0, out)
        profile = os.path.join(self.tmp, "profile")
        subprocess.run(["soffice", "--headless", "-env:UserInstallation=file://" + profile,
                        "--convert-to", "odt", "--outdir", self.tmp, path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        odt = os.path.join(self.tmp, "out.odt")
        self.assertTrue(os.path.exists(odt), "LibreOffice could not open the result")
        with zipfile.ZipFile(odt) as z:
            content = z.read("content.xml").decode("utf-8")
        self.assertGreaterEqual(content.count("<text:changed-region"), 4)
        self.assertIn("Claude", content)


if __name__ == "__main__":
    unittest.main()
