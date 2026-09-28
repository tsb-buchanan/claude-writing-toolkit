#!/usr/bin/env python3
"""Read a Word file, and write changes into a copy as tracked changes.

Standard library only. No network calls.

Commands:
  outline FILE                 One short line per paragraph, with its number.
  read FILE [--section NAME]   Paragraphs in full, numbered, with flags and comments.
       [--paras A-B]           Only paragraphs A to B.
  apply FILE CHANGES OUT       Write the changes in the JSON file CHANGES into the copy OUT,
                               as tracked changes. The original stays as it is.
  from-text TEXT OUT           Build a plain Word file from a text file, so changes can be
                               tracked against it. "# ", "## " and "### " start headings.

apply and from-text never overwrite a file, unless you add --replace.

CHANGES looks like this. Paragraph numbers come from outline or read.
  {"author": "Claude", "changes": [
    {"op": "replace", "para": 6, "expect": "first words", "text": "the whole new paragraph"},
    {"op": "delete", "para": 9, "expect": "first words"},
    {"op": "insert_after", "para": 3, "text": "a new paragraph", "style": "Heading2"},
    {"op": "move", "paras": [12, 14], "after": 4, "expect": "first words of 12"}]}

"expect" is optional: a change is skipped unless its paragraph starts with those words.
"style" is optional; it must be a paragraph style in the file. "after": 0 means before p1.
The tool refuses paragraphs it cannot change safely, and says why: table cells, keep
passages, and paragraphs with equations, fields, footnotes, links, images or tracked changes.
"""

import argparse
import datetime
import difflib
import json
import os
import re
import signal
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import check_protected
except ImportError:
    check_protected = None

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W = "{" + W_NS + "}"
DOC_PART = "word/document.xml"
COMMENTS_PART = "word/comments.xml"
STYLES_PART = "word/styles.xml"

ATTRS = r"""(?:\s+[^\s=/>]+\s*=\s*(?:"[^"]*"|'[^']*'))*\s*"""
P_TOKEN = re.compile(r"<w:p" + ATTRS + r"(/?)>|</w:p>")
TBL_TOKEN = re.compile(r"<w:tbl" + ATTRS + r">|</w:tbl>")
P_START = re.compile(r"<w:p" + ATTRS + r">")
PPR_RAW = re.compile(r"<w:pPr" + ATTRS + r"/>|<w:pPr" + ATTRS + r">.*?</w:pPr>", re.S)
RPR_RAW = re.compile(r"<w:rPr" + ATTRS + r"/>|<w:rPr" + ATTRS + r">.*?</w:rPr>", re.S)
RUN_RAW = re.compile(r"<w:r" + ATTRS + r">.*?</w:r>|<w:r" + ATTRS + r"/>", re.S)
CHILD_RAW = re.compile(r"<w:r" + ATTRS + r">.*?</w:r>|<w:[A-Za-z]+" + ATTRS + r"/>", re.S)
TOKEN = re.compile(r"\s+|\w+(?:['\u2019]\w+)*|[^\w\s]")
BAD_XML_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

RUN_TEXT = {"rPr", "t", "tab", "br", "cr", "lastRenderedPageBreak", "softHyphen", "noBreakHyphen"}
MARKERS = {"commentRangeStart", "commentRangeEnd", "bookmarkStart", "bookmarkEnd", "proofErr"}


class ToolError(Exception):
    pass


def local(tag):
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def norm(text):
    return " ".join(text.split()).lower()


def clean(text):
    return BAD_XML_CHARS.sub("", text)


# ---------------------------------------------------------------- reading


def root_namespaces(xml):
    m = re.search(r"<w:document\b([^>]*)>", xml)
    if not m:
        raise ToolError("no <w:document> root: the file does not use the usual w: prefix")
    decls = dict(re.findall(r'xmlns:([A-Za-z0-9_.-]+)\s*=\s*"([^"]*)"', m.group(1)))
    if decls.get("w") != W_NS:
        raise ToolError("the w: prefix is not the Word main namespace")
    return decls


def parse_fragment(frag, decls):
    attrs = " ".join('xmlns:%s="%s"' % (k, v) for k, v in decls.items())
    return ET.fromstring("<wrap %s>%s</wrap>" % (attrs, frag))[0]


def paragraph_spans(xml):
    """(start, end) of every w:p that is not inside another w:p, in document order."""
    spans, depth, start = [], 0, None
    for m in P_TOKEN.finditer(xml):
        if m.group(0) == "</w:p>":
            depth -= 1
            if depth == 0:
                spans.append((start, m.end()))
        elif m.group(1) == "/":
            if depth == 0:
                spans.append((m.start(), m.end()))
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    if depth != 0:
        raise ToolError("unbalanced paragraphs in word/document.xml")
    return spans


def table_spans(xml):
    spans, stack = [], []
    for m in TBL_TOKEN.finditer(xml):
        if m.group(0) == "</w:tbl>":
            if stack:
                start = stack.pop()
                if not stack:
                    spans.append((start, m.end()))
        else:
            stack.append(m.start())
    return spans


