#!/usr/bin/env python3
"""List every symbol in the math of LaTeX or Markdown files, with its places.

  symbols.py FILE [FILE ...] [--symbol SYMBOL]

For each symbol it prints the number of uses, then:
  first    its first use in each file, with the line around it
  "="      each place where it stands left of "=": a definition or a value
  other    the lines of its other uses
A use inside a keep passage is marked [keep], and inside a keep light passage
[keep light]. --symbol shows one symbol only, such as --symbol "\\Lambda".
Standard library only. No network calls.
"""

import argparse
import os
import re
import signal
import sys
from collections import OrderedDict

GREEK = set("""alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda
    mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta
    Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega ell""".split())
DECOR = set("""hat bar tilde dot ddot vec check breve widehat widetilde overline mathbf boldsymbol
    bm mathcal mathbb mathsf mathfrak mathit""".split())
DROP = set("""text textrm textit textbf textsf mbox label tag operatorname mathrm ref eqref cite
    begin end hspace vspace mathop""".split())

LATEX_MATH = [
    re.compile(r"\\begin\{((?:equation|align|gather|multline|eqnarray|displaymath|math|flalign)\*?)\}"
               r"(.*?)\\end\{\1\}", re.S),
    re.compile(r"\\\[(.*?)\\\]", re.S),
    re.compile(r"\\\((.*?)\\\)", re.S),
    re.compile(r"\$\$(.*?)\$\$", re.S),
    re.compile(r"(?<!\\)\$((?:\\\$|[^$])+?)(?<!\\)\$", re.S),
]
MARKDOWN_MATH = [
    re.compile(r"\$\$(.*?)\$\$", re.S),
    re.compile(r"(?<![\\$\w])\$(?![\s\d$])([^$\n]+?)(?<![\s\\])\$(?![\d\w])"),
]
LATEX_LABEL = re.compile(r"\\label\{([^}]*)\}")
LATEX_KEEP = re.compile(r"^\s*%\s*(keep light|keep|end keep)\b")
MARKDOWN_KEEP = re.compile(r"^\s*<!--\s*(keep light|keep|end keep)\b")
DISPLAY_START = ("\\begin", "\\[", "$$")


def blank_comments(text):
    """LaTeX comments become spaces, so offsets and line numbers stay the same."""
    return re.sub(r"(?<!\\)%.*", lambda m: " " * len(m.group(0)), text)


def keep_lines(lines, fmt):
    """{line number: "keep" or "keep light"} for lines inside keep passages."""
    marker = LATEX_KEEP if fmt == "latex" else MARKDOWN_KEEP
    out, state = {}, None
    for n, line in enumerate(lines, 1):
        m = marker.match(line)
        if m:
            state = None if m.group(1) == "end keep" else m.group(1)
            continue
        if state:
            out[n] = state
    return out


