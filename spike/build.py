#!/usr/bin/env python3
"""Build the spike files in spike/dist/.

1. spike-sample.docx: an invented Word file with headings, mixed formatting, a table,
   three comments and a canary line at the end.
2. docx-spike-A.zip, -B.zip and -C.zip: the test skill for claude.ai, with fewer
   frontmatter fields in each. A keeps every field. B drops argument-hint.
   C keeps only name and description.

Standard library only. Every name and number in the sample is made up.
"""

import os
import re
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
SKILL_DIR = os.path.join(HERE, "docx-spike")
SKILL_NAME = "docx-spike"
STAMP = "2026-09-28T09:00:00Z"
FIXED_TIME = (2026, 9, 28, 9, 0, 0)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'


# ---------------------------------------------------------------- sample document


def run(text, bold=False, italic=False):
    props = ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "")
    rpr = "<w:rPr>%s</w:rPr>" % props if props else ""
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(text))


def para(*parts, style=None, comment=None):
    ppr = '<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % style if style else ""
    body = "".join(p if p.startswith("<w:r>") else run(p) for p in parts)
    if comment is not None:
        body = ('<w:commentRangeStart w:id="%d"/>%s<w:commentRangeEnd w:id="%d"/>'
                '<w:r><w:commentReference w:id="%d"/></w:r>' % (comment, body, comment, comment))
    return "<w:p>%s%s</w:p>" % (ppr, body)


def table(rows):
    grid = "".join('<w:gridCol w:w="3000"/>' for _ in rows[0])
    trs = "".join(
        "<w:tr>%s</w:tr>" % "".join(
            '<w:tc><w:tcPr><w:tcW w:w="3000" w:type="dxa"/></w:tcPr>%s</w:tc>' % para(cell) for cell in row)
        for row in rows)
    return ('<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
            '<w:tblLook w:val="04A0"/></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>' % (grid, trs))


def document_xml():
    body = [
        para("Harbour Row Repair Cafe: first-year review", style="Title"),
        para(run("An invented sample for testing the writing toolkit. "
                 "Every name and number in it is made up.", italic=True)),
        para("Summary", style="Heading1"),
        para("In its first year, the cafe fixed 412 bicycles and 96 small appliances. "
             "Volunteers gave 1,830 hours. The cafe should open a second evening each week, "
             "because the waiting list now runs to three weeks."),
        para("Background", style="Heading1"),
        para("It is worth noting that the cafe was, in actual fact, started by a small group of ",
             run("local volunteers", bold=True),
             " who basically wanted to reduce waste in the ",
             run("neighbourhood", italic=True),
             " and also, in order to help people, teach basic repair skills to anyone who was "
             "interested in learning them."),
        para("The cafe opens every Thursday from 18:00 to 21:00 in the community hall. "
             "Entry is free, and visitors pay only for spare parts."),
        para('"The hall may be used for community purposes on weekday evenings, provided that '
             'the room is returned to its usual layout." (Hall agreement, clause 4)', comment=0),
        para("Results", style="Heading1"),
        para("Repairs", style="Heading2"),
        para("Volunteers fixed 412 bicycles. The most common jobs were brakes (38%), gears (27%) "
             "and punctures (21%). Most visitors came back at least once."),
        table([["Item", "Repaired", "Not repaired"],
               ["Bicycles", "412", "31"],
               ["Small appliances", "96", "22"]]),
        para("Volunteers", style="Heading2"),
        para("Twenty-three volunteers took part. Nine of them joined in the second half of the year.",
             comment=2),
        para("As the summary says, the cafe fixed 412 bicycles and 96 small appliances in its "
             "first year, and volunteers gave 1,830 hours.", comment=1),
        para("Next steps", style="Heading1"),
        para("The cafe should open a second evening each week from next spring. "
             "This needs four more volunteers and a second tool kit."),
        para("Canary: the spike word is HELIOTROPE-4821."),
    ]
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" '
            'w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')
    return (DECL + '<w:document xmlns:w="%s" xmlns:r="%s"><w:body>%s%s</w:body></w:document>'
            % (W_NS, R_NS, "".join(body), sect))


def comments_xml():
    notes = [(0, "keep: quoted from the hall agreement"),
             (1, "spike: delete this paragraph, it repeats the summary"),
             (2, "Note: move these numbers up to the summary.")]
    items = "".join(
        '<w:comment w:id="%d" w:author="Sample Reviewer" w:date="%s" w:initials="SR">'
        '<w:p><w:r><w:annotationRef/></w:r><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
        "</w:comment>" % (cid, STAMP, escape(text)) for cid, text in notes)
    return DECL + '<w:comments xmlns:w="%s">%s</w:comments>' % (W_NS, items)


