# Profile reference

The profile is one page about you and your document. Every skill reads it before it does anything.
It is the only place for anything specific to your work.

Where it lives:

1. On claude.ai: in your Project's instructions. On a plan without Project instructions, add it to the Project's knowledge as a file.
2. In Claude Code: in doc-profile.md at the root of your repo.

doc-setup writes it for you after a short interview. You can also copy templates/doc-profile.md and fill it in by hand.
Two filled-in examples: samples/report/doc-profile.md and samples/thesis/doc-profile.md.

## Format

1. The first line after the title gives the toolkit version, for example `toolkit: 0.1`.
2. The profile has four parts: Document, Style guide, Thesis and Claude Code.
3. Document, Thesis and Claude Code hold `key: value` lines. A list is numbered, one item per line.
4. The style guide holds numbered rules in plain words. Each rule starts with a label, such as "Voice:". The skills find a rule by its label.
5. Leave out any part or field that does not apply. A report has no Thesis part. A profile on the web has no Claude Code part.
6. Keep it to one page, about 450 words, because it is read in every chat.

## Document

| Field | What it sets | Thesis default | Report default | Read by |
|---|---|---|---|---|
| mode | thesis or report; switches defaults and features | thesis | report | all skills |
| audience | who reads the document and what they need | examiners and researchers in the field | busy decision makers; many read only page one | all skills |
| key_message | the one sentence the reader must take away; a report adds the decision it asks for | no default: you write it | no default: you write it | doc-flow, doc-check; human-write through the map |
| opening | where the main message must appear | each chapter states its claim in its first paragraph | the first paragraph states the message and the decision needed | doc-flow, doc-check |
| parts | the chapters or sections in reading order (see below) | the chapters, from the files | the sections, from the headings | doc-flow, doc-check, notation-check |
| length | a length target for the whole document | none | the summary fits on one page | doc-flow, doc-check |
| keep | passages never rewritten (see below) | direct quotations | direct quotations; contract and legal text | human-write, doc-flow, notation-check |
| budget | auto, lean or standard (see below) | auto | auto | human-write, doc-flow |

### parts

One line per chapter or section, numbered as the reader sees them. After the name, you can add details, each after a "|":

| Detail | What it sets | Default |
|---|---|---|
| file | the source file, in Claude Code only | none |
| audience | an audience for this part only | the document's audience |
| length | a length target for this part only | none |
| paper | thesis only: none, submitted or published, for a chapter based on a paper | none |
| passes | thesis only: what may change in that chapter: none, light or full | light for a published paper, full otherwise |

Example: `3. A model of the return desk | file: ch3.tex | paper: published | passes: light`

human-write and doc-flow read paper and passes.
Use them only for a chapter that as a whole is based on a paper. If only one section comes from a paper, give the chapter no paper detail. Mark that section keep light in the file instead.

### keep

The keep list names passages that must never be rewritten. You can also mark a passage in the document itself:

| Where | Mark |
|---|---|
| Word | a comment on the passage that starts with "keep" |
| LaTeX | a line `% keep` before the passage and a line `% end keep` after it |
| Markdown | an HTML comment `keep` before the passage and an HTML comment `end keep` after it |

A reason may follow the mark after a colon, for example `% keep: quoted from the contract`.

Write "keep light" instead of "keep" to allow light passes only. A light pass fixes voice, spelling, dashes, number format and banned words, and nothing else. notation-check may also fix symbols in a keep light passage. Nothing changes in a keep passage.

### budget

| Value | What it does |
|---|---|
| lean | human-write reads the map, the section and the paragraph on either side. doc-flow's report is at most 600 words. |
| standard | human-write also reads the rest of the chapter. doc-flow's report is at most 1,200 words. |
| auto | standard for a thesis in Claude Code; lean everywhere else |

All other token rules hold at every budget. PLAN.md section 10 lists them.

## Style guide

| Label | Field | What it sets | Thesis default | Report default | Read by |
|---|---|---|---|---|---|
| Voice | voice | who speaks, and how others get credit | "I"; name others for their work | "we" for the organization | human-write, doc-check |
| Spelling | spelling | US or UK English | taken from the document | taken from the document | human-write, doc-check |
| Sentences | sentence_limit | the length in words after which a sentence needs a reason | 25 | 25 | human-write, doc-flow, doc-check |
| Words to cut | banned_words | words and phrases to cut | very, clearly, obviously, it is worth noting, novel | leverage, going forward, in order to, very, basically | human-write, doc-check |
| Dashes | dashes | the dash rule | no em dashes; ranges written "5 to 10" | the same | human-write, doc-check |
| Numbers | numbers | how numbers are written | digits with units (5 kg); counts from one to nine in words | one to nine in words, digits from 10; a thousands separator; the % sign | human-write, doc-check |
| House rules | house_rules | your own rules, from a supervisor, school or company | none | none | human-write, doc-flow, doc-check |

A number's format may change to meet the Numbers rule. Its value never changes, and neither does a number inside a keep passage.

## Thesis

Thesis mode only.

| Field | What it sets | Default | Read by |
|---|---|---|---|
| contribution | yes: a chapter based on a co-authored paper says who did what | yes | doc-flow, doc-check |
| notation_source | the chapter or table that sets the symbols | the symbol table | notation-check, human-write |
| define_symbols | each chapter or once: where each symbol must be defined | each chapter | notation-check |
| milestone | the next deadline or draft; used in full-check severity labels | you write it | doc-check |

## Claude Code

Claude Code only.

| Field | What it sets | Default | Read by |
|---|---|---|---|
| format | latex, markdown, word or text | detected from the files | all skills |
| notes_dir | where the map, plans, reports and symbol table go | doc-notes/ | all skills |
| commit | yes: commit each approved change; the skills never push | yes | all skills |
| protected_extra | your own LaTeX macros that must never change | none | human-write, doc-flow |
