"""Tests for shared/doc_stats.py, against the planted problems. Run: python3 -m unittest discover tests"""

import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "shared"))
import doc_stats  # noqa: E402

REPORT_MD = os.path.join(ROOT, "samples", "report", "built", "report.md")
REPORT_DOCX = os.path.join(ROOT, "samples", "report", "built", "report.docx")
THESIS = os.path.join(ROOT, "samples", "thesis", "ch3-desks.tex")
REPORT_BANNED = ["leverage", "going forward", "in order to", "very", "basically", "it is important to note that"]
THESIS_BANNED = ["very", "clearly", "obviously", "it is worth noting", "novel"]

# From samples/report/planted.md: every sentence over 25 words, with its place.
REPORT_LONG = [
    ("Background, paragraph 1", 59),
    ("How the pilot worked, paragraph 7", 28),
    ("Results > Cost per order, paragraph 1", 26),
    ("Results > Cost per order, paragraph 3", 54),
    ("Results > Returns and losses, paragraph 3", 26),
    ("Results > Driver time, paragraph 1", 51),
    ("Results > Driver time, paragraph 3", 28),
    ("Risks and costs of a full rollout, paragraph 3", 29),
]
# From samples/thesis/planted.md.
THESIS_LONG = [
    ("Introduction, paragraph 1", 31),
    ("Introduction, paragraph 2", 29),
    ("The model, paragraph 1", 31),
    ("The model, paragraph 1", 29),
    ("Waiting times, paragraph 2", 63),
    ("A staffing rule, paragraph 2", 44),
    ("Checking the model against the desk logs, paragraph 1", 29),
    ("Checking the model against the desk logs, paragraph 5", 27),
]


def long_list(path, banned=()):
    _, _, longs, found, dashes, new_marks = doc_stats.stats(path, 25, banned)
    parsed = []
    for line in longs:
        m = re.match(r"(?:.* > )?(?P<where>.*?, paragraph \d+): (?P<n>\d+) words", line)
        where = m.group("where")
        parsed.append((where, int(m.group("n"))))
    return parsed, found, dashes, new_marks


def strip_chapter(pairs):
    return [(w.split(" > ", 1)[1] if w.startswith("Sizing") else w, n) for w, n in pairs]


class DocStats(unittest.TestCase):
    def test_report_markdown_long_sentences(self):
        _, _, longs, _, _, _ = doc_stats.stats(REPORT_MD, 25, REPORT_BANNED)
        found = [(re.match(r"(.*?): (\d+) words", l).group(1), int(re.match(r"(.*?): (\d+) words", l).group(2)))
                 for l in longs]
        self.assertEqual(found, REPORT_LONG)

    def test_report_word_long_sentences(self):
        _, _, longs, _, _, _ = doc_stats.stats(REPORT_DOCX, 25)
        found = [(re.match(r"(.*?): (\d+) words", l).group(1), int(re.match(r"(.*?): (\d+) words", l).group(2)))
                 for l in longs]
        self.assertEqual(found, REPORT_LONG)

    def test_report_banned_words_and_dash(self):
        _, _, _, found, dashes, _ = doc_stats.stats(REPORT_MD, 25, REPORT_BANNED)
        joined = "\n".join(found)
        for phrase in REPORT_BANNED:
            self.assertIn('"%s"' % phrase, joined)
        self.assertEqual(dashes, ["Risks and costs of a full rollout, paragraph 2: em dash (1)"])

    def test_thesis_long_sentences(self):
        _, _, longs, _, _, _ = doc_stats.stats(THESIS, 25)
        found = []
        for line in longs:
            m = re.match(r"(.*?): (\d+) words", line)
            where = m.group(1).split(" > ", 1)[1]
            found.append((where, int(m.group(2))))
        self.assertEqual(found, THESIS_LONG)

    def test_thesis_banned_words_and_en_dash(self):
        _, _, _, found, dashes, _ = doc_stats.stats(THESIS, 25, THESIS_BANNED)
        joined = "\n".join(found)
        self.assertIn('Waiting times, paragraph 2: "clearly" (1)', joined)
        self.assertIn('A staffing rule, paragraph 2: "clearly" (1)', joined)
        self.assertIn('"it is worth noting"', joined)
        self.assertEqual(len(dashes), 1)
        self.assertIn('Checking the model against the desk logs, paragraph 1: en dash written "--" (1)', dashes[0])

    def test_voice_and_number_lists_of_the_report(self):
        voice, numbers = doc_stats.voice_and_numbers(REPORT_MD)
        i_line = [v for v in voice if v.startswith("I: ")]
        self.assertEqual(len(i_line), 1)
        self.assertIn("Customer response", i_line[0])  # RP16
        self.assertTrue(any('"twelve weeks"' in n for n in numbers))  # RP15
        self.assertTrue(any('"3 staff"' in n for n in numbers))  # RP15
        self.assertFalse(any("twenty" in n for n in numbers))  # inside the quoted clause (RP13)

    def test_voice_and_number_lists_of_the_thesis(self):
        voice, numbers = doc_stats.voice_and_numbers(THESIS)
        self.assertTrue(any(v.startswith("we: 3,") for v in voice))  # TH07
        self.assertTrue(any(v.startswith("our: 1,") for v in voice))  # TH07
        self.assertTrue(any('"2 desks"' in n for n in numbers))  # TH14

    def test_new_marks(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("## One\n\n[NEW] A new sentence. An old one.\n\n## Two\n\nNothing new here.\n")
        try:
            _, _, _, _, _, new_marks = doc_stats.stats(f.name, 25)
            self.assertEqual(new_marks, ["One, paragraph 1: 1"])
        finally:
            os.unlink(f.name)

    def test_repeated_openings_of_the_samples(self):
        rp20 = ('"In addition," (3): Background, paragraph 4; Results > Returns and losses, paragraph 3; '
                'Recommendation and next steps, paragraph 4')
        for path in (REPORT_MD, REPORT_DOCX):
            self.assertEqual(doc_stats.repeated_openings(path), [rp20])
        self.assertEqual(doc_stats.repeated_openings(REPORT_MD, "Results"), [])  # one per section
        self.assertEqual(doc_stats.repeated_openings(THESIS), [])

    def openings(self, suffix, text, section=None):
        with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as f:
            f.write(text)
        try:
            return doc_stats.repeated_openings(f.name, section)
        finally:
            os.unlink(f.name)

    def test_repeated_openings(self):
        text = ("## One\n\nIn addition, the first.\n\nThe pilot ran here.\n\nThe results show more.\n\n"
                "## Two\n\n**In addition,** the second.\n\nThe pilot ran there.\n\nThe results show less.\n\n"
                "## Three\n\nIn addition, the third.\n\nThe pilot cost less.\n\nThe results show both.\n")
        self.assertEqual(self.openings(".md", text), [
            '"In addition," (3): One, paragraph 1; Two, paragraph 1; Three, paragraph 1',
            '"The results show" (3): One, paragraph 3; Two, paragraph 3; Three, paragraph 3',
        ])  # "The pilot ran" starts only two paragraphs
        self.assertEqual(self.openings(".md", text, "Two"), [])

    def test_repeated_openings_in_latex(self):
        text = ("\\section{One}\n\n\\noindent Taken together, $x$ grows.\n\n"
                "Taken together, the model holds.\n\nTaken~together, it fits.\n")
        self.assertEqual(self.openings(".tex", text), ['"Taken together," (3): One, paragraph 1; One, paragraph 2; '
                                                       'One, paragraph 3'])


if __name__ == "__main__":
    unittest.main()