def para_text(p, view="accepted"):
    """Text of one paragraph. "original" rejects all tracked changes, "accepted" accepts them."""
    parts = []

    def walk(el, ins, dele):
        tag = el.tag
        if tag in (W + "pPr", W + "rPr", W + "instrText", W + "delInstrText", W + "txbxContent"):
            return
        if tag == W + "p" and el is not p:
            return
        if tag in (W + "ins", W + "moveTo"):
            ins = True
        elif tag in (W + "del", W + "moveFrom"):
            dele = True
        hidden = (view == "original" and ins) or (view == "accepted" and dele)
        if not hidden:
            if tag in (W + "t", W + "delText"):
                parts.append(el.text or "")
            elif tag == W + "tab":
                parts.append("\t")
            elif tag in (W + "br", W + "cr"):
                parts.append("\n")
            elif tag == W + "noBreakHyphen":
                parts.append("-")
        for child in el:
            walk(child, ins, dele)

    walk(p, False, False)
    return "".join(parts)


def mark_state(p):
    """(inserted, deleted) for the paragraph mark."""
    ppr = p.find(W + "pPr")
    rpr = ppr.find(W + "rPr") if ppr is not None else None
    if rpr is None:
        return False, False
    return rpr.find(W + "ins") is not None, rpr.find(W + "del") is not None


def view_texts(paras, view):
    """Paragraph texts as Word shows them after rejecting ("original") or accepting all changes."""
    out, carry = [], ""
    for p in paras:
        inserted, deleted = mark_state(p)
        text = carry + para_text(p, view)
        carry = ""
        if (view == "original" and inserted) or (view == "accepted" and deleted):
            carry = text
            continue
        out.append(text)
    if carry:
        out.append(carry)
    return out


def para_flags(p):
    flags = set()
    for el in p.iter():
        tag = el.tag
        if tag.startswith("{" + M_NS + "}oMath"):
            flags.add("equation")
        elif tag in (W + "fldSimple", W + "fldChar", W + "instrText"):
            flags.add("field")
        elif tag in (W + "footnoteReference", W + "endnoteReference"):
            flags.add("footnote")
        elif tag in (W + "commentRangeStart", W + "commentReference"):
            flags.add("comment")
        elif tag in (W + "ins", W + "del", W + "moveFrom", W + "moveTo", W + "pPrChange", W + "rPrChange"):
            flags.add("tracked")
        elif tag in (W + "drawing", W + "pict", W + "object"):
            flags.add("image")
        elif tag == W + "hyperlink":
            flags.add("link")
        elif tag == W + "txbxContent":
            flags.add("text box")
    formats = set()
    for r in p.findall(W + "r"):
        if r.find(W + "t") is not None:
            rpr = r.find(W + "rPr")
            formats.add(ET.tostring(rpr) if rpr is not None else b"")
    if len(formats) > 1:
        flags.add("mixed formatting")
    return flags


def para_style(p):
    ppr = p.find(W + "pPr")
    ps = ppr.find(W + "pStyle") if ppr is not None else None
    return ps.get(W + "val") if ps is not None else None


