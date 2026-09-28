#!/usr/bin/env python3
"""Spike script for the writing toolkit.

Reads a Word file and writes tracked changes into a copy.
Standard library only. No network calls.

Commands:
  env                  Print the Python version, the folders that exist and the .docx files found.
  read FILE            List the paragraphs (numbered), their styles and flags, and the comments.
  apply FILE JSON OUT  Write the changes in the JSON file as tracked changes into OUT.

JSON format:
  {"author": "Claude",
   "changes": [
     {"op": "replace", "para": 6, "expect": "first words", "text": "new paragraph text"},
     {"op": "insert_after", "para": 3, "text": "new paragraph text", "style": "Heading2"},
     {"op": "delete", "para": 15, "expect": "first words"}]}

Paragraph numbers come from the read command. "expect" is optional: a change is
skipped unless its paragraph starts with those words. "style" is optional.
"""

import argparse
import datetime
import difflib
import importlib.util
import json
import os
import platform
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W = "{" + W_NS + "}"
DOC_PART = "word/document.xml"
COMMENTS_PART = "word/comments.xml"

# Attributes inside a start tag. Values may hold any character except their own quote.
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

P_CHILDREN = {"pPr", "r", "proofErr", "bookmarkStart", "bookmarkEnd"}
P_CHILDREN_DELETE = P_CHILDREN | {"commentRangeStart", "commentRangeEnd"}
R_CHILDREN = {"rPr", "t", "tab", "br", "cr", "lastRenderedPageBreak"}


class ProbeError(Exception):
    pass


def local(tag):
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def norm(text):
    return " ".join(text.split()).lower()


# ---------------------------------------------------------------- reading


def root_namespaces(xml):
    m = re.search(r"<w:document\b([^>]*)>", xml)
    if not m:
        raise ProbeError("no <w:document> root: the main namespace does not use the w: prefix")
    decls = dict(re.findall(r'xmlns:([A-Za-z0-9_.-]+)\s*=\s*"([^"]*)"', m.group(1)))
    if decls.get("w") != W_NS:
        raise ProbeError("the w: prefix is not the Word main namespace")
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
        raise ProbeError("unbalanced paragraphs in word/document.xml")
    return spans


def table_spans(xml):
    spans, stack = [], []
    for m in TBL_TOKEN.finditer(xml):
        if m.group(0) == "</w:tbl>":
            if stack:
                spans.append((stack.pop(), m.end()))
        else:
            stack.append(m.start())
    return spans


def para_text(p, view="accepted"):
    """Text of one paragraph. view "original" rejects all tracked changes, "accepted" accepts them."""
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
            flags.add("textbox")
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
                    raise ProbeError("not a Word file: word/document.xml is missing")
                self.xml = z.read(DOC_PART).decode("utf-8")
                self.comments_xml = z.read(COMMENTS_PART).decode("utf-8") if COMMENTS_PART in names else None
        except zipfile.BadZipFile:
            raise ProbeError("not a Word file: it is not a zip package")
        self.decls = root_namespaces(self.xml)
        self.spans = paragraph_spans(self.xml)
        self.paras = [parse_fragment(self.xml[s:e], self.decls) for s, e in self.spans]
        self.tables = table_spans(self.xml)

    def in_table(self, i):
        s, e = self.spans[i]
        return any(ts <= s and e <= te for ts, te in self.tables)

    def label(self, i):
        style = para_style(self.paras[i])
        if self.in_table(i):
            return "table"
        if style:
            m = re.fullmatch(r"[Hh]eading\s?(\d)", style)
            return "H" + m.group(1) if m else style
        return "body"

    def comments(self):
        if not self.comments_xml:
            return []
        root = ET.fromstring(self.comments_xml.encode("utf-8"))
        out = []
        for c in root.findall(W + "comment"):
            text = " ".join(para_text(p) for p in c.findall(W + "p")).strip()
            out.append((c.get(W + "id"), c.get(W + "author") or "", text))
        return out

    def comment_anchors(self):
        anchors = {}
        for kind in ("commentRangeStart", "commentReference"):
            for i, p in enumerate(self.paras, 1):
                for el in p.iter(W + kind):
                    anchors.setdefault(el.get(W + "id"), i)
        return anchors


