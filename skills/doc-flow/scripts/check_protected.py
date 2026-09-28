#!/usr/bin/env python3
"""Check that an edit kept the protected content of a text.

Protected content: number values, citations, math, cross-references and
labels, links, quotations, and comment marks (keep marks and notes).
Only the format of a number may change, for example "twelve" to "12".

  check_protected.py BEFORE AFTER [--format latex|markdown|text]

BEFORE and AFTER can also be Word files. The check reads a Word file's text
with all tracked changes accepted, so AFTER can be a tracked-changes copy.
It prints one line per kind of content, then a result line. It exits with 1
when protected content changed. docx_tool.py also calls it for Word files.
Standard library only. No network calls.
"""

import argparse
import os
import re
import signal
import sys
from collections import Counter

UNITS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
         "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90}
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
WORD_NUMBER = re.compile(
    r"\b(?:(%s)(?:-(%s))?|(%s))\b" % ("|".join(TENS), "|".join(SMALL), "|".join(UNITS)), re.I)
DIGIT_NUMBER = re.compile(
    r"(?<![\w.,])(?:(?:\\\$|[$\u20ac\u00a3])\s?)?\d+(?:,\d{3})*(?:\.\d+)?(?:\s?(?:%|\\%|per ?cent\b))?(?![\w])")
TIME = re.compile(r"(?<![\w:])\d{1,2}:\d{2}(?![\w:])")

LATEX_MATH = [
    re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray|displaymath|math)(\*?)\}.*?\\end\{\1\2\}", re.S),
    re.compile(r"\\\[.*?\\\]", re.S),
    re.compile(r"\\\(.*?\\\)", re.S),
    re.compile(r"\$\$.*?\$\$", re.S),
    re.compile(r"(?<!\\)\$(?!\$).+?(?<!\\)\$", re.S),
]
MARKDOWN_MATH = [
    re.compile(r"\$\$.*?\$\$", re.S),
    re.compile(r"(?<![\\$\w])\$(?![\s\d$])[^$\n]+?(?<![\s\\])\$(?![\d\w])"),
]
LATEX_CITE = re.compile(
    r"\\(?:cite|citep|citet|parencite|textcite|autocite|footcite|citeauthor|citeyear)\*?"
    r"(?:\[[^\]]*\]){0,2}\{[^}]*\}")
LATEX_REF = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref|nameref|label)\{[^}]*\}")
MARKDOWN_CITE = re.compile(r"\[[^\]\n]*@[\w:.-]+[^\]\n]*\]")
MARKDOWN_REF = re.compile(r"\[\^[^\]\s]+\]")
TEXT_CITE = [
    re.compile(r"\((?:[A-Z][\w'-]+(?: et al\.)?(?:,? (?:and|&) [A-Z][\w'-]+)?,? (?:19|20)\d{2}[a-z]?"
               r"(?:; ?[A-Z][\w'-]+(?: et al\.)?,? (?:19|20)\d{2}[a-z]?)*)\)"),
    re.compile(r"\[\d+(?:\s?[,\u2013-]\s?\d+)*\]"),
]
LINK = re.compile(r"https?://[^\s)>\]}\"']+")
QUOTE = [re.compile(r'"[^"\n]{3,}?"'), re.compile("\u201c[^\u201d]{3,}?\u201d"), re.compile(r"``[^`']{3,}?''")]
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
LATEX_KEEP = re.compile(r"(?m)^[ \t]*%[ \t]*(?:keep light|keep|end keep)\b.*$")
LATEX_COMMENT = re.compile(r"(?<!\\)%.*$", re.M)

KINDS = ("numbers", "citations", "math", "references", "links", "quotations", "marks")


def detect_format(path):
    ext = os.path.splitext(path)[1].lower()
    return {".tex": "latex", ".md": "markdown", ".markdown": "markdown"}.get(ext, "text")


def read_text(path):
    """The text of a file. A Word file gives its text with all tracked changes accepted."""
    if path.lower().endswith(".docx"):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import docx_tool
        doc = docx_tool.Doc(path)
        return "\n\n".join(docx_tool.view_texts(doc.paras, "accepted"))
    with open(path, encoding="utf-8") as f:
        return f.read()


def _take(pattern, text, bucket):
    """Move every match of pattern from text into bucket. Returns the rest."""
    def keep(m):
        bucket.append(m.group(0))
        return " "
    return pattern.sub(keep, text)


def number_value(token):
    """(kind, value) for a number token, or None."""
    t = token.lower().replace("\\", "")
    m = WORD_NUMBER.fullmatch(t)
    if m:
        if m.group(1):
            return ("num", float(TENS[m.group(1)] + (SMALL[m.group(2)] if m.group(2) else 0)))
        return ("num", float(UNITS[m.group(3)]))
    if TIME.fullmatch(t):
        return ("time", t)
    kind = "num"
    if t.startswith(("$", "\u20ac", "\u00a3")):
        kind, t = "money", t[1:].strip()
    if t.endswith("%") or t.endswith("per cent") or t.endswith("percent"):
        kind = "percent"
        t = re.sub(r"\s?(%|per ?cent)$", "", t)
    try:
        return (kind, float(t.replace(",", "")))
    except ValueError:
        return None