class Doc:
    def __init__(self, path):
        self.path = path
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                if DOC_PART not in names:
                    raise ToolError("not a Word file: word/document.xml is missing")
                self.xml = z.read(DOC_PART).decode("utf-8")
                self.comments_xml = z.read(COMMENTS_PART).decode("utf-8") if COMMENTS_PART in names else None
                self.styles_xml = z.read(STYLES_PART).decode("utf-8") if STYLES_PART in names else None
        except zipfile.BadZipFile:
            raise ToolError("not a Word file: it is not a zip package")
        self.decls = root_namespaces(self.xml)
        self.spans = paragraph_spans(self.xml)
        self.paras = [parse_fragment(self.xml[s:e], self.decls) for s, e in self.spans]
        self.tables = table_spans(self.xml)
        self.table_of = [self._table_index(i) for i in range(len(self.paras))]
        self.style_levels, self.style_ids = self._styles()
        self.comments = self._comments()
        self.comment_paras = self._comment_paras()
        self.keep = self._keep_marks()

    def _table_index(self, i):
        s, e = self.spans[i]
        for n, (ts, te) in enumerate(self.tables):
            if ts <= s and e <= te:
                return n
        return None

    def _styles(self):
        """Outline level per paragraph style id (0 for Title), and the set of style ids."""
        if not self.styles_xml:
            return {}, set()
        root = ET.fromstring(self.styles_xml.encode("utf-8"))
        info, ids = {}, set()
        for st in root.findall(W + "style"):
            if st.get(W + "type") != "paragraph":
                continue
            sid = st.get(W + "styleId")
            ids.add(sid)
            name_el, based_el = st.find(W + "name"), st.find(W + "basedOn")
            name = (name_el.get(W + "val") if name_el is not None else "") or ""
            lvl_el = st.find(W + "pPr/" + W + "outlineLvl")
            level = None
            if lvl_el is not None and lvl_el.get(W + "val", "").isdigit() and int(lvl_el.get(W + "val")) < 9:
                level = int(lvl_el.get(W + "val")) + 1
            m = re.fullmatch(r"heading\s?(\d)", name.strip().lower()) or re.fullmatch(r"[Hh]eading(\d)", sid or "")
            if level is None and m:
                level = int(m.group(1))
            if level is None and name.strip().lower() == "title":
                level = 0
            info[sid] = (level, based_el.get(W + "val") if based_el is not None else None)
        levels = {}
        for sid in info:
            seen, cur = set(), sid
            while cur in info and cur not in seen:
                seen.add(cur)
                if info[cur][0] is not None:
                    levels[sid] = info[cur][0]
                    break
                cur = info[cur][1]
        return levels, ids

    def level(self, i):
        """Heading level of paragraph i (0 for a title), or None for body text."""
        if self.table_of[i] is not None:
            return None
        p = self.paras[i]
        lvl = p.find(W + "pPr/" + W + "outlineLvl")
        if lvl is not None and lvl.get(W + "val", "").isdigit() and int(lvl.get(W + "val")) < 9:
            return int(lvl.get(W + "val")) + 1
        style = para_style(p)
        if style in self.style_levels:
            return self.style_levels[style]
        m = re.fullmatch(r"[Hh]eading\s?(\d)", style or "")
        if m:
            return int(m.group(1))
        return 0 if style == "Title" else None

    def label(self, i):
        if self.table_of[i] is not None:
            return "table"
        level = self.level(i)
        if level == 0:
            return "Title"
        if level:
            return "H%d" % level
        style = para_style(self.paras[i])
        return style if style and style not in ("Normal", "BodyText", "Standard") else "body"

    def _comments(self):
        if not self.comments_xml:
            return {}
        root = ET.fromstring(self.comments_xml.encode("utf-8"))
        out = {}
        for c in root.findall(W + "comment"):
            text = " ".join(para_text(p) for p in c.findall(W + "p")).strip()
            out[c.get(W + "id")] = (c.get(W + "author") or "", text)
        return out

    def _comment_paras(self):
        """comment id -> (first paragraph, last paragraph), 0-based."""
        starts, ends = {}, {}
        for i, p in enumerate(self.paras):
            for el in p.iter(W + "commentRangeStart"):
                starts.setdefault(el.get(W + "id"), i)
            for el in p.iter(W + "commentRangeEnd"):
                ends[el.get(W + "id")] = i
            for el in p.iter(W + "commentReference"):
                starts.setdefault(el.get(W + "id"), i)
                ends.setdefault(el.get(W + "id"), i)
        return {cid: (starts[cid], ends.get(cid, starts[cid])) for cid in starts}

    def _keep_marks(self):
        """paragraph index -> "keep" or "keep light", from comments that start with those words."""
        keep = {}
        for cid, (author, text) in self.comments.items():
            m = re.match(r"\s*keep(\s+light)?\b", text, re.I)
            if not m or cid not in self.comment_paras:
                continue
            first, last = self.comment_paras[cid]
            for i in range(first, last + 1):
                if keep.get(i) != "keep":
                    keep[i] = "keep light" if m.group(1) else "keep"
        return keep

    def headings(self):
        return [(i, self.level(i)) for i in range(len(self.paras)) if self.level(i)]

    def section(self, name):
        """(first, last) paragraph indexes of the section whose heading matches name."""
        heads = self.headings()
        target = norm(name)
        match = None
        for rule in (lambda t: t == target, lambda t: t.startswith(target), lambda t: target in t):
            match = next((h for h in heads if rule(norm(para_text(self.paras[h[0]])))), None)
            if match:
                break
        if match is None and re.fullmatch(r"\d+(\.\d+)*", name.strip()):
            path = [int(x) for x in name.strip().split(".")]
            counters = [0] * 9
            for i, level in heads:
                counters[level - 1] += 1
                for k in range(level, 9):
                    counters[k] = 0
                if level == len(path) and counters[:level] == path:
                    match = (i, level)
                    break
        if match is None:
            raise ToolError("no heading matches %r. Run outline to see the headings." % name)
        first, level = match
        last = len(self.paras) - 1
        for i, lvl in heads:
            if i > first and lvl <= level:
                last = i - 1
                break
        return first, last


def short(text, words=8):
    parts = text.split()
    return " ".join(parts[:words]) + (" ..." if len(parts) > words else "")


def describe_comments(doc, first, last):
    lines = []
    for cid, (a, b) in sorted(doc.comment_paras.items(), key=lambda x: x[1]):
        if b < first or a > last or cid not in doc.comments:
            continue
        author, text = doc.comments[cid]
        where = "p%d" % (a + 1) if a == b else "p%d-p%d" % (a + 1, b + 1)
        kind = "keep mark" if re.match(r"\s*keep\b", text, re.I) else "note"
        lines.append("  %s on %s by %s: %s" % (kind, where, author, text))
    return lines


