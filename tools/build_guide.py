#!/usr/bin/env python3
"""Build the web guide as a Word file: docs/web-guide.md to dist/web-guide.docx.

It reads a small part of Markdown: "# " is the title, "## " and "### " are headings,
"1. " starts a numbered step (indent it for a sub-step), a line that starts with
"[Screenshot" is a screenshot place, and **bold**, `code` and web links work inside
a line. Everything else is a plain paragraph. A blank line ends a paragraph.

  python3 tools/build_guide.py [SOURCE] [OUT]

Standard library only. No network calls.
"""

import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "docs", "web-guide.md")
OUT = os.path.join(ROOT, "dist", "web-guide.docx")
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
STAMP = "2026-01-01T00:00:00Z"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_WORD = "application/vnd.openxmlformats-officedocument.wordprocessingml"
DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

STEP = re.compile(r"^( *)(\d+)\.\s+(.*)$")
INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|https?://[^\s)]+[^\s).,;:])")


def parse(text):
    """Blocks as (kind, level, text). Kinds: title, heading, step, shot, para."""
    blocks, buffer = [], []

    def flush():
        if buffer:
            blocks.append(("para", 0, " ".join(buffer)))
            buffer.clear()

    for line in text.splitlines():
        stripped = line.strip()
        step = STEP.match(line)
        if not stripped:
            flush()
        elif stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            kind = "title" if level == 1 else "heading"
            blocks.append((kind, max(level - 1, 1), stripped[level:].strip()))
        elif stripped.startswith("[Screenshot"):
            flush()
            blocks.append(("shot", 0, stripped.strip("[]")))
        elif step:
            flush()
            level = 1 if len(step.group(1)) >= 2 else 0
            blocks.append(("step", level, "%s.\t%s" % (step.group(2), step.group(3))))
        elif blocks and blocks[-1][0] == "step" and line.startswith("   ") and not buffer:
            kind, level, body = blocks[-1]
            blocks[-1] = (kind, level, body + " " + stripped)
        else:
            buffer.append(stripped)
    flush()
    return blocks


class Links:
    """Relationship ids for web links."""

    def __init__(self):
        self.targets = []

    def rid(self, url):
        if url not in self.targets:
            self.targets.append(url)
        return "rIdL%d" % (self.targets.index(url) + 1)


def runs(text, links, rpr=""):
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            out.append(run(part[2:-2], "<w:b/>" + rpr))
        elif part.startswith("`"):
            out.append(run(part[1:-1], '<w:rStyle w:val="Code"/>' + rpr))
        elif part.startswith("http"):
            out.append('<w:hyperlink r:id="%s">%s</w:hyperlink>'
                       % (links.rid(part), run(part, '<w:rStyle w:val="Hyperlink"/>' + rpr)))
        else:
            out.append(run(part, rpr))
    return "".join(out)


def run(text, rpr):
    pieces = text.split("\t")
    body = '<w:tab/>'.join('<w:t xml:space="preserve">%s</w:t>' % escape(p) for p in pieces)
    return "<w:r>%s%s</w:r>" % ("<w:rPr>%s</w:rPr>" % rpr if rpr else "", body)


def paragraph(style, body):
    return '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p>' % (style, body)


def document_xml(blocks, links):
    body = []
    for kind, level, text in blocks:
        if kind == "title":
            body.append(paragraph("Title", runs(text, links)))
        elif kind == "heading":
            body.append(paragraph("Heading%d" % level, runs(text, links)))
        elif kind == "step":
            body.append(paragraph("Step%d" % (level + 1), runs(text, links)))
        elif kind == "shot":
            body.append(paragraph("Screenshot", runs(text, links)))
        else:
            body.append(paragraph("Normal", runs(text, links)))
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" '
            'w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')
    return DECL + ('<w:document xmlns:w="%s" xmlns:r="%s"><w:body>%s%s</w:body></w:document>'
                   % (W_NS, R_NS, "".join(body), sect))