def extract(text, fmt="text"):
    """Protected content of a text, as lists per kind."""
    found = {kind: [] for kind in KINDS}
    rest = text
    if fmt == "latex":
        rest = _take(LATEX_KEEP, rest, found["marks"])
        rest = LATEX_COMMENT.sub(" ", rest)
        for pattern in LATEX_MATH:
            rest = _take(pattern, rest, found["math"])
        rest = _take(LATEX_CITE, rest, found["citations"])
        rest = _take(LATEX_REF, rest, found["references"])
    elif fmt == "markdown":
        rest = _take(HTML_COMMENT, rest, found["marks"])
        for pattern in MARKDOWN_MATH:
            rest = _take(pattern, rest, found["math"])
        rest = _take(MARKDOWN_CITE, rest, found["citations"])
        rest = _take(MARKDOWN_REF, rest, found["references"])
    if fmt != "latex":
        for pattern in TEXT_CITE:
            rest = _take(pattern, rest, found["citations"])
    rest = _take(LINK, rest, found["links"])
    for pattern in QUOTE:
        for m in pattern.finditer(rest):
            found["quotations"].append(m.group(0))
    rest = _take(TIME, rest, found["numbers"])
    rest = _take(DIGIT_NUMBER, rest, found["numbers"])
    for m in WORD_NUMBER.finditer(rest):
        found["numbers"].append(m.group(0))
    return found


def compare(before, after, fmt="text"):
    """Differences in protected content between two texts."""
    a, b = extract(before, fmt), extract(after, fmt)
    report = {}
    for kind in KINDS:
        if kind == "numbers":
            continue
        removed = Counter(a[kind]) - Counter(b[kind])
        added = Counter(b[kind]) - Counter(a[kind])
        report[kind] = {"removed": sorted(removed.elements()), "added": sorted(added.elements())}
    values_a = Counter(v for v in map(number_value, a["numbers"]) if v)
    values_b = Counter(v for v in map(number_value, b["numbers"]) if v)
    forms_a, forms_b = {}, {}
    for token in a["numbers"]:
        forms_a.setdefault(number_value(token), Counter())[token] += 1
    for token in b["numbers"]:
        forms_b.setdefault(number_value(token), Counter())[token] += 1
    format_changes = []
    for value in set(forms_a) & set(forms_b):
        old = forms_a[value] - forms_b[value]
        new = forms_b[value] - forms_a[value]
        for x, y in zip(sorted(old.elements()), sorted(new.elements())):
            format_changes.append((x, y))
    report["numbers"] = {
        "removed": sorted(t for v, n in (values_a - values_b).items() for t in _forms(forms_a, v, n)),
        "added": sorted(t for v, n in (values_b - values_a).items() for t in _forms(forms_b, v, n)),
        "gone": sorted(t for v in values_a if v not in values_b for t in forms_a[v]),
        "format_changes": sorted(format_changes),
    }
    return report


def _forms(forms, value, n):
    return list(forms[value].elements())[:n]


def changed(report):
    """True when protected content changed. Number format changes do not count."""
    return any(report[k]["removed"] or report[k]["added"] for k in KINDS)


def format_report(report):
    lines = []
    for kind in KINDS:
        r = report[kind]
        if not (r["removed"] or r["added"]):
            extra = ""
            if kind == "numbers" and r["format_changes"]:
                extra = " (format changes: %s)" % "; ".join('"%s" to "%s"' % pair for pair in r["format_changes"])
            lines.append("%s: unchanged%s" % (kind, extra))
            continue
        parts = []
        if r["removed"]:
            parts.append("removed %s" % ", ".join(r["removed"]))
        if r["added"]:
            parts.append("added %s" % ", ".join(r["added"]))
        if kind == "numbers" and r["format_changes"]:
            parts.append("format changes: %s" % "; ".join('"%s" to "%s"' % pair for pair in r["format_changes"]))
        if kind == "numbers" and r["gone"]:
            parts.append("no longer anywhere in the text: %s" % ", ".join(r["gone"]))
        lines.append("%s: CHANGED: %s" % (kind, "; ".join(parts)))
    lines.append("result: %s" % ("CHANGED: fix it, or list it for the writer" if changed(report) else "pass"))
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Check that an edit kept the protected content.")
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--format", choices=("latex", "markdown", "text"))
    args = parser.parse_args(argv)
    try:
        before = read_text(args.before)
        after = read_text(args.after)
    except Exception as err:  # a missing file, or a file that is not what its name says
        print("error: %s" % err)
        return 2
    report = compare(before, after, args.format or detect_format(args.before))
    print(format_report(report))
    return 1 if changed(report) else 0


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # stop quietly when output is cut short
    sys.exit(main(sys.argv[1:]))