def cmd_outline(path):
    doc = Doc(path)
    print("file: %s (%d paragraphs, %d comments)" % (path, len(doc.paras), len(doc.comments)))
    i = 0
    while i < len(doc.paras):
        t = doc.table_of[i]
        if t is not None:
            j = i
            while j + 1 < len(doc.paras) and doc.table_of[j + 1] == t:
                j += 1
            print("p%d-p%d [table: %d cells]" % (i + 1, j + 1, j - i + 1))
            i = j + 1
            continue
        label, text = doc.label(i), para_text(doc.paras[i]).replace("\n", " ")
        extra = " {%s}" % doc.keep[i] if i in doc.keep else ""
        print("p%d [%s] %s%s" % (i + 1, label, text if label.startswith(("H", "Title")) else short(text), extra))
        i += 1
    comments = describe_comments(doc, 0, len(doc.paras) - 1)
    if comments:
        print("comments:")
        print("\n".join(comments))


def print_para(doc, i):
    text = para_text(doc.paras[i]).replace("\t", " ").replace("\n", " / ")
    flags = sorted(para_flags(doc.paras[i]))
    if i in doc.keep:
        flags.append(doc.keep[i])
    extra = "  {%s}" % ", ".join(flags) if flags else ""
    print("p%d [%s] %s%s" % (i + 1, doc.label(i), text, extra))


def cmd_read(path, section=None, paras=None):
    doc = Doc(path)
    if section:
        first, last = doc.section(section)
    elif paras:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", paras)
        if not m:
            raise ToolError("--paras takes a number or a range such as 12-18")
        first, last = int(m.group(1)) - 1, int(m.group(2) or m.group(1)) - 1
        if not 0 <= first <= last < len(doc.paras):
            raise ToolError("the file has paragraphs 1 to %d" % len(doc.paras))
    else:
        first, last = 0, len(doc.paras) - 1
    print("file: %s, paragraphs %d to %d of %d" % (path, first + 1, last + 1, len(doc.paras)))
    if first > 0:
        print("before:")
        print_para(doc, first - 1)
    print("selection:")
    for i in range(first, last + 1):
        print_para(doc, i)
    if last < len(doc.paras) - 1:
        print("after:")
        print_para(doc, last + 1)
    comments = describe_comments(doc, first, last)
    if comments:
        print("comments:")
        print("\n".join(comments))


# ---------------------------------------------------------------- writing


class Revisions:
    def __init__(self, xml, author):
        ids = [int(x) for x in re.findall(r'\bw:id="(-?\d+)"', xml)]
        self.next_id = max(ids + [0]) + 1
        self.author = author
        self.date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def attrs(self):
        n = self.next_id
        self.next_id += 1
        return 'w:id="%d" w:author=%s w:date="%s"' % (n, quoteattr(self.author), self.date)

    def wrap(self, kind, content):
        if not content:
            return ""
        return "<w:%s %s>%s</w:%s>" % (kind, self.attrs(), content, kind)


def make_run(rpr, text, deleted):
    tag = "w:delText" if deleted else "w:t"
    body, buf = [], []
    for ch in text:
        if ch in "\t\n":
            if buf:
                body.append('<%s xml:space="preserve">%s</%s>' % (tag, escape("".join(buf)), tag))
                buf = []
            body.append("<w:tab/>" if ch == "\t" else "<w:br/>")
        else:
            buf.append(ch)
    if buf:
        body.append('<%s xml:space="preserve">%s</%s>' % (tag, escape("".join(buf)), tag))
    return "<w:r>%s%s</w:r>" % (rpr, "".join(body)) if body else ""


def run_pieces(run_el):
    parts = []
    for sub in run_el:
        name = local(sub.tag)
        if name == "t":
            parts.append(sub.text or "")
        elif name == "tab":
            parts.append("\t")
        elif name in ("br", "cr"):
            parts.append("\n")
        elif name == "noBreakHyphen":
            parts.append("-")
    return "".join(parts)


def split_paragraph(frag):
    """Start tag, raw pPr and the raw content after it."""
    if frag.endswith("/>"):
        return frag[:-2].rstrip() + ">", "", ""
    m = P_START.match(frag)
    if not m:
        raise ToolError("could not read a paragraph start tag")
    inner = frag[m.end():-len("</w:p>")]
    ppr = PPR_RAW.match(inner.lstrip())
    if ppr:
        lead = len(inner) - len(inner.lstrip())
        return m.group(0), ppr.group(0), inner[lead + ppr.end():]
    return m.group(0), "", inner


