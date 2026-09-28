#!/usr/bin/env python3
"""Build the sample documents in samples/*/built/.

Report: samples/report/source.md becomes built/report.md, built/report.docx
and built/report.pdf. The source writes planted dashes as {emdash} and
{endash}, so that no dash character appears in the repo's text files.
Keep marks and notes in the source become Word comments in the .docx.

Thesis: samples/thesis/main.tex becomes built/thesis.pdf.

Standard library only. The PDFs need LibreOffice (soffice) and LaTeX
(pdflatex, bibtex). A missing tool skips that file with a note.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(ROOT, "samples", "report")
THESIS_DIR = os.path.join(ROOT, "samples", "thesis")
STAMP = "2026-09-28T09:00:00Z"
FIXED_TIME = (2026, 9, 28, 9, 0, 0)
PLACEHOLDERS = {"{emdash}": "\u2014", "{endash}": "\u2013"}

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_WORD = "application/vnd.openxmlformats-officedocument.wordprocessingml"
DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

MARKER = re.compile(r"^<!--\s*(keep light|keep|end keep|note)\s*:?\s*(.*?)\s*-->$")
INLINE = re.compile(r"(\*\*|\*|\[\^[A-Za-z0-9_-]+\])")
FOOTNOTE_DEF = re.compile(r"^\[\^([A-Za-z0-9_-]+)\]:\s*(.*)$")


# ---------------------------------------------------------------- parsing the source


def fill(text):
    for key, char in PLACEHOLDERS.items():
        text = text.replace(key, char)
    return text


def parse_source(text):
    """Blocks (title, subtitle, heading, para, table) plus comments and footnotes."""
    blocks, comments, footnotes = [], [], {}
    buffer, table = [], []
    pending_starts, open_keep = [], None

    def add_block(block):
        block.setdefault("starts", [])
        block.setdefault("ends", [])
        block["starts"].extend(pending_starts)
        pending_starts.clear()
        blocks.append(block)

    def flush():
        if buffer:
            text = " ".join(line.strip() for line in buffer)
            buffer.clear()
            if text.startswith("*") and text.endswith("*") and not text.startswith("**"):
                add_block({"kind": "subtitle", "text": text[1:-1]})
            else:
                add_block({"kind": "para", "text": text})
        if table:
            rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
                    for line in table if not re.match(r"^\|\s*-", line)]
            table.clear()
            add_block({"kind": "table", "rows": rows})

    for line in text.splitlines():
        stripped = line.strip()
        marker = MARKER.match(stripped)
        footnote = FOOTNOTE_DEF.match(stripped)
        if marker:
            flush()
            kind, body = marker.group(1), marker.group(2)
            if kind in ("keep", "keep light"):
                cid = len(comments)
                comments.append((cid, "%s: %s" % (kind, body) if body else kind))
                pending_starts.append(cid)
                open_keep = cid
            elif kind == "end keep":
                if open_keep is not None and blocks:
                    blocks[-1]["ends"].append(open_keep)
                open_keep = None
            else:
                cid = len(comments)
                comments.append((cid, "Note: " + body))
                pending_starts.append(("note", cid))
        elif footnote:
            flush()
            footnotes[footnote.group(1)] = footnote.group(2)
        elif stripped.startswith("|"):
            if buffer:
                flush()
            table.append(stripped)
        elif not stripped:
            flush()
        elif stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            add_block({"kind": "title" if level == 1 else "heading", "level": level - 1, "text": title})
        else:
            if table:
                flush()
            buffer.append(stripped)
    flush()

    # A note covers only the block right after it.
    for block in blocks:
        starts = []
        for item in block["starts"]:
            if isinstance(item, tuple):
                starts.append(item[1])
                block["ends"].append(item[1])
            else:
                starts.append(item)
        block["starts"] = starts
    return blocks, comments, footnotes


# ---------------------------------------------------------------- writing the .docx


def runs_xml(text, footnote_ids):
    out, bold, italic = [], False, False
    for part in INLINE.split(text):
        if part == "**":
            bold = not bold
        elif part == "*":
            italic = not italic
        elif part.startswith("[^"):
            fid = footnote_ids[part[2:-1]]
            out.append('<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
                       '<w:footnoteReference w:id="%d"/></w:r>' % fid)
        elif part:
            props = ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "")
            rpr = "<w:rPr>%s</w:rPr>" % props if props else ""
            out.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(part)))
    return "".join(out)


def paragraph_xml(block, footnote_ids, style=None, text=None):
    ppr = '<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % style if style else ""
    body = runs_xml(block["text"] if text is None else text, footnote_ids)
    starts = "".join('<w:commentRangeStart w:id="%d"/>' % c for c in block["starts"])
    ends = "".join('<w:commentRangeEnd w:id="%d"/><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>'
                   '<w:commentReference w:id="%d"/></w:r>' % (c, c) for c in block["ends"])
    return "<w:p>%s%s%s%s</w:p>" % (ppr, starts, body, ends)


def table_xml(block, footnote_ids):
    rows = block["rows"]
    width = 9000 // len(rows[0])
    grid = "".join('<w:gridCol w:w="%d"/>' % width for _ in rows[0])
    trs = []
    for r, row in enumerate(rows):
        cells = []
        for cell in row:
            text = "**%s**" % cell if r == 0 else cell
            cells.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr>%s</w:tc>'
                         % (width, paragraph_xml({"text": text, "starts": [], "ends": []}, footnote_ids)))
        trs.append("<w:tr>%s</w:tr>" % "".join(cells))
    table = ('<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
             '<w:tblLook w:val="04A0"/></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>' % (grid, "".join(trs)))
    if block["starts"] or block["ends"]:
        raise ValueError("comments on tables are not supported")
    return table


def document_xml(blocks, footnote_ids):
    body = []
    for block in blocks:
        kind = block["kind"]
        if kind == "title":
            body.append(paragraph_xml(block, footnote_ids, style="Title"))
        elif kind == "subtitle":
            body.append(paragraph_xml(block, footnote_ids, text="*%s*" % block["text"]))
        elif kind == "heading":
            body.append(paragraph_xml(block, footnote_ids, style="Heading%d" % block["level"]))
        elif kind == "para":
            body.append(paragraph_xml(block, footnote_ids))
        else:
            body.append(table_xml(block, footnote_ids))
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" '
            'w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')
    return DECL + ('<w:document xmlns:w="%s" xmlns:r="%s"><w:body>%s%s</w:body></w:document>'
                   % (W_NS, R_NS, "".join(body), sect))


def comments_xml(comments):
    items = "".join(
        '<w:comment w:id="%d" w:author="Sample Writer" w:date="%s" w:initials="SW">'
        '<w:p><w:pPr><w:pStyle w:val="CommentText"/></w:pPr>'
        '<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r>'
        '<w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p></w:comment>' % (cid, STAMP, escape(text))
        for cid, text in comments)
    return DECL + '<w:comments xmlns:w="%s">%s</w:comments>' % (W_NS, items)


def footnotes_xml(footnotes, footnote_ids):
    sep = ('<w:footnote w:type="%s" w:id="%d"><w:p><w:pPr><w:spacing w:after="0" w:line="240" '
           'w:lineRule="auto"/></w:pPr><w:r><w:%s/></w:r></w:p></w:footnote>')
    items = [sep % ("separator", -1, "separator"), sep % ("continuationSeparator", 0, "continuationSeparator")]
    for key, text in footnotes.items():
        items.append('<w:footnote w:id="%d"><w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>'
                     '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
                     '<w:r><w:t xml:space="preserve"> %s</w:t></w:r></w:p></w:footnote>'
                     % (footnote_ids[key], escape(text)))
    return DECL + '<w:footnotes xmlns:w="%s">%s</w:footnotes>' % (W_NS, "".join(items))


def styles_xml():
    borders = "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="auto"/>' % side
                      for side in ("top", "left", "bottom", "right", "insideH", "insideV"))

    def para_style(sid, name, ppr="", rpr="", extra=""):
        return ('<w:style w:type="paragraph" w:styleId="%s"><w:name w:val="%s"/><w:basedOn w:val="Normal"/>'
                '%s<w:qFormat/>%s%s</w:style>' % (sid, name, extra, ppr, rpr))

    parts = [
        '<w:styles xmlns:w="%s">' % W_NS,
        "<w:docDefaults>"
        '<w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" '
        'w:cs="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-US"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
        "</w:docDefaults>",
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>',
        '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont">'
        '<w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>',
        para_style("Title", "Title", rpr='<w:rPr><w:sz w:val="44"/></w:rPr>', extra='<w:next w:val="Normal"/>'),
        para_style("Heading1", "heading 1",
                   ppr='<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="0"/></w:pPr>',
                   rpr='<w:rPr><w:b/><w:sz w:val="32"/></w:rPr>', extra='<w:next w:val="Normal"/>'),
        para_style("Heading2", "heading 2",
                   ppr='<w:pPr><w:keepNext/><w:spacing w:before="160" w:after="60"/><w:outlineLvl w:val="1"/></w:pPr>',
                   rpr='<w:rPr><w:b/><w:sz w:val="26"/></w:rPr>', extra='<w:next w:val="Normal"/>'),
        para_style("FootnoteText", "footnote text",
                   ppr='<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>',
                   rpr='<w:rPr><w:sz w:val="18"/></w:rPr>'),
        para_style("CommentText", "annotation text", rpr='<w:rPr><w:sz w:val="20"/></w:rPr>'),
        '<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/>'
        '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>',
        '<w:style w:type="character" w:styleId="CommentReference"><w:name w:val="annotation reference"/>'
        '<w:rPr><w:sz w:val="16"/></w:rPr></w:style>',
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>'
        "<w:tblPr><w:tblBorders>%s</w:tblBorders></w:tblPr></w:style>" % borders,
        "</w:styles>",
    ]
    return DECL + "".join(parts)


def build_docx(blocks, comments, footnotes, title, path):
    footnote_ids = {key: n for n, key in enumerate(footnotes, 1)}
    override = '<Override PartName="/%s" ContentType="%s"/>'
    parts = [
        ("[Content_Types].xml", DECL +
         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
         '<Default Extension="xml" ContentType="application/xml"/>'
         + override % ("word/document.xml", CT_WORD + ".document.main+xml")
         + override % ("word/styles.xml", CT_WORD + ".styles+xml")
         + override % ("word/settings.xml", CT_WORD + ".settings+xml")
         + override % ("word/comments.xml", CT_WORD + ".comments+xml")
         + override % ("word/footnotes.xml", CT_WORD + ".footnotes+xml")
         + override % ("docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml")
         + override % ("docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml")
         + "</Types>"),
        ("_rels/.rels", DECL +
         '<Relationships xmlns="%s">'
         '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/>'
         '<Relationship Id="rId2" Type="%s/metadata/core-properties" Target="docProps/core.xml"/>'
         '<Relationship Id="rId3" Type="%s/extended-properties" Target="docProps/app.xml"/>'
         "</Relationships>" % (PKG_REL, DOC_REL, PKG_REL, DOC_REL)),
        ("docProps/core.xml", DECL +
         '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
         'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
         "<dc:title>%s</dc:title><dc:creator>Sample Writer</dc:creator>"
         '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
         '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
         "</cp:coreProperties>" % (escape(title), STAMP, STAMP)),
        ("docProps/app.xml", DECL +
         '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
         "<Application>writing toolkit samples</Application></Properties>"),
        ("word/_rels/document.xml.rels", DECL +
         '<Relationships xmlns="%s">'
         '<Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>'
         '<Relationship Id="rId2" Type="%s/settings" Target="settings.xml"/>'
         '<Relationship Id="rId3" Type="%s/comments" Target="comments.xml"/>'
         '<Relationship Id="rId4" Type="%s/footnotes" Target="footnotes.xml"/>'
         "</Relationships>" % (PKG_REL, DOC_REL, DOC_REL, DOC_REL, DOC_REL)),
        ("word/document.xml", document_xml(blocks, footnote_ids)),
        ("word/styles.xml", styles_xml()),
        ("word/settings.xml", DECL +
         '<w:settings xmlns:w="%s"><w:footnotePr><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr>'
         '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" '
         'w:val="15"/></w:compat></w:settings>' % W_NS),
        ("word/comments.xml", comments_xml(comments)),
        ("word/footnotes.xml", footnotes_xml(footnotes, footnote_ids)),
    ]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts:
            z.writestr(zipfile.ZipInfo(name, date_time=FIXED_TIME), text.encode("utf-8"),
                       compress_type=zipfile.ZIP_DEFLATED)


# ---------------------------------------------------------------- PDFs


def soffice_pdf(docx_path, out_dir):
    soffice = shutil.which("soffice")
    if not soffice:
        print("skipped %s: LibreOffice (soffice) is not installed" % os.path.basename(docx_path).replace(".docx", ".pdf"))
        return
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([soffice, "--headless", "-env:UserInstallation=file://" + profile,
                        "--convert-to", "pdf", "--outdir", out_dir, docx_path],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    print("wrote %s" % os.path.join(out_dir, os.path.basename(docx_path)[:-5] + ".pdf"))


def latex_pdf(src_dir, out_path):
    if not (shutil.which("pdflatex") and shutil.which("bibtex")):
        print("skipped %s: LaTeX (pdflatex, bibtex) is not installed" % out_path)
        return
    with tempfile.TemporaryDirectory() as work:
        for name in os.listdir(src_dir):
            if name.endswith((".tex", ".bib")):
                shutil.copy(os.path.join(src_dir, name), work)
        latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        for cmd in (latex, ["bibtex", "main"], latex, latex):
            result = subprocess.run(cmd, cwd=work, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
            if result.returncode != 0:
                sys.stdout.write(result.stdout.decode("utf-8", "replace")[-2000:])
                raise SystemExit("LaTeX failed on: %s" % " ".join(cmd))
        shutil.copy(os.path.join(work, "main.pdf"), out_path)
    print("wrote %s" % out_path)


# ---------------------------------------------------------------- main


def build_report():
    with open(os.path.join(REPORT_DIR, "source.md"), encoding="utf-8") as f:
        source = f.read()
    built = os.path.join(REPORT_DIR, "built")
    os.makedirs(built, exist_ok=True)
    text = fill(source)
    md_path = os.path.join(built, "report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote %s" % md_path)
    blocks, comments, footnotes = parse_source(text)
    title = next(b["text"] for b in blocks if b["kind"] == "title")
    docx_path = os.path.join(built, "report.docx")
    build_docx(blocks, comments, footnotes, title, docx_path)
    print("wrote %s" % docx_path)
    soffice_pdf(docx_path, built)


def build_thesis():
    built = os.path.join(THESIS_DIR, "built")
    os.makedirs(built, exist_ok=True)
    latex_pdf(THESIS_DIR, os.path.join(built, "thesis.pdf"))


if __name__ == "__main__":
    build_report()
    build_thesis()