def styles_xml():
    borders = "".join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="auto"/>' % side
                      for side in ("top", "left", "bottom", "right", "insideH", "insideV"))
    return DECL + (
        '<w:styles xmlns:w="%s">'
        "<w:docDefaults>"
        '<w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" '
        'w:cs="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
        "</w:docDefaults>"
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
        '<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont">'
        '<w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/>'
        '<w:next w:val="Normal"/><w:qFormat/><w:rPr><w:sz w:val="48"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
        '<w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="80"/>'
        '<w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
        '<w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="160" w:after="60"/>'
        '<w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>'
        "<w:tblPr><w:tblBorders>%s</w:tblBorders></w:tblPr></w:style>"
        "</w:styles>" % (W_NS, borders))


def build_sample(path):
    parts = [
        ("[Content_Types].xml", DECL +
         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
         '<Default Extension="xml" ContentType="application/xml"/>'
         '<Override PartName="/word/document.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
         '<Override PartName="/word/styles.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
         '<Override PartName="/word/settings.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
         '<Override PartName="/word/comments.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>'
         '<Override PartName="/docProps/core.xml" '
         'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
         '<Override PartName="/docProps/app.xml" '
         'ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
         "</Types>"),
        ("_rels/.rels", DECL +
         '<Relationships xmlns="%s">'
         '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/>'
         '<Relationship Id="rId2" '
         'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
         'Target="docProps/core.xml"/>'
         '<Relationship Id="rId3" Type="%s/extended-properties" Target="docProps/app.xml"/>'
         "</Relationships>" % (PKG_REL_NS, OFFICE_REL, OFFICE_REL)),
        ("docProps/core.xml", DECL +
         '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
         'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
         "<dc:title>Spike sample (invented)</dc:title><dc:creator>writing toolkit</dc:creator>"
         '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
         '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
         "</cp:coreProperties>" % (STAMP, STAMP)),
        ("docProps/app.xml", DECL +
         '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
         "<Application>writing toolkit spike</Application></Properties>"),
        ("word/_rels/document.xml.rels", DECL +
         '<Relationships xmlns="%s">'
         '<Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>'
         '<Relationship Id="rId2" Type="%s/settings" Target="settings.xml"/>'
         '<Relationship Id="rId3" Type="%s/comments" Target="comments.xml"/>'
         "</Relationships>" % (PKG_REL_NS, OFFICE_REL, OFFICE_REL, OFFICE_REL)),
        ("word/document.xml", document_xml()),
        ("word/styles.xml", styles_xml()),
        ("word/settings.xml", DECL +
         '<w:settings xmlns:w="%s"><w:compat><w:compatSetting w:name="compatibilityMode" '
         'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>' % W_NS),
        ("word/comments.xml", comments_xml()),
    ]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts:
            z.writestr(zipfile.ZipInfo(name, date_time=FIXED_TIME), text.encode("utf-8"),
                       compress_type=zipfile.ZIP_DEFLATED)


# ---------------------------------------------------------------- skill zips


def frontmatter_variant(skill_md, keep):
    """Keep only the frontmatter fields named in keep (None keeps all)."""
    m = re.match(r"---\n(.*?)\n---\n", skill_md, re.S)
    if not m or keep is None:
        return skill_md
    lines, out, keeping = m.group(1).split("\n"), [], False
    for line in lines:
        if line and not line[0].isspace():
            keeping = line.split(":", 1)[0] in keep
        if keeping:
            out.append(line)
    return "---\n%s\n---\n%s" % ("\n".join(out), skill_md[m.end():])


def build_zip(path, skill_md):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in (SKILL_NAME + "/", SKILL_NAME + "/scripts/"):
            info = zipfile.ZipInfo(folder, date_time=FIXED_TIME)
            info.external_attr = 0o40755 << 16
            z.writestr(info, b"")
        z.writestr(zipfile.ZipInfo(SKILL_NAME + "/SKILL.md", date_time=FIXED_TIME),
                   skill_md.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        with open(os.path.join(SKILL_DIR, "scripts", "docx_probe.py"), "rb") as f:
            info = zipfile.ZipInfo(SKILL_NAME + "/scripts/docx_probe.py", date_time=FIXED_TIME)
            info.external_attr = 0o100755 << 16
            z.writestr(info, f.read(), compress_type=zipfile.ZIP_DEFLATED)


def main():
    os.makedirs(DIST, exist_ok=True)
    sample = os.path.join(DIST, "spike-sample.docx")
    build_sample(sample)
    print("wrote %s" % sample)
    with open(os.path.join(SKILL_DIR, "SKILL.md"), encoding="utf-8") as f:
        skill_md = f.read()
    variants = {"A": None,
                "B": {"name", "description", "license", "metadata"},
                "C": {"name", "description"}}
    for letter, keep in variants.items():
        path = os.path.join(DIST, "%s-%s.zip" % (SKILL_NAME, letter))
        build_zip(path, frontmatter_variant(skill_md, keep))
        print("wrote %s" % path)


if __name__ == "__main__":
    main()