def cmd_read(path):
    doc = Doc(path)
    print("file: %s" % path)
    print("paragraphs: %d" % len(doc.paras))
    for i, p in enumerate(doc.paras):
        text = para_text(p).replace("\t", " ").replace("\n", " / ")
        flags = para_flags(p)
        extra = "  {%s}" % ", ".join(sorted(flags)) if flags else ""
        print("p%d [%s] %s%s" % (i + 1, doc.label(i), text, extra))
    comments = doc.comments()
    anchors = doc.comment_anchors()
    print("comments: %d" % len(comments))
    for cid, author, text in comments:
        where = "p%d" % anchors[cid] if cid in anchors else "no anchor"
        print("c%s on %s by %s: %s" % (cid, where, author, text))


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


def clean(text):
    return BAD_XML_CHARS.sub("", text)


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
    return "".join(parts)


def check_simple(p, for_delete=False):
    """Return why the paragraph is not safe to edit, or None."""
    allowed = P_CHILDREN_DELETE if for_delete else P_CHILDREN
    gobacks = set()
    for child in p:
        if not child.tag.startswith(W):
            return "it holds %s" % child.tag
        name = local(child.tag)
        if name not in allowed:
            return "it holds w:%s" % name
        if name == "pPr":
            for sub in child:
                if local(sub.tag) in ("sectPr", "pPrChange"):
                    return "its properties hold w:%s" % local(sub.tag)
            inserted, deleted = mark_state(p)
            if inserted or deleted:
                return "its paragraph mark is already a tracked change"
        elif name == "bookmarkStart":
            if child.get(W + "name") != "_GoBack" and not for_delete:
                return "it holds a bookmark"
            gobacks.add(child.get(W + "id"))
        elif name == "bookmarkEnd":
            if child.get(W + "id") not in gobacks and not for_delete:
                return "it holds the end of a bookmark"
        elif name == "r":
            for sub in child:
                sname = local(sub.tag)
                if sname == "commentReference" and for_delete:
                    continue
                if sname not in R_CHILDREN:
                    return "a run holds w:%s" % sname
                if sname == "br" and sub.get(W + "type") not in (None, "textWrapping"):
                    return "it holds a page or column break"
                if sname == "rPr" and sub.find(W + "rPrChange") is not None:
                    return "it holds a tracked format change"
    return None


def split_paragraph(frag):
    """Start tag, raw pPr and the raw content after it."""
    if frag.endswith("/>"):
        return frag[:-2].rstrip() + ">", "", ""
    m = P_START.match(frag)
    if not m:
        raise ProbeError("could not read a paragraph start tag")
    inner = frag[m.end():-len("</w:p>")]
    ppr = PPR_RAW.match(inner.lstrip())
    if ppr:
        lead = len(inner) - len(inner.lstrip())
        return m.group(0), ppr.group(0), inner[lead + ppr.end():]
    return m.group(0), "", inner