def read_group(s, i):
    """The content of a {...} group that starts at s[i], and the index after it."""
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def read_argument(s, i):
    """One argument at s[i]: a {...} group, a command, or one character."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return "", i
    if s[i] == "{":
        return read_group(s, i)
    if s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        if m:
            return m.group(0), i + len(m.group(0))
        return s[i:i + 2], i + 2
    return s[i], i + 1


def tokens(math):
    """(symbol, offset) pairs in a piece of math."""
    out, i = [], 0
    while i < len(math):
        c = math[i]
        start = i
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", math[i:])
            if not m:
                i += 2
                continue
            name, i = m.group(1), i + len(m.group(0))
            if name in DROP:
                while i < len(math) and math[i] in " *":
                    i += 1
                if i < len(math) and math[i] == "{":
                    _, i = read_group(math, i)
                continue
            if name in DECOR:
                arg, i = read_argument(math, i)
                symbol = "\\%s{%s}" % (name, arg.strip())
            elif name in GREEK:
                symbol = "\\" + name
            else:
                continue
        elif c.isalpha():
            symbol, i = c, i + 1
        else:
            i += 1
            continue
        j = i
        while j < len(math) and math[j] == " ":
            j += 1
        if j < len(math) and math[j] == "_":
            sub, i = read_argument(math, j + 1)
            sub = sub.strip()
            symbol += "_" + (sub if len(sub) == 1 or sub.startswith("\\") and "{" not in sub else "{%s}" % sub)
        out.append((symbol, start))
    return out


def left_of_equals(math, offset, symbol):
    """True when the symbol opens a row of the math and "=" follows it."""
    before = math[:offset]
    row_start = max(before.rfind("\\\\"), before.rfind("&"), before.rfind(","), before.rfind("\n"))
    head = before[row_start + 1:] if row_start >= 0 else before
    if head.strip() not in ("", "&"):
        return False
    rest = math[offset + len(symbol):].lstrip()
    if rest.startswith("}"):
        rest = rest[1:].lstrip()
    return rest.startswith("=") or rest.startswith("&=") or rest.startswith("& =")


def scan(path):
    """Uses of every symbol in one file: (symbol, line, context, is_definition)."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    fmt = "latex" if path.lower().endswith(".tex") else "markdown"
    lines = raw.splitlines()
    keep = keep_lines(lines, fmt)
    text = blank_comments(raw) if fmt == "latex" else raw
    patterns = LATEX_MATH if fmt == "latex" else MARKDOWN_MATH
    uses = []
    for pattern in patterns:
        for m in pattern.finditer(text):
            math = m.group(m.lastindex)
            math_start = m.start(m.lastindex)
            display = m.group(0).startswith(DISPLAY_START)
            label = LATEX_LABEL.search(math)
            for symbol, offset in tokens(math):
                line = text.count("\n", 0, math_start + offset) + 1
                if display:
                    lead = m.start()
                    lead_line = text.count("\n", 0, lead)
                    before = next((lines[k].strip() for k in range(lead_line - 1, -1, -1) if lines[k].strip()), "")
                    body = " ".join(LATEX_LABEL.sub("", math).split())
                    context = "[%s]%s after: %s" % (body, " (%s)" % label.group(1) if label else "", before)
                else:
                    context = lines[line - 1].strip()
                uses.append((symbol, line, context, left_of_equals(math, offset, symbol), keep.get(line)))
            # blank the match, so that a later pattern does not find the same math
            text = text[:m.start()] + re.sub(r"[^\n]", " ", m.group(0)) + text[m.end():]
    uses.sort(key=lambda u: u[1])
    return uses


def short(context, limit=160):
    return context if len(context) <= limit else context[:limit - 3] + "..."


def report(paths, only=None):
    table = OrderedDict()
    for path in paths:
        for symbol, line, context, is_def, keep in scan(path):
            if only and symbol != only:
                continue
            table.setdefault(symbol, []).append((path, line, context, is_def, keep))
    out = ["symbols.py: %d file(s), %d symbol(s)" % (len(paths), len(table))]
    for symbol, uses in table.items():
        out.append("%s: %d use(s)" % (symbol, len(uses)))
        shown = set()
        for path in paths:
            mine = [u for u in uses if u[0] == path]
            if not mine:
                continue
            first = mine[0]
            out.append("  first  %s:%d%s: %s" % (os.path.basename(path), first[1], mark(first[4]), short(first[2])))
            shown.add((path, first[1]))
        for path, line, context, is_def, keep in uses:
            if is_def and (path, line) not in shown:
                out.append("  =      %s:%d%s: %s" % (os.path.basename(path), line, mark(keep), short(context)))
                shown.add((path, line))
        others = OrderedDict()
        for path, line, context, is_def, keep in uses:
            if (path, line) not in shown:
                others.setdefault(os.path.basename(path), []).append("%d%s" % (line, mark(keep)))
        if others:
            out.append("  other  " + "; ".join("%s: %s" % (name, ", ".join(OrderedDict.fromkeys(nums)))
                                              for name, nums in others.items()))
    return "\n".join(out)


def mark(keep):
    return " [%s]" % keep if keep else ""


def main(argv):
    parser = argparse.ArgumentParser(description="List every symbol in the math of LaTeX or Markdown files.")
    parser.add_argument("files", nargs="+")
    parser.add_argument("--symbol")
    args = parser.parse_args(argv)
    try:
        print(report(args.files, args.symbol))
    except OSError as err:
        print("error: %s" % err)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # stop quietly when output is cut short
    sys.exit(main(sys.argv[1:]))