def styles_xml():
    def para(sid, name, ppr="", rpr="", extra=""):
        return ('<w:style w:type="paragraph" w:styleId="%s"><w:name w:val="%s"/><w:basedOn w:val="Normal"/>'
                '%s<w:qFormat/>%s%s</w:style>' % (sid, name, extra, ppr, rpr))

    def step(sid, name, left):
        return para(sid, name, ppr='<w:pPr><w:tabs><w:tab w:val="left" w:pos="%d"/></w:tabs>'
                                   '<w:spacing w:after="80"/><w:ind w:left="%d" w:hanging="425"/></w:pPr>'
                                   % (left, left))

    box = "".join('<w:%s w:val="single" w:sz="6" w:space="4" w:color="7F7F7F"/>' % side
                  for side in ("top", "left", "bottom", "right"))
    return DECL + "".join([
        '<w:styles xmlns:w="%s">' % W_NS,
        "<w:docDefaults><w:rPrDefault><w:rPr>"
        '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>'
        "</w:pPrDefault></w:docDefaults>",
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>',
        '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont">'
        '<w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>',
        para("Title", "Title", ppr='<w:pPr><w:spacing w:after="240"/></w:pPr>',
             rpr='<w:rPr><w:sz w:val="48"/></w:rPr>', extra='<w:next w:val="Normal"/>'),
        para("Heading1", "heading 1",
             ppr='<w:pPr><w:keepNext/><w:spacing w:before="360" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>',
             rpr='<w:rPr><w:b/><w:sz w:val="32"/></w:rPr>', extra='<w:next w:val="Normal"/>'),
        para("Heading2", "heading 2",
             ppr='<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="1"/></w:pPr>',
             rpr='<w:rPr><w:b/><w:sz w:val="26"/></w:rPr>', extra='<w:next w:val="Normal"/>'),
        step("Step1", "Step", 425),
        step("Step2", "Step 2", 850),
        para("Screenshot", "Screenshot place",
             ppr='<w:pPr><w:pBdr>%s</w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="EDEDED"/>'
                 '<w:spacing w:before="120" w:after="240"/><w:jc w:val="center"/></w:pPr>' % box,
             rpr='<w:rPr><w:i/><w:color w:val="595959"/></w:rPr>'),
        '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/>'
        '<w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr></w:style>',
        '<w:style w:type="character" w:styleId="Code"><w:name w:val="Code"/>'
        '<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/></w:rPr></w:style>',
        "</w:styles>",
    ])


def build(source=SOURCE, out=OUT):
    with open(source, encoding="utf-8") as f:
        blocks = parse(f.read())
    title = next((text for kind, _, text in blocks if kind == "title"), "Guide")
    links = Links()
    document = document_xml(blocks, links)
    link_rels = "".join('<Relationship Id="%s" Type="%s/hyperlink" Target="%s" TargetMode="External"/>'
                        % (links.rid(url), DOC_REL, escape(url, {'"': "&quot;"})) for url in links.targets)
    override = '<Override PartName="/%s" ContentType="%s"/>'
    parts = [
        ("[Content_Types].xml", DECL +
         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
         '<Default Extension="xml" ContentType="application/xml"/>'
         + override % ("word/document.xml", CT_WORD + ".document.main+xml")
         + override % ("word/styles.xml", CT_WORD + ".styles+xml")
         + override % ("docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml")
         + "</Types>"),
        ("_rels/.rels", DECL +
         '<Relationships xmlns="%s">'
         '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/>'
         '<Relationship Id="rId2" Type="%s/metadata/core-properties" Target="docProps/core.xml"/>'
         "</Relationships>" % (PKG_REL, DOC_REL, PKG_REL)),
        ("docProps/core.xml", DECL +
         '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
         'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
         "<dc:title>%s</dc:title><dc:creator>writing toolkit</dc:creator>"
         '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
         '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
         "</cp:coreProperties>" % (escape(title), STAMP, STAMP)),
        ("word/_rels/document.xml.rels", DECL +
         '<Relationships xmlns="%s"><Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>%s'
         "</Relationships>" % (PKG_REL, DOC_REL, link_rels)),
        ("word/document.xml", document),
        ("word/styles.xml", styles_xml()),
    ]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts:
            z.writestr(zipfile.ZipInfo(name, date_time=FIXED_TIME), text.encode("utf-8"),
                       compress_type=zipfile.ZIP_DEFLATED)
    return out


def main(argv):
    source = argv[0] if argv else SOURCE
    out = argv[1] if len(argv) > 1 else OUT
    print("wrote %s" % os.path.relpath(build(source, out), ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
