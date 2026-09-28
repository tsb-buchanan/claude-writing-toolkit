#!/usr/bin/env python3
"""Count words, long sentences, banned words, dashes and [NEW] marks per section.

  doc_stats.py FILE [--limit 25] [--banned "very, basically"] [--section NAME]

It also lists, for a person to judge against the profile: each first-person word
(voice), each number under 10 written in digits, and each number from ten written
in words. Text inside quotation marks is left out of these two lists.

FILE can be Word (.docx), LaTeX (.tex), Markdown (.md) or plain text.
Paragraphs are counted from 1 in each section or subsection. Headings and tables
do not count. A LaTeX display equation stays part of the sentence around it.
Standard library only. No network calls.
"""

import argparse
import os
import re
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EM, EN = "\u2014", "\u2013"
SENTENCE_END = re.compile(r"(?<=[.?!])[\"')\]]*\s+(?=[A-Z0-9\"'($\\\[])")
LATEX_SECTION = re.compile(r"\\(chapter|section|subsection|subsubsection)\*?\{([^}]*)\}")
LATEX_DISPLAY = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray)(\*?)\}.*?\\end\{\1\2\}|\\\[.*?\\\]", re.S)
LATEX_FLOAT = re.compile(r"\\begin\{(table|figure)(\*?)\}.*?\\end\{\1\2\}", re.S)
LATEX_DROP = re.compile(r"\\(?:cite\w*|ref|eqref|autoref|cref|Cref|label|pageref)\*?(?:\[[^\]]*\])*\{[^}]*\}")


def words_in(sentence):
    s = re.sub(r"\$[^$]*\$", " X ", sentence)
    s = LATEX_DROP.sub(" ", s)
    s = s.replace("~", " ").replace("**", "")
    return sum(1 for token in s.split() if re.search(r"\w", token))


def sentences_in(text):
    return [s.strip() for s in SENTENCE_END.split(text.replace("**", "")) if s.strip()]


# ---------------------------------------------------------------- reading each format


def blocks_markdown(text):
    """[(section path, [paragraph texts])]"""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    sections, path, paras = [], ["(start)"], []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or re.match(r"\[\^[^\]]+\]:", block) or block.startswith("|"):
            continue
        m = re.match(r"(#{1,6})\s+(.*)", block)
        if m and "\n" not in block:
            if paras or path != ["(start)"]:
                sections.append((path, paras))
            level = len(m.group(1))
            path = path[:max(level - 2, 0)] + [m.group(2).strip()] if level > 1 else [m.group(2).strip()]
            paras = []
            continue
        paras.append(" ".join(line.strip() for line in block.splitlines()))
    sections.append((path, paras))
    return [(p, ps) for p, ps in sections if ps]