def child_kind(raw, decls):
    """Classify one child of a paragraph: text, reference (a comment reference run), marker, or bad."""
    if raw.startswith("<w:r") and RUN_RAW.fullmatch(raw):
        el = parse_fragment(raw, decls)
        names = [local(sub.tag) for sub in el]
        if "commentReference" in names and all(n in ("rPr", "commentReference") for n in names):
            return "reference", None
        for sub in el:
            n = local(sub.tag)
            if n not in RUN_TEXT:
                return "bad", "a run holds w:%s" % n
            if n == "br" and sub.get(W + "type") not in (None, "textWrapping"):
                return "bad", "it holds a page or column break"
            if n == "rPr" and sub.find(W + "rPrChange") is not None:
                return "bad", "it holds a tracked format change"
        return "text", el
    m = re.match(r"<w:([A-Za-z]+)", raw)
    name = m.group(1) if m else "?"
    if name in MARKERS:
        if name == "bookmarkStart" and 'w:name="_GoBack"' not in raw:
            return "bad", "it holds a bookmark"
        return "marker", name
    return "bad", "it holds w:%s" % name


def paragraph_parts(frag, p, decls, for_delete=False):
    """Split a paragraph into start tag, pPr, and classified children. Raise ToolError when unsafe."""
    for sub in p.iter():
        name = local(sub.tag)
        if sub.tag.startswith("{" + M_NS + "}"):
            raise ToolError("it holds an equation")
        if name in ("footnoteReference", "endnoteReference"):
            raise ToolError("it holds a footnote")
        if name in ("fldSimple", "fldChar", "instrText"):
            raise ToolError("it holds a field")
        if name in ("drawing", "pict", "object", "txbxContent"):
            raise ToolError("it holds an image or a text box")
        if name in ("ins", "del", "moveFrom", "moveTo", "pPrChange"):
            raise ToolError("it already holds tracked changes")
        if name == "sectPr":
            raise ToolError("it ends a section of the document")
        if name == "hyperlink":
            raise ToolError("it holds a link")
        if name in ("sdt", "smartTag", "customXml"):
            raise ToolError("it holds a content control")
    start, ppr, rest = split_paragraph(frag)
    tokens = CHILD_RAW.findall(rest)
    if re.sub(r"\s", "", "".join(tokens)) != re.sub(r"\s", "", rest):
        raise ToolError("it holds content that the tool cannot read safely")
    children = []
    goback = set(re.findall(r'<w:bookmarkStart[^>]*?w:id="([^"]*)"[^>]*?w:name="_GoBack"', rest) +
                 re.findall(r'<w:bookmarkStart[^>]*?w:name="_GoBack"[^>]*?w:id="([^"]*)"', rest))
    for raw in tokens:
        kind, info = child_kind(raw, decls)
        if kind == "bad":
            raise ToolError(info)
        if info == "bookmarkEnd":
            m = re.search(r'w:id="([^"]*)"', raw)
            if not m or m.group(1) not in goback:
                raise ToolError("it holds the end of a bookmark")
        children.append((kind, raw, info))
    return start, ppr, children


