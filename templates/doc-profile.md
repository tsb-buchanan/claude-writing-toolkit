<!--
Writing profile template for the writing toolkit.
doc-setup fills it in for you, after a short interview. You can also fill it in by hand.
Each comment says what a field does and gives its defaults. docs/profile-reference.md has the full detail.
Leave out any section or field that does not apply. Delete the comments when you are done, so the profile fits on one page.
-->
# Writing profile
<!-- The toolkit version this profile was written for. doc-setup offers to update an older profile. -->
toolkit: 1.0

## Document

<!-- thesis or report. It switches the defaults below and turns the thesis-only features on or off. -->
mode:

<!-- Who reads the document, and what they need from it.
Thesis default: examiners and researchers in the field. Report default: busy decision makers; many read only page one. -->
audience:

<!-- The one sentence the reader must take away. A report adds the decision it asks for. There is no default: you write it. -->
key_message:

<!-- Where the main message must appear.
Thesis default: each chapter states its claim in its first paragraph.
Report default: the first paragraph states the message and the decision needed. -->
opening:

<!-- The chapters (thesis) or sections (report) in reading order, one per line, numbered as the reader sees them.
After the name you can add details, each after a "|":
  file: the source file, in Claude Code only. Example: file: chapters/ch3.tex
  audience: an audience for this part only
  length: a length target for this part only
  paper: none, submitted or published, for a thesis chapter that as a whole is based on a paper
  passes: what may change in that chapter: none, light or full. Default for a published paper: light
Example: 3. A model of the return desk | file: ch3.tex | paper: published | passes: light
If only one section of a chapter comes from a paper, give the chapter no paper detail. Mark that section keep light in the file instead. -->
parts:
1.

<!-- A length target for the whole document, in words or pages.
Thesis default: none. Report default: the summary fits on one page. -->
length:

<!-- Passages that must never be rewritten, one per line.
You can also mark a passage in the document itself. Word: a comment on the passage that starts with "keep".
LaTeX: a line "% keep" before the passage and a line "% end keep" after it.
Markdown: an HTML comment "keep" before the passage and an HTML comment "end keep" after it.
Write "keep light" instead of "keep" to allow light fixes only: voice, spelling, dashes, number format and banned words.
Thesis default: direct quotations. Report default: direct quotations; contract and legal text. -->
keep:
1.

<!-- auto, lean or standard. auto means standard for a thesis in Claude Code, and lean everywhere else.
standard lets human-write read the whole chapter and doc-flow write a longer report. -->
budget: auto

## Style guide

<!-- Each rule starts with its label. The skills find a rule by its label. -->

<!-- Voice: who speaks, and how others get credit. The options are "I", "we", or no personal pronouns.
Thesis default: "I"; name others for their work. Report default: "we" for the organization. -->
1. Voice:

<!-- Spelling: US or UK English. Default: taken from the document. -->
2. Spelling:

<!-- Sentences: the length in words after which a sentence needs a reason. Default: 25. -->
3. Sentences: at most 25 words. A longer sentence needs a reason.

<!-- Words to cut, separated by commas.
Thesis default: very, clearly, obviously, it is worth noting, novel.
Report default: leverage, going forward, in order to, very, basically. -->
4. Words to cut:

<!-- Dashes: the dash rule. Default for both modes: no em dashes, and ranges written "5 to 10". -->
5. Dashes: no em dashes. Write ranges as "5 to 10".

<!-- Numbers: how numbers are written.
Thesis default: digits with units (5 kg); counts from one to nine in words.
Report default: one to nine in words, digits from 10; a thousands separator; the % sign. -->
6. Numbers:

<!-- House rules: your own rules, from a supervisor, a school or a company. One rule per sentence. Default: none. -->
7. House rules: none.

## Thesis

<!-- Thesis mode only. Leave this section out for a report. -->

<!-- yes or no. yes: a chapter based on a co-authored paper says who did what. Default: yes. -->
contribution: yes

<!-- The chapter that sets the symbols, or "the symbol table". Default: the symbol table. -->
notation_source: the symbol table

<!-- each chapter or once: define a symbol at its first use in each chapter, or once in the thesis. Default: each chapter. -->
define_symbols: each chapter

<!-- The next deadline or draft, for example "committee draft". doc-check full mode uses it in its severity labels. -->
milestone:

## Claude Code

<!-- Claude Code only. Leave this section out on the web. -->

<!-- latex, markdown, word or text. Default: detected from the files. -->
format:

<!-- Where the skills keep the map, plans, reports and symbol table. Default: doc-notes/ -->
notes_dir: doc-notes/

<!-- yes or no. yes: each approved change is committed. The skills never push. Default: yes. -->
commit: yes

<!-- Your own LaTeX macros that must never change, separated by commas. Default: none. -->
protected_extra: none
