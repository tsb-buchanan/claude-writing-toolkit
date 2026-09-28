#!/usr/bin/env python3
"""Show the changes between two text files, word by word.

  word_diff.py OLD NEW

Each changed stretch starts with a line like "@@ new lines 62 to 64". Removed
words show as [-like this-], added words as {+like this+}. Unchanged lines are
left out. It works where git is not installed, such as on claude.ai.
Standard library only. No network calls.
"""

import difflib
import re
import signal
import sys

TOKEN = re.compile(r"\S+|\n")


def words(lines):
    return TOKEN.findall("".join(lines))


def join(tokens):
    out = ""
    for t in tokens:
        if t == "\n":
            out = out.rstrip(" ") + "\n"
        else:
            out += t + " "
    return out.rstrip(" ")


def mark(old, new):
    """The new stretch with removed and added words marked."""
    out = []
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    if old and new and matcher.ratio() < 0.5:
        # too different to read word by word: show the old text, then the new
        return join(["[-%s-]" % " ".join(t for t in old if t != "\n"), "\n", "{+%s+}" % join(new).strip("\n")])
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            out.extend(new[j1:j2])
            continue
        gone = [t for t in old[i1:i2] if t != "\n"]
        came = new[j1:j2]
        if gone:
            out.append("[-%s-]" % " ".join(gone))
        if [t for t in came if t != "\n"]:
            text = join(came).strip("\n")
            out.append("{+%s+}" % text)
            if came and came[-1] == "\n":
                out.append("\n")
        else:
            out.extend(t for t in came if t == "\n")
    return join(out)


def diff(old_text, new_text, context=0):
    a = old_text.splitlines(keepends=True)
    b = new_text.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    blocks = []
    for group in matcher.get_grouped_opcodes(context):
        i1, j1 = group[0][1], group[0][3]
        i2, j2 = group[-1][2], group[-1][4]
        if j2 > j1:
            head = "@@ new lines %d to %d" % (j1 + 1, j2) if j2 - j1 > 1 else "@@ new line %d" % (j1 + 1)
        else:
            head = "@@ removed after new line %d" % j1
        body = mark(words(a[i1:i2]), words(b[j1:j2])).strip("\n")
        blocks.append(head + "\n" + body)
    return "\n\n".join(blocks) if blocks else "no changes"


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            old = f.read()
        with open(argv[1], encoding="utf-8") as f:
            new = f.read()
    except OSError as err:
        print("error: %s" % err)
        return 2
    print(diff(old, new))
    return 0


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # stop quietly when output is cut short
    sys.exit(main(sys.argv[1:]))