def build_replace(frag, p, new_text, revs, decls):
    start, ppr, children = paragraph_parts(frag, p, decls)
    text_pos = [n for n, c in enumerate(children) if c[0] == "text"]
    first_text = text_pos[0] if text_pos else len(children)
    last_text = text_pos[-1] if text_pos else -1
    for n, (kind, raw, info) in enumerate(children):
        if first_text < n < last_text and (kind == "reference" or info in ("commentRangeStart", "commentRangeEnd")):
            raise ToolError("a comment starts or ends inside its text")
    lead = "".join(raw for n, (kind, raw, info) in enumerate(children)
                   if n < first_text and info not in ("proofErr", "bookmarkStart", "bookmarkEnd"))
    tail = "".join(raw for n, (kind, raw, info) in enumerate(children)
                   if n > last_text and info not in ("proofErr", "bookmarkStart", "bookmarkEnd"))

    rprs, chars = [], []
    for n in text_pos:
        raw, el = children[n][1], children[n][2]
        m = RPR_RAW.search(raw)
        rprs.append(m.group(0) if m else "")
        for ch in run_pieces(el):
            chars.append((ch, len(rprs) - 1))
    old_text = "".join(c for c, _ in chars)
    new_text = clean(new_text)
    if new_text == old_text:
        raise ToolError("the new text is the same as the old text")

    weight = {}
    for _, idx in chars:
        weight[rprs[idx]] = weight.get(rprs[idx], 0) + 1
    base = max(weight, key=weight.get) if weight else (rprs[0] if rprs else "")

    old_tokens, new_tokens = TOKEN.findall(old_text), TOKEN.findall(new_text)
    starts = [0]
    for tok in old_tokens:
        starts.append(starts[-1] + len(tok))

    def old_runs(a, b, deleted):
        out, i = [], a
        while i < b:
            idx, j = chars[i][1], i
            while j < b and chars[j][1] == idx:
                j += 1
            out.append(make_run(rprs[idx], "".join(c for c, _ in chars[i:j]), deleted))
            i = j
        return "".join(out)

    body, removed, added = [], 0, 0
    matcher = difflib.SequenceMatcher(None, old_tokens, new_tokens, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        a, b = starts[i1], starts[i2]
        if tag == "equal":
            body.append(old_runs(a, b, False))
        if tag in ("delete", "replace"):
            body.append(revs.wrap("del", old_runs(a, b, True)))
            removed += sum(1 for t in old_tokens[i1:i2] if re.match(r"\w", t))
        if tag in ("insert", "replace"):
            body.append(revs.wrap("ins", make_run(base, "".join(new_tokens[j1:j2]), False)))
            added += sum(1 for t in new_tokens[j1:j2] if re.match(r"\w", t))
    note = "%d words deleted, %d words inserted" % (removed, added)
    return start + ppr + lead + "".join(body) + tail + "</w:p>", old_text, note


def mark_paragraph(ppr, kind, revs):
    mark = "<w:%s %s/>" % (kind, revs.attrs())
    if not ppr or ppr.endswith("/>"):
        return "<w:pPr><w:rPr>%s</w:rPr></w:pPr>" % mark
    m = re.search(r"<w:rPr" + ATTRS + r">", ppr)
    if m:
        return ppr[:m.end()] + mark + ppr[m.end():]
    m = re.search(r"<w:rPr" + ATTRS + r"/>", ppr)
    if m:
        return ppr[:m.start()] + "<w:rPr>%s</w:rPr>" % mark + ppr[m.end():]
    return ppr[:-len("</w:pPr>")] + "<w:rPr>%s</w:rPr></w:pPr>" % mark


def build_delete(frag, p, revs, decls):
    start, ppr, children = paragraph_parts(frag, p, decls, for_delete=True)
    out, pending = [], []

    def flush():
        if pending:
            out.append(revs.wrap("del", "".join(pending)))
            pending.clear()

    for kind, raw, info in children:
        if kind == "text":
            m = RPR_RAW.search(raw)
            run = make_run(m.group(0) if m else "", run_pieces(info), True)
            if run:
                pending.append(run)
        else:
            flush()
            out.append(raw)
    flush()
    return start + mark_paragraph(ppr, "del", revs) + "".join(out) + "</w:p>"


def build_inserted_copy(frag, p, revs, decls):
    """A tracked insertion that repeats paragraph p, for a move."""
    start, ppr, children = paragraph_parts(frag, p, decls, for_delete=True)
    runs = []
    for kind, raw, info in children:
        if kind == "text":
            m = RPR_RAW.search(raw)
            runs.append(make_run(m.group(0) if m else "", run_pieces(info), False))
    return "<w:p>" + mark_paragraph(ppr, "ins", revs) + revs.wrap("ins", "".join(runs)) + "</w:p>"


def build_insert(text, style, revs, style_ids):
    if style and (not re.fullmatch(r"[A-Za-z0-9_-]+", style) or (style_ids and style not in style_ids)):
        heads = sorted(s for s in style_ids if re.match(r"[Hh]eading", s))
        raise ToolError("the file has no paragraph style %r. Heading styles here: %s"
                        % (style, ", ".join(heads) or "none"))
    pstyle = '<w:pStyle w:val="%s"/>' % style if style else ""
    mark = "<w:ins %s/>" % revs.attrs()
    body = revs.wrap("ins", make_run("", clean(text), False))
    return "<w:p><w:pPr>%s<w:rPr>%s</w:rPr></w:pPr>%s</w:p>" % (pstyle, mark, body)


def guard(doc, i):
    """Raise ToolError when paragraph i may not be changed."""
    if doc.table_of[i] is not None:
        raise ToolError("it is a table cell; tables stay as they are")
    if doc.keep.get(i) == "keep":
        raise ToolError("it is marked keep")


def insert_point(doc, after):
    """Where new paragraphs go "after" paragraph number after (0: at the start).
    Returns (position in document.xml, index of the paragraph they follow). After any
    table cell, they go after the whole table."""
    if after == 0:
        t = doc.table_of[0]
        return (doc.tables[t][0] if t is not None else doc.spans[0][0]), -1
    i = after - 1
    t = doc.table_of[i]
    if t is None:
        return doc.spans[i][1], i
    last = max(j for j in range(len(doc.paras)) if doc.table_of[j] == t)
    return doc.tables[t][1], last


def cmd_apply(path, json_path, out_path):
    with open(json_path, encoding="utf-8") as f:
        spec = json.load(f)
    doc = Doc(path)
    revs = Revisions(doc.xml, spec.get("author") or "Claude")
    count = len(doc.paras)
    old_texts = [para_text(p) for p in doc.paras]
    has_tracked = any("tracked" in para_flags(p) for p in doc.paras)

    edits, done, skipped, notes, used = [], [], [], [], set()
    replaced, deleted, inserted = {}, set(), {}
    protected = []
    for n, ch in enumerate(spec.get("changes", []), 1):
        op = ch.get("op")
        try:
            if op == "move":
                a, b = (ch.get("paras") or [None, None])[:2]
                after = ch.get("after")
                if not all(isinstance(x, int) for x in (a, b, after)) or not (1 <= a <= b <= count and 0 <= after <= count):
                    raise ToolError("move needs \"paras\": [first, last] and \"after\" within 0 to %d" % count)
                if a - 1 <= after <= b:
                    raise ToolError("a block cannot move next to itself")
                targets = list(range(a - 1, b))
            else:
                para = ch.get("para")
                if not isinstance(para, int) or not (0 <= para <= count) or (op != "insert_after" and para == 0):
                    raise ToolError("no paragraph %s" % para)
                targets = [para - 1] if op != "insert_after" else []
            first = targets[0] if targets else None
            if "expect" in ch and first is not None and not norm(old_texts[first]).startswith(norm(ch["expect"])):
                raise ToolError("p%d does not start with %r" % (first + 1, ch["expect"]))
            for i in targets:
                if i in used:
                    raise ToolError("p%d already has a change" % (i + 1))
                guard(doc, i)
            if op == "replace":
                i = targets[0]
                s, e = doc.spans[i]
                new, before, note = build_replace(doc.xml[s:e], doc.paras[i], ch.get("text", ""), revs, doc.decls)
                edits.append((s, e, len(edits), new))
                replaced[i] = clean(ch.get("text", ""))
                if check_protected is not None:
                    report = check_protected.compare(before, replaced[i], "text")
                    if check_protected.changed(report) or report["numbers"]["format_changes"]:
                        protected.append("p%d:\n%s" % (i + 1, "\n".join(
                            "  " + line for line in check_protected.format_report(report).splitlines()
                            if "unchanged" not in line or "format" in line)))
            elif op == "delete":
                i = targets[0]
                s, e = doc.spans[i]
                edits.append((s, e, len(edits), build_delete(doc.xml[s:e], doc.paras[i], revs, doc.decls)))
                deleted.add(i)
                note = "1 paragraph deleted"
            elif op == "insert_after":
                pos, follows = insert_point(doc, ch.get("para"))
                edits.append((pos, pos, len(edits), build_insert(ch.get("text", ""), ch.get("style"), revs, doc.style_ids)))
                inserted.setdefault(follows, []).append(clean(ch.get("text", "")))
                note = "1 paragraph inserted" + (" (style %s)" % ch["style"] if ch.get("style") else "")
            elif op == "move":
                copies, removals = [], []
                for i in targets:
                    s, e = doc.spans[i]
                    copies.append(build_inserted_copy(doc.xml[s:e], doc.paras[i], revs, doc.decls))
                    removals.append((s, e, build_delete(doc.xml[s:e], doc.paras[i], revs, doc.decls)))
                pos, follows = insert_point(doc, after)
                for s, e, new in removals:
                    edits.append((s, e, len(edits), new))
                edits.append((pos, pos, len(edits), "".join(copies)))
                deleted.update(targets)
                inserted.setdefault(follows, []).extend(old_texts[i] for i in targets)
                note = "%d paragraph(s) moved after p%d" % (len(targets), after)
            else:
                raise ToolError("unknown op %r" % op)
        except ToolError as err:
            where = ("p%d" % ch["para"]) if isinstance(ch.get("para"), int) else "change %d" % n
            skipped.append("change %d (%s %s): skipped because %s" % (n, op, where, err))
            continue
        used.update(targets)
        done.append("change %d: %s %s: %s" % (n, op, ",".join("p%d" % (i + 1) for i in targets) or
                                               "after p%d" % ch.get("para", 0), note))
        for i in targets:
            if doc.keep.get(i) == "keep light":
                notes.append("p%d is marked keep light: make light changes only" % (i + 1))

    edits.sort()
    pieces, cursor = [], 0
    for s, e, _, new in edits:
        if s < cursor:
            raise ToolError("two changes overlap")
        pieces.append(doc.xml[cursor:s])
        pieces.append(new)
        cursor = e
    pieces.append(doc.xml[cursor:])
    new_xml = "".join(pieces)

    try:
        ET.fromstring(new_xml.encode("utf-8"))
    except ET.ParseError as err:
        raise ToolError("the new document.xml is not well formed: %s" % err)
    new_paras = [parse_fragment(new_xml[s:e], doc.decls) for s, e in paragraph_spans(new_xml)]

    reject_ok = view_texts(new_paras, "original") == view_texts(doc.paras, "original")
    accept_ok = None
    if not has_tracked:
        expected = []
        if -1 in inserted:
            expected.extend(inserted[-1])
        for i, text in enumerate(old_texts):
            if i not in deleted:
                expected.append(replaced.get(i, text))
            expected.extend(inserted.get(i, []))
        accept_ok = view_texts(new_paras, "accepted") == expected

    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(out_path, "w") as zout:
        for item in zin.infolist():
            data = new_xml.encode("utf-8") if item.filename == DOC_PART else zin.read(item.filename)
            info = zipfile.ZipInfo(item.filename, date_time=item.date_time)
            info.compress_type = item.compress_type
            info.external_attr = item.external_attr
            info.create_system = item.create_system
            zout.writestr(info, data)
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(out_path) as zout:
        others = [x for x in zin.namelist() if x != DOC_PART]
        same = sum(1 for x in others if x in zout.namelist() and zin.read(x) == zout.read(x))

    def yes(flag):
        return "not checked (the file already had tracked changes)" if flag is None else ("yes" if flag else "NO")

    total = len(spec.get("changes", []))
    print("applied: %d of %d changes" % (len(done), total))
    for line in done:
        print("  " + line)
    if skipped:
        print("skipped: %d. Put their proposed text in the chat instead." % len(skipped))
        for line in skipped:
            print("  " + line)
    for line in notes:
        print("note: " + line)
    if protected:
        print("protected content, per replaced paragraph:")
        for block in protected:
            print("  " + block.replace("\n", "\n  "))
    print("check, reject all gives the original text: %s" % yes(reject_ok))
    print("check, accept all gives the requested text: %s" % yes(accept_ok))
    print("check, other parts of the file unchanged: %s (%d of %d)" % (yes(same == len(others)), same, len(others)))
    print("output: %s" % os.path.abspath(out_path))
    return 0 if reject_ok and accept_ok is not False and same == len(others) else 1


# ---------------------------------------------------------------- from text


def cmd_from_text(text_path, out_path):
    with open(text_path, encoding="utf-8") as f:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", f.read()) if b.strip()]
    body = []
    for block in blocks:
        m = re.match(r"(#{1,3})\s+(.*)", block)
        if m and "\n" not in block:
            style, text = "Heading%d" % len(m.group(1)), m.group(2)
        else:
            style, text = None, " ".join(line.strip() for line in block.splitlines())
        ppr = '<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % style if style else ""
        body.append("<w:p>%s%s</w:p>" % (ppr, make_run("", clean(text), False)))
    decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    heading = ('<w:style w:type="paragraph" w:styleId="Heading%d"><w:name w:val="heading %d"/>'
               '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/>'
               '<w:outlineLvl w:val="%d"/></w:pPr><w:rPr><w:b/><w:sz w:val="%d"/></w:rPr></w:style>')
    styles = (decl + '<w:styles xmlns:w="%s"><w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
              '<w:name w:val="Normal"/><w:qFormat/></w:style>%s</w:styles>'
              % (W_NS, "".join(heading % (n, n, n - 1, 34 - 4 * n) for n in (1, 2, 3))))
    parts = {
        "[Content_Types].xml": decl +
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.'
        'wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.'
        'wordprocessingml.styles+xml"/></Types>',
        "_rels/.rels": decl +
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
        'officeDocument" Target="word/document.xml"/></Relationships>',
        "word/_rels/document.xml.rels": decl +
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
        'styles" Target="styles.xml"/></Relationships>',
        "word/document.xml": decl + '<w:document xmlns:w="%s"><w:body>%s<w:sectPr/></w:body></w:document>'
        % (W_NS, "".join(body)),
        "word/styles.xml": styles,
    }
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts.items():
            z.writestr(name, text.encode("utf-8"))
    print("wrote %s: %d paragraphs" % (os.path.abspath(out_path), len(body)))
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description="Read a Word file and write tracked changes into a copy.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("outline")
    p.add_argument("file")
    p = sub.add_parser("read")
    p.add_argument("file")
    p.add_argument("--section")
    p.add_argument("--paras")
    p = sub.add_parser("apply")
    p.add_argument("file")
    p.add_argument("changes")
    p.add_argument("out")
    p.add_argument("--replace", action="store_true", help="overwrite OUT if it exists")
    p = sub.add_parser("from-text")
    p.add_argument("text")
    p.add_argument("out")
    p.add_argument("--replace", action="store_true", help="overwrite OUT if it exists")
    args = parser.parse_args(argv)
    if args.cmd in ("apply", "from-text") and os.path.exists(args.out):
        source = args.file if args.cmd == "apply" else args.text
        if os.path.abspath(args.out) == os.path.abspath(source):
            print("error: OUT is the input file. Write the changes into a new file.")
            return 2
        if not args.replace:
            print("error: %s already exists. To redo your own output, add --replace. "
                  "If it is from an earlier run, use a new name, such as NAME-tracked-2.docx." % args.out)
            return 2
    try:
        if args.cmd == "outline":
            cmd_outline(args.file)
            return 0
        if args.cmd == "read":
            cmd_read(args.file, args.section, args.paras)
            return 0
        if args.cmd == "apply":
            return cmd_apply(args.file, args.changes, args.out)
        return cmd_from_text(args.text, args.out)
    except (ToolError, OSError, ValueError, ET.ParseError) as err:
        print("error: %s" % err)
        return 2


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # stop quietly when output is cut short
    sys.exit(main(sys.argv[1:]))