def blocks_latex(text):
    text = re.sub(r"(?<!\\)%.*$", "", text, flags=re.M)
    text = LATEX_FLOAT.sub("\n\n", text)
    # A display equation that ends with a full stop also ends its sentence.
    text = LATEX_DISPLAY.sub(
        lambda m: " X. " if re.search(r"\.\s*(\\label\{[^}]*\}\s*)?(\\end\{\w+\*?\}|\\\])$", m.group(0)) else " X ",
        text)
    levels = {"chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}
    sections, path, paras = [], ["(start)"], []
    for block in re.split(r"\n\s*\n", text):
        block = " ".join(block.split())
        if not block:
            continue
        m = LATEX_SECTION.search(block)
        while m:
            before = block[:m.start()].strip()
            if before and not before.startswith("\\"):
                paras.append(before)
            if paras:
                sections.append((path, paras))
            depth = levels[m.group(1)]
            path = (path[:depth] if path != ["(start)"] else []) + [m.group(2)]
            paras = []
            block = block[m.end():]
            block = re.sub(r"^\s*\\label\{[^}]*\}", "", block).strip()
            m = LATEX_SECTION.search(block)
        if block and not re.fullmatch(r"(\\[A-Za-z]+(\{[^}]*\})*\s*)+", block):
            paras.append(block)
    sections.append((path, paras))
    return [(p, ps) for p, ps in sections if ps]


def blocks_docx(path):
    import docx_tool
    doc = docx_tool.Doc(path)
    sections, spath, paras = [], ["(start)"], []
    for i, p in enumerate(doc.paras):
        if doc.table_of[i] is not None:
            continue
        level = doc.level(i)
        text = docx_tool.para_text(p).strip()
        if level:
            if paras:
                sections.append((spath, paras))
            spath = (spath[:level - 1] if spath != ["(start)"] else []) + [text]
            paras = []
        elif level == 0 or not text:
            continue
        else:
            paras.append(text)
    sections.append((spath, paras))
    return [(p, ps) for p, ps in sections if ps]


def blocks_text(text):
    return [(["(text)"], [" ".join(b.split()) for b in re.split(r"\n\s*\n", text) if b.strip()])]


def load(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return "word", blocks_docx(path)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if ext == ".tex":
        return "latex", blocks_latex(text)
    if ext in (".md", ".markdown"):
        return "markdown", blocks_markdown(text)
    return "text", blocks_text(text)


# ---------------------------------------------------------------- counting


def stats(path, limit=25, banned=(), section=None):
    fmt, sections = load(path)
    banned = [b.strip() for b in banned if b.strip()]
    rows, longs, found, dashes, new_marks = [], [], [], [], []
    for spath, paras in sections:
        name = " > ".join(spath)
        if section and section.lower() not in name.lower():
            continue
        n_words = n_sent = n_long = 0
        for k, para in enumerate(paras, 1):
            where = "%s, paragraph %d" % (name, k)
            n_words += words_in(para)
            for s in sentences_in(para):
                n_sent += 1
                w = words_in(s)
                if w > limit:
                    n_long += 1
                    longs.append("%s: %d words: %s" % (where, w, " ".join(s.split()[:8]) + " ..."))
            for b in banned:
                hits = len(re.findall(r"(?<![\w-])%s(?![\w-])" % re.escape(b), para, re.I))
                if hits:
                    found.append('%s: "%s" (%d)' % (where, b, hits))
            kinds = []
            if EM in para:
                kinds.append("em dash (%d)" % para.count(EM))
            if EN in para:
                kinds.append("en dash (%d)" % para.count(EN))
            if fmt == "latex":
                prose = re.sub(r"\$[^$]*\$", " ", para)
                em_tex = len(re.findall(r"(?<!-)---(?!-)", prose))
                en_tex = len(re.findall(r"(?<!-)--(?!-)", prose))
                if em_tex:
                    kinds.append('em dash written "---" (%d)' % em_tex)
                if en_tex:
                    kinds.append('en dash written "--" (%d)' % en_tex)
            if kinds:
                dashes.append("%s: %s" % (where, ", ".join(kinds)))
            if "[NEW]" in para:
                new_marks.append("%s: %d" % (where, para.count("[NEW]")))
        rate = "%d%%" % round(100.0 * n_long / n_sent) if n_sent else "0%"
        rows.append((name, n_words, n_sent, n_long, rate))
    return fmt, rows, longs, found, dashes, new_marks


FIRST_PERSON = re.compile(r"\b(I|we|We|our|Our|us|my|My|me|ours|Ours)\b")
QUOTED = re.compile(r'"[^"]*"|\u201c[^\u201d]*\u201d|``.*?\'\'')
REFERENCE_WORDS = ("section", "chapter", "table", "figure", "equation", "page", "paragraph", "clause",
                   "step", "part", "appendix", "item", "phase", "stage", "version", "level", "day", "week")
SMALL_DIGIT = re.compile(r"(?<![\w.,$\u00a3\u20ac/:#-])([1-9])(?![\w.,%/:-])\s+([A-Za-z][\w-]*)")
BIG_WORD = re.compile(r"\b(ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
                      r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)(-\w+)?\s+([A-Za-z][\w-]*)",
                      re.I)


def prose_only(para, fmt):
    """The paragraph without math, citations, references and quotations."""
    text = re.sub(r"\$[^$]*\$", " ", para) if fmt == "latex" else para
    text = LATEX_DROP.sub(" ", text)
    return QUOTED.sub(" ", text)


def voice_and_numbers(path, section=None):
    """(first-person words, number-format cases), each as lines with their place."""
    fmt, sections = load(path)
    voice, numbers = [], []
    for spath, paras in sections:
        name = " > ".join(spath)
        if section and section.lower() not in name.lower():
            continue
        for k, para in enumerate(paras, 1):
            where = "%s, paragraph %d" % (name, k)
            text = prose_only(para, fmt)
            for m in FIRST_PERSON.finditer(text):
                after = text[m.end():].split()
                word = m.group(1) if m.group(1) == "I" else m.group(1).lower()
                voice.append((word, where, ("%s %s" % (m.group(1), after[0] if after else "")).strip()))
            for m in SMALL_DIGIT.finditer(text):
                before = text[:m.start()].split()[-1:] or [""]
                if before[0].lower().strip("~(") in REFERENCE_WORDS:
                    continue
                numbers.append('%s: digit under 10: "%s %s"' % (where, m.group(1), m.group(2)))
            for m in BIG_WORD.finditer(text):
                numbers.append('%s: word for 10 or more: "%s"' % (where, m.group(0)))
    return group_voice(voice), numbers


def group_voice(hits, shown=4):
    """One line per first-person word: its count, and its first places."""
    lines = []
    for word in sorted(set(h[0] for h in hits), key=lambda w: -sum(1 for h in hits if h[0] == w)):
        mine = [h for h in hits if h[0] == word]
        places = "; ".join('%s ("%s")' % (where, snippet) for _, where, snippet in mine[:shown])
        more = " and %d more" % (len(mine) - shown) if len(mine) > shown else ""
        lines.append("%s: %d, in %s%s" % (word, len(mine), places, more))
    return lines


def main(argv):
    parser = argparse.ArgumentParser(description="Count words, long sentences, banned words and dashes.")
    parser.add_argument("file")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--banned", default="", help="words and phrases to cut, separated by commas")
    parser.add_argument("--section")
    args = parser.parse_args(argv)
    try:
        fmt, rows, longs, found, dashes, new_marks = stats(
            args.file, args.limit, args.banned.split(","), args.section)
    except Exception as err:  # the message is more useful to the writer than a traceback
        print("error: %s" % err)
        return 2
    total = sum(r[1] for r in rows)
    print("file: %s (%s, %d sections, about %d words); sentence limit: %d words" % (
        args.file, fmt, len(rows), total, args.limit))
    print("section | words | sentences | over limit | rate")
    for name, w, s, n_long, rate in rows:
        print("%s | %d | %d | %d | %s" % (name, w, s, n_long, rate))
    voice, numbers = voice_and_numbers(args.file, args.section)
    for title, items in (("long sentences", longs), ("banned words", found),
                         ("dashes", dashes), ("[NEW] marks", new_marks),
                         ("first person, to check against the voice rule", voice),
                         ("numbers, to check against the number rule", numbers)):
        print("%s: %s" % (title, len(items) if items else "none"))
        for item in items:
            print("  " + item)
    return 0


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # stop quietly when output is cut short
    sys.exit(main(sys.argv[1:]))