def build_replace(frag, p, new_text, revs, decls):
    reason = check_simple(p)
    if reason:
        return None, reason, None
    start, ppr, rest = split_paragraph(frag)
    raw_runs = RUN_RAW.findall(rest)
    if len(raw_runs) != len(p.findall(W + "r")):
        return None, "its runs could not be matched", None
    rprs, chars = [], []
    for idx, raw in enumerate(raw_runs):
        m = RPR_RAW.search(raw)
        rprs.append(m.group(0) if m else "")
        for ch in run_pieces(parse_fragment(raw, decls)):
            chars.append((ch, idx))
    old_text = "".join(c for c, _ in chars)
    new_text = clean(new_text)
    if new_text == old_text:
        return None, "the new text is the same as the old text", None

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
    return start + ppr + "".join(body) + "</w:p>", None, note


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
    reason = check_simple(p, for_delete=True)
    if reason:
        return None, reason, None
    start, ppr, rest = split_paragraph(frag)
    tokens = CHILD_RAW.findall(rest)
    if re.sub(r"\s", "", "".join(tokens)) != re.sub(r"\s", "", rest):
        return None, "its content could not be split safely", None
    out, pending = [], []

    def flush():
        if pending:
            out.append(revs.wrap("del", "".join(pending)))
            pending.clear()

    for tok in tokens:
        is_run = RUN_RAW.fullmatch(tok) is not None and "commentReference" not in tok
        if is_run:
            m = RPR_RAW.search(tok)
            run = make_run(m.group(0) if m else "", run_pieces(parse_fragment(tok, decls)), True)
            if run:
                pending.append(run)
        else:
            flush()
            out.append(tok)
    flush()
    return start + mark_paragraph(ppr, "del", revs) + "".join(out) + "</w:p>", None, "1 paragraph deleted"


def build_insert(text, style, revs):
    if style and not re.fullmatch(r"[A-Za-z0-9_-]+", style):
        return None, "the style name is not valid", None
    pstyle = '<w:pStyle w:val="%s"/>' % style if style else ""
    mark = "<w:ins %s/>" % revs.attrs()
    body = revs.wrap("ins", make_run("", clean(text), False))
    return "<w:p><w:pPr>%s<w:rPr>%s</w:rPr></w:pPr>%s</w:p>" % (pstyle, mark, body), None, "1 paragraph inserted"


def cmd_apply(path, json_path, out_path):
    with open(json_path, encoding="utf-8") as f:
        spec = json.load(f)
    doc = Doc(path)
    revs = Revisions(doc.xml, spec.get("author") or "Claude")
    old_texts = [para_text(p) for p in doc.paras]
    has_tracked = any("tracked" in para_flags(p) for p in doc.paras)

    edits, done, skipped, used = [], [], [], set()
    replaced, deleted, inserted = {}, set(), {}
    for n, ch in enumerate(spec.get("changes", []), 1):
        op, para = ch.get("op"), ch.get("para")
        if not isinstance(para, int) or not 1 <= para <= len(doc.paras):
            skipped.append("change %d: no paragraph %s" % (n, para))
            continue
        i = para - 1
        s, e = doc.spans[i]
        if "expect" in ch and not norm(old_texts[i]).startswith(norm(ch["expect"])):
            skipped.append("change %d: p%d does not start with %r" % (n, para, ch["expect"]))
            continue
        if op in ("replace", "delete") and para in used:
            skipped.append("change %d: p%d already has a change" % (n, para))
            continue
        if op == "replace":
            new, reason, note = build_replace(doc.xml[s:e], doc.paras[i], ch.get("text", ""), revs, doc.decls)
            span = (s, e)
        elif op == "delete":
            new, reason, note = build_delete(doc.xml[s:e], doc.paras[i], revs, doc.decls)
            span = (s, e)
        elif op == "insert_after":
            new, reason, note = build_insert(ch.get("text", ""), ch.get("style"), revs)
            span = (e, e)
        else:
            skipped.append("change %d: unknown op %r" % (n, op))
            continue
        if new is None:
            skipped.append("change %d: p%d skipped because %s" % (n, para, reason))
            continue
        if op == "replace":
            replaced[i] = clean(ch.get("text", ""))
            used.add(para)
        elif op == "delete":
            deleted.add(i)
            used.add(para)
        else:
            inserted.setdefault(i, []).append(clean(ch.get("text", "")))
        edits.append((span[0], span[1], len(edits), new))
        done.append("p%d %s: %s" % (para, op, note))

    edits.sort()
    pieces, cursor = [], 0
    for s, e, _, new in edits:
        if s < cursor:
            raise ProbeError("two changes overlap")
        pieces.append(doc.xml[cursor:s])
        pieces.append(new)
        cursor = e
    pieces.append(doc.xml[cursor:])
    new_xml = "".join(pieces)

    try:
        ET.fromstring(new_xml.encode("utf-8"))
    except ET.ParseError as err:
        raise ProbeError("the new document.xml is not well formed: %s" % err)
    new_paras = [parse_fragment(new_xml[s:e], doc.decls) for s, e in paragraph_spans(new_xml)]

    reject_ok = view_texts(new_paras, "original") == view_texts(doc.paras, "original")
    if has_tracked:
        accept_ok = None
    else:
        expected = []
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
        others = [n for n in zin.namelist() if n != DOC_PART]
        same = sum(1 for n in others if n in zout.namelist() and zin.read(n) == zout.read(n))

    def yes(flag):
        return "not checked (the file already had tracked changes)" if flag is None else ("yes" if flag else "NO")

    print("applied: %d of %d changes" % (len(done), len(spec.get("changes", []))))
    for line in done:
        print("  " + line)
    print("skipped: %s" % ("none" if not skipped else len(skipped)))
    for line in skipped:
        print("  " + line)
    print("check, reject all gives the original text: %s" % yes(reject_ok))
    print("check, accept all gives the requested text: %s" % yes(accept_ok))
    print("check, other parts of the file unchanged: %s (%d of %d)" % (yes(same == len(others)), same, len(others)))
    print("output: %s" % os.path.abspath(out_path))
    return 0 if reject_ok and accept_ok is not False and same == len(others) else 1


