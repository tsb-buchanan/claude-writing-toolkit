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

    def test_new_marks(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("## One\n\n[NEW] A new sentence. An old one.\n\n## Two\n\nNothing new here.\n")
        try:
            _, _, _, _, _, new_marks = doc_stats.stats(f.name, 25)
            self.assertEqual(new_marks, ["One, paragraph 1: 1"])
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