# ---------------------------------------------------------------- environment


def find_docx(roots, limit=40):
    found, seen = [], set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath[len(root):].count(os.sep)
            dirnames[:] = [] if depth >= 4 else [
                d for d in dirnames if not d.startswith(".") and d not in ("node_modules", "__pycache__")]
            for name in filenames:
                full = os.path.realpath(os.path.join(dirpath, name))
                if name.lower().endswith(".docx") and not name.startswith("~$") and full not in seen:
                    seen.add(full)
                    found.append(full)
                    if len(found) >= limit:
                        return found
    return found


def cmd_env():
    print("python: %s" % platform.python_version())
    print("system: %s %s" % (platform.system(), platform.release()))
    print("working folder: %s" % os.getcwd())
    print("script: %s" % os.path.abspath(__file__))
    if os.path.isdir("/mnt"):
        print("/mnt holds: %s" % ", ".join(sorted(os.listdir("/mnt"))))
    for folder in ("/mnt/user-data/uploads", "/mnt/user-data/outputs", "/mnt/data"):
        print("folder %s: %s" % (folder, "yes" if os.path.isdir(folder) else "no"))
    for mod in ("lxml", "docx", "pypdf"):
        print("module %s: %s" % (mod, "yes" if importlib.util.find_spec(mod) else "no"))
    roots = ["/mnt/user-data", "/mnt/data", os.getcwd(), os.path.expanduser("~")]
    found = find_docx(roots)
    print("docx files found: %d" % len(found))
    for path in found:
        print("  %s" % path)


def main(argv):
    parser = argparse.ArgumentParser(description="Spike script for the writing toolkit.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("env")
    p_read = sub.add_parser("read")
    p_read.add_argument("file")
    p_apply = sub.add_parser("apply")
    p_apply.add_argument("file")
    p_apply.add_argument("changes")
    p_apply.add_argument("out")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "env":
            cmd_env()
            return 0
        if args.cmd == "read":
            cmd_read(args.file)
            return 0
        return cmd_apply(args.file, args.changes, args.out)
    except (ProbeError, OSError, ValueError, ET.ParseError) as err:
        print("error: %s" % err)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
