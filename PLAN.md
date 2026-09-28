# PLAN

Status: approved on 28 September 2026. Nothing is built yet.
This plan replaces the earlier plan, which built slash commands for Claude Code only.

## 1. Goal

A small set of Claude Skills that help one writer turn a rough draft of a long document into a clear one.
The writer decides what the document says. The skills apply the writer's rules, fix structure and style, and catch what a tired eye misses.
Every skill shows its changes before anything is written.
Every skill works on claude.ai (web and desktop app) and in Claude Code.

The toolkit has four parts:

1. Five skills: doc-setup, human-write, doc-flow, doc-check and notation-check.
2. The profile: one page per writer, with their settings and style guide. It is the only place for anything specific to one writer.
3. The document map: one page per document (or per thesis chapter), written by doc-flow. Other skills read it instead of the whole document.
4. Docs: a web guide (a Word document), a Claude Code guide and a five-line README.

## 2. Users and modes

Two first users. One set of skills serves both.

1. A PhD student who writes a thesis: chapters, supervisor rules, notation, papers inside chapters. Works mostly in Claude Code, sometimes on the web. Can afford larger checks.
2. A business writer who writes reports on claude.ai. Not technical. Small token budget. Needs human-write, doc-flow and a light doc-check.

The profile setting `mode: thesis | report` switches defaults and turns thesis-only features on or off.

| | thesis | report |
|---|---|---|
| The parts are called | chapters | sections |
| notation-check | on | off |
| Papers inside chapters | on | off |
| doc-check full mode | suggested before a milestone | not suggested, still available on request |
| Token budget | standard in Claude Code, lean on the web | lean |
| Style and structure defaults | see section 7 | see section 7 |

## 3. How the pieces fit

The profile says how the writer wants to write. The map says what the document says. The skills read both.

A typical cycle:

1. doc-setup, once. The interview writes the profile.
2. doc-flow on the document (a thesis: one chapter at a time). Structure first, then the map.
3. human-write, one section per run.
4. doc-check quick before the document goes out. A thesis also gets notation-check and doc-check full before a milestone.

Where things live:

| Thing | Web (claude.ai) | Claude Code |
|---|---|---|
| Skills | uploaded once under Customize, Skills; a Team or Enterprise owner can add them for everyone | .claude/skills/ in the repo, or ~/.claude/skills/ |
| Profile | the Project's instructions | doc-profile.md at the repo root |
| Map | a file in the Project's knowledge | doc-notes/doc-map.md |
| The document | uploaded to the chat when a step needs it (Word or PDF), or pasted | files in the repo (LaTeX, Markdown, text or Word) |
| The writer's notes | the chat message, or comments in the Word file | doc-notes/notes.md, or comments in the source |
| Keep marks | a Word comment that starts with "keep" or "keep light" | `% keep` or `% keep light`, then `% end keep` (LaTeX); `<!-- keep -->` or `<!-- keep light -->`, then `<!-- end keep -->` (Markdown) |
| Plans and reports | the chat | doc-notes/plans/ and doc-notes/checks/ |
| Symbol table (thesis) | a file in the Project's knowledge | doc-notes/notation.md |
| Changes | a Word file with tracked changes | a diff, then the file, then a commit |

The profile and the map belong in the Project: every chat needs them, and they are short.
The document itself does not. A copy there goes out of date after each round of changes, and everything in the Project's knowledge is read in every chat.
Instead, the writer uploads the current version to each chat that needs it.

## 4. Repo layout

```
claude-writing-toolkit/
  README.md                     five lines: what it is, how to start
  CLAUDE.md
  PLAN.md
  LICENSE
  skills/                       what users install
    doc-setup/
      SKILL.md
      profile-template.md       read when the profile is written (copy of templates/doc-profile.md)
      thesis-questions.md       extra interview questions, read in thesis mode only
      project-instructions.md   copy of the template of the same name
      claude-md-snippet.md      copy of the template of the same name
    human-write/
      SKILL.md
      word-output.md            how to return tracked changes; read only for Word output
      scripts/                  copies of shared/ scripts
    doc-flow/
      SKILL.md
      map-template.md
      word-output.md
      scripts/
    doc-check/
      SKILL.md                  quick mode
      full-mode.md              read only in full mode
      scripts/
    notation-check/
      SKILL.md
      scripts/symbols.py        lists every symbol in the math, with place and context
  shared/                       the one source for files that several skills need
    docx_tool.py                reads Word files and writes tracked changes
    check_protected.py          compares numbers, citations and math before and after
    doc_stats.py                words, long sentences, banned words and dashes per section
    word-output.md
  templates/
    doc-profile.md              blank profile with a comment on every field
    doc-map.md                  the map format, with an invented example
    project-instructions.md     what to paste into a Claude Project
    claude-md-snippet.md        two lines for the writer's own CLAUDE.md
  docs/
    web-guide.md                source of the Word guide; each release builds web-guide.docx
    claude-code-guide.md
    profile-reference.md        every field, its defaults per mode, which skills read it
  samples/
    report/                     source.md, planted.md and doc-profile.md; built/ holds report.md, .docx and .pdf
    thesis/                     the LaTeX chapter, a stub of the chapter before it, refs.bib, planted.md and
                                doc-profile.md; built/ holds thesis.pdf
  tests/
    expected/                   what each skill must find, change and leave alone, per sample
    results/                    one file per release test
    test_docx_tool.py
    test_check_protected.py
    test_doc_stats.py
    test_symbols.py
  tools/
    build_samples.py            builds samples/*/built/ from the sources (PDFs need LibreOffice and LaTeX)
    sync_shared.py              copies shared/ files and templates into the skills that use them; --check fails if a copy differs
    check_repo.py               dash check, SKILL.md size and frontmatter, copies in sync
    build_release.py            one zip per skill, one zip with all skills, the Word guide
  .github/workflows/
    checks.yml                  runs check_repo.py and the tests on every push
    release.yml                 on a version tag, builds the release files and attaches them
```

What a Claude Code writer's repo holds after setup:

```
<writer's repo>/
  doc-profile.md                fixed path, so every skill finds it
  CLAUDE.md                     two lines point to the profile (added after approval)
  .claude/skills/               the skills, unless installed in ~/.claude/skills/
  doc-notes/
    doc-map.md
    notes.md                    optional: the writer's own notes, one heading per part
    notation.md                 thesis mode
    plans/                      doc-flow reports and approved outlines
    checks/                     doc-check reports
    drafts/                     temporary copies; emptied after each decision
```

## 5. Rules every skill follows

1. Read the profile first. If there is none, offer doc-setup, or continue with the defaults for the mode the writer names.
2. The writer's own notes, outline and keep marks win over the skill's suggestions. A conflict is reported, never settled silently.
3. Show first. Write only after approval. On the web the approval is in Word (tracked changes). In Claude Code it is a reply to a diff.
4. Never change the value of a number, a fact, a citation, an equation, a cross-reference or a quotation. Only notation-check may change symbols inside equations.
5. Never add a claim, result or citation that is not in the document or the writer's notes. Every new sentence starts with [NEW].
6. Never rewrite a keep passage. A keep light passage gets light passes only: voice, spelling, dashes, number format and banned words.
7. Stay in scope. Flag work that belongs to another skill or another part of the document. Do not do it.
8. Check every change before showing it: protected content with check_protected.py, dashes and banned words with doc_stats.py.
9. Keep the output within the caps in section 10.
10. A read-only skill says so in its first line.
11. Claude Code: one commit per run that writes files, unless the profile says `commit: no`. Never push.

## 6. The skills

Each skill is a folder with a SKILL.md: a short description (what it does and when to use it) and the instructions.
On the web, Claude picks a skill when the request matches its description, or when the writer names it: "Use human-write on section 3."
In Claude Code, the writer can also type the name: `/human-write chapters/ch3.tex "3.2"`.

### 6.1 doc-setup

Job: interview the writer and write their one-page profile (settings and style guide).

Input:

1. Web: the chat. Optionally the document, uploaded, so the skill can propose values.
2. Claude Code: the chat and the repo. It looks for the main file, the chapter files and the source format before it asks.

The interview has at most three rounds. Every question has a default. "OK" accepts all defaults in a round.

1. The document: mode; who reads it and what they need; the key message in one sentence; the sections or chapters (proposed from the document when there is one).
2. Style: voice, spelling, sentence limit, banned words, dash rule, number format. The skill shows the mode's defaults and the writer changes only what differs. Each voice option comes with a one-line example.
3. Limits: passages that must not be rewritten; house rules (supervisor, school or company rules); length target. Thesis mode adds: which chapters are papers and what may change in them, the notation source, and the next milestone. These questions sit in thesis-questions.md, so report runs never load them.

Output: the profile, shown in full. The writer approves it or edits it.

| | Web | Claude Code |
|---|---|---|
| Output | the profile as one block to copy, and the same text as a file | doc-profile.md at the repo root, written after approval |
| Then | the writer pastes it into the Project's instructions (three steps shown); on a plan without Project instructions, the file goes into the Project's knowledge | the skill offers two lines for the writer's CLAUDE.md, adds them after approval, and commits |

Rules:

1. Look before asking. Propose values from the document or the repo.
2. Never copy document text into the profile, except the headings and the key message.
3. The profile fits on one page, about 450 words. Fields that do not apply to the mode are left out.
4. A rerun reads the current profile, asks what to change and shows a diff.
5. If the profile comes from an older toolkit version, offer to add the new fields.
6. Use only the headings and a two-page sample of the document. On the web, an upload puts the whole text in the context anyway, so the upload is optional: the writer can type the section names instead.

### 6.2 human-write

Job: rewrite one section to the profile's style.

Input:

1. Web: an uploaded Word file and the section's heading or number. A PDF or pasted text also works. Optional notes in the message.
2. Claude Code: a file and a section heading or line range. Optional notes.
3. Optional in both: "light", which fixes only rule breaches (banned words, dashes, number format, voice, spelling) and leaves the sentences otherwise alone.

Reads: the profile, the map, the target section, and the paragraph before and after it. With the standard budget it also reads the rest of the chapter. It never reads the whole document with a tool. (On the web, the upload itself puts the whole text in the context; see 10.4.) Without a map, it works from the section alone and suggests "doc-flow map only".

Rules:

1. Lead each paragraph with its claim.
2. Short sentences by default. A sentence over the profile's limit (default 25 words) needs a reason, and the reason is listed.
3. Cut filler words and the profile's banned words.
4. No recaps or signposting inside the section.
5. Never change numbers, facts, citations or equations. The format of a number may change to meet the profile's number rule. Its value never changes.
6. Never invent claims, results or citations. A new sentence may only restate what the section or the map already says, and it starts with [NEW].
7. Never rewrite a keep passage. A keep light passage, or a chapter based on a paper, gets only the passes it allows.
8. Follow the profile's voice, spelling, dash rule and house rules.
9. Use the map's key terms. A symbol that differs from the notation table is flagged for notation-check, not changed.
10. Material that belongs elsewhere is flagged for doc-flow, not moved.
11. One section per run. A request for more gets the first section and a note to start a new chat for the next one.
12. Before showing anything, run check_protected.py and doc_stats.py on the result. Fix every difference, or list it.

Output, in both places: the rewrite with its [NEW] marks, then these lists. One line per item. Empty lists are left out.

1. Number changes: old and new form, and where.
2. Removed sentences, and where their content went.
3. Sentences whose meaning could have shifted: old and new, side by side.
4. Long sentences kept: word count and reason.
5. Flags for other skills.

| | Web | Claude Code |
|---|---|---|
| Shows | a copy of the Word file with the rewrite as tracked changes (author "Claude"); the lists in the chat | a diff of a draft copy, and the lists |
| Approval | the writer accepts or rejects each change in Word; their own file does not change until they do | "approve", "approve except 2 and 5", or edits |
| Writes | nothing else | after approval: the file, then one commit |
| PDF or pasted text | a new Word file with the original section and the changes tracked | the skill works on the files in the repo |
| A Word file in the repo | as above | a copy next to it with tracked changes; the original stays until the writer replaces it |

Paragraphs the script cannot edit safely (equations, fields, footnotes, existing tracked changes) stay as they are. Their proposed text goes into the chat instead.

### 6.3 doc-flow

Job: review the structure of one report or one thesis chapter, apply approved structural moves, and write the map.

Input:

1. Web: an uploaded Word file (or a PDF, or pasted text). The writer's notes in the message or as Word comments. Their own outline, if they have one.
2. Claude Code: a file. Notes from doc-notes/notes.md and from comments in the source.

Reads: the profile, the whole document or chapter, the writer's notes and the current map.

Stage 1, the report. Then stop.

1. Main message: quoted, with its place. Is it stated as early as the profile's opening rule asks?
2. One line per section: its job, and whether it moves toward the main message.
3. Repetition: where, and which place should keep the material.
4. Broken handoffs between sections.
5. Material in the wrong place. Material that belongs in another chapter is flagged, never moved there.
6. Where to condense, with the words each cut saves. Current length against the target.
7. Long-sentence rate per section, from doc_stats.py.
8. The writer's notes: applied, or why not. The notes win over the skill's own suggestions.
9. The proposed outline, and a numbered list of moves: reorder, merge, cut a duplicate, add a heading.

Stage 2, after the writer approves all moves or some of them: apply only structural moves. No sentence is rewritten. A new heading gets no body text. The facts in a cut duplicate must survive elsewhere, and check_protected.py confirms it. Every removed passage is listed with where its content went.

Stage 3: write the map (section 8). "doc-flow map only" skips stages 1 and 2. It reads the document and writes the map. This is the cheap way to give human-write a map.

| | Web | Claude Code |
|---|---|---|
| Stage 1 | the report in the chat | the report in the chat, saved in doc-notes/plans/ |
| Stage 2 | a copy of the Word file with the moves as tracked changes (a move shows as a deletion and an insertion) | a draft copy, a diff that marks moved lines, a second approval, then the file |
| Map | a doc-map.md file to download and add to the Project's knowledge | doc-notes/doc-map.md |
| Commit | none | one commit for the plan, the moves and the map |

### 6.4 doc-check

Read-only. It never changes the document. It has two modes.

Quick mode is the default. Both users, web and Claude Code.

1. Input: the whole document, or one chapter.
2. Reads: the profile, the map and the document. One pass. No subagents.
3. The checklist is fixed:
   1. The main message is clear and up front.
   2. Numbers agree across sections, and with the map.
   3. Terms are used the same way throughout.
   4. Claims that need a source and have none.
   5. The length suits the audience and the target.
   6. The profile's style rules: sentence limit, banned words, dashes, number format, voice, leftover [NEW] marks. doc_stats.py counts these.
4. Output: the top 10 issues only, most important first. Each gives the section, the words it is about (a short quote), why it matters in one line, and a next step: a skill to run or a decision for the writer. One more line gives the count of smaller issues not shown.

| | Web | Claude Code |
|---|---|---|
| Quick output | the list in the chat | the list in the chat, saved as doc-notes/checks/<date>-quick.md, one commit |
| Full mode | not available; says it needs Claude Code and offers quick mode | available |

Full mode is for Claude Code, thesis users and a large budget. It states its estimated cost and asks before it starts. Its instructions sit in full-mode.md, so quick runs never load them. The skill runs in the main conversation (not as a forked skill), because the main conversation launches the subagents.

1. Extract: one subagent per chapter, on Sonnet. Each returns the chapter's claim, one line per section, key numbers, terms, symbols, citations and handoffs.
2. Review: one subagent per check dimension: message, structure and handoffs, repetition, numbers, terms, notation (thesis mode only), claims and sources, style and voice, house rules.
3. Verify: subagents that try to disprove each finding by reading the cited lines. Each verifier takes up to five findings from one chapter. Only findings that survive reach the report. Rejected findings get one line each.
4. Report: saved as doc-notes/checks/<date>-full.md. A summary of at most five lines. Findings grouped by severity: blocking before the milestone, major, minor. Each has its place, its evidence and a next step. A comparison with the previous full report: new, fixed, still open.
5. The chat shows the summary and the blocking findings. The file holds the rest.

### 6.5 notation-check

Thesis mode only. In report mode it says so and stops.

Job: keep symbols consistent across chapters.

Input:

1. Claude Code: the chapter files named in the profile, or one chapter.
2. Web: uploaded LaTeX or Markdown files. A PDF gives a report only, with lower accuracy.

Stage 1: symbols.py lists every symbol in the math with file, line and the sentence around its first use. Claude reads that list, not the whole thesis. It builds or updates the symbol table: symbol, meaning, where it is defined, variants.

Stage 2, the report. Then stop.

1. Variants: one quantity, several symbols.
2. Clashes: one symbol, several meanings.
3. Symbols used before they are defined, under the profile's rule (in each chapter, or once per thesis).
4. Numbered fixes. The profile's notation source decides. Where it is silent, the skill proposes a convention and marks it as the writer's decision.

Stage 3: apply approved fixes only. This is the only skill that may change symbols inside equations. It changes nothing else. It may fix symbols in a keep light passage, but never in a keep passage.

| | Web | Claude Code |
|---|---|---|
| Symbol table | a notation.md file to download and add to the Project's knowledge | doc-notes/notation.md |
| Fixes | corrected copies of the uploaded LaTeX or Markdown files, and the list; symbols inside Word equations are listed for the writer to change by hand | a draft copy, a diff, approval, the files, one commit |

## 7. The profile, field by field

The profile is one Markdown page of about 450 words at most. doc-setup writes it. It has two parts:

1. Document: settings, one `key: value` line each.
2. Style guide: numbered rules in plain words, so that the writer and Claude can both read them. In a Project, they also guide any text Claude drafts there.

The written profile has no comments, to stay short. docs/profile-reference.md explains every field. The first line gives the toolkit version. Fields that do not apply to the mode or the place are left out.

Document:

| Field | What it sets | Thesis default | Report default | Read by |
|---|---|---|---|---|
| mode | defaults and features | thesis | report | all |
| audience | who reads it and what they need | examiners and researchers in the field | busy decision makers; many read only page one | all |
| key_message | the one sentence the reader must take away; a report adds the decision it asks for | asked | asked | doc-flow, doc-check; human-write through the map |
| opening | where the main message must appear | each chapter states its claim in its first paragraph | the first paragraph states the message and the decision needed | doc-flow, doc-check |
| parts | chapters or sections in reading order; per part, optional: file (Claude Code), audience, length, paper and passes (thesis) | chapters, from the files | sections, from the headings | doc-flow, doc-check, notation-check |
| length | length target | none | summary on one page | doc-flow, doc-check |
| keep | passages never rewritten, besides keep and keep light marks in the text | quotations | quotations; legal and policy text | human-write, doc-flow, notation-check |
| budget | auto, lean or standard (section 10) | auto: standard in Claude Code, lean on the web | auto: lean | human-write, doc-flow |

Style guide:

| Field | What it sets | Thesis default | Report default | Read by |
|---|---|---|---|---|
| voice | who speaks, and how others get credit | "I"; others named for their work | "we" for the organization | human-write, doc-check |
| spelling | US or UK English | taken from the document | taken from the document | human-write, doc-check |
| sentence_limit | the length in words after which a sentence needs a reason | 25 | 25 | human-write, doc-flow, doc-check |
| banned_words | words to cut | short list of academic filler ("very", "clearly", "it is worth noting") | short list of business filler ("leverage", "going forward", "in order to") | human-write, doc-check |
| dashes | the dash rule | no em dashes; ranges written "5 to 10" | same | human-write, doc-check |
| numbers | how numbers are written | digits with units ("5 kg"); counts from one to nine in words | one to nine in words, digits from 10; a thousands separator; the % sign | human-write, doc-check |
| house_rules | the writer's own rules: supervisor, school or company | none | none | human-write, doc-flow, doc-check |

Thesis only:

| Field | What it sets | Thesis default | Read by |
|---|---|---|---|
| paper and passes (per chapter in parts) | whether a chapter is based on a paper (none, submitted, published) and what may change in it (none, light, full) | published: light; submitted or none: full | human-write, doc-flow |
| contribution | chapters based on co-authored papers say who did what | yes | doc-flow, doc-check |
| notation_source | the chapter or table that sets the symbols | the symbol table | notation-check, human-write |
| define_symbols | define each symbol at first use in each chapter, or once in the thesis | each chapter | notation-check |
| milestone | the next deadline; used in full-check severity labels | asked | doc-check |

Claude Code only:

| Field | What it sets | Default | Read by |
|---|---|---|---|
| format | latex, markdown, word or text | detected | all |
| notes_dir | where the map, plans, reports and symbol table go | doc-notes/ | all |
| commit | commit after each approved write | yes | all |
| protected_extra | the writer's own macros that must never change | none | human-write, doc-flow |

## 8. The document map

doc-flow writes the map. human-write and doc-check read it. No other skill changes it.

It holds:

1. The date it was written.
2. The main message.
3. For each section (a thesis: each chapter, then its sections): the heading and one line on its job.
4. Key numbers: the value, what it is, and where it appears.
5. Key terms: the term to use, and the variants to avoid. doc-check's terms check needs them.

The cap is one page for a report, and one page per chapter for a thesis.
If the headings in the document no longer match the map, human-write says so and suggests "doc-flow map only".

## 9. Scripts

Scripts do the mechanical work, so Claude reads less and the results are exact.
They use only the Python standard library and make no network calls.
Their code never enters Claude's context. Claude runs them and reads their short output.
The same SKILL.md text finds them in both places: on claude.ai the skill folder is copied into the sandbox; in Claude Code the path is `${CLAUDE_SKILL_DIR}/scripts/`.

1. docx_tool.py (human-write, doc-flow, doc-check):
   1. `outline`: the headings, with paragraph numbers.
   2. `read`: the paragraphs of one section (or all), numbered, with flags for equations, fields, footnotes, comments and tracked changes. Word comments come out as notes and keep marks.
   3. `apply`: takes a list of changes by paragraph number (replace, delete, insert, move, add heading) and writes them as tracked changes into a copy. Inside a replaced paragraph, only the changed words are marked. Everything else in the file stays byte for byte the same. It refuses a paragraph it cannot edit safely, and says why.
   4. `from-text`: builds a plain Word file from pasted or PDF text, so changes can be tracked against it.
2. check_protected.py (human-write, doc-flow): compares text before and after. It reports any change to number values, citation keys, math, cross-references, labels, links and quotations. A number from a cut passage must appear elsewhere, or be listed.
3. doc_stats.py (human-write, doc-flow, doc-check): words per section, sentences over the limit, banned words and dashes, for Word, LaTeX, Markdown and plain text.
4. symbols.py (notation-check only): every symbol in LaTeX or Markdown math, with file, line and context.

Real Word files are messy. The first version edits plain paragraphs and headings only. Tables, text boxes and paragraphs with equations or fields stay as they are, and the proposal goes into the chat.

Why our own Word script: Anthropic's built-in docx skill can also write tracked changes, but Claude then reads and writes the raw Word XML. That XML is several times longer than the text, and writing it is output, the most expensive kind of token. Our script takes plain text and paragraph numbers instead. On the web, the built-in skill stays a fallback for a paragraph our script refuses, at a higher token cost. Its license forbids copying, so the toolkit never copies or adapts its code.

## 10. Token budget and cost

### 10.1 Budget rules

The budget setting is `lean` or `standard`. The default (`auto`) is lean in report mode and on the web, and standard for a thesis in Claude Code. Standard changes two things only: human-write also reads the rest of the chapter, and doc-flow may write a longer report.

1. No subagents, except in doc-check full mode.
2. One section per human-write run.
3. human-write reads the map, the section and the paragraph on either side, never the whole document. On the web, the upload still puts the whole text in the context (10.4).
4. Outputs are capped (10.2).
5. Each SKILL.md is at most 900 words, about 1,500 tokens. Each description is under 200 characters, the limit claude.ai's help pages give. That also matters for cost: every installed skill's description is read in every chat. Detail that only some runs need sits in a separate file in the skill folder.
6. Scripts do the mechanical work. Their code is never read into the context.
7. On the web, each step starts a new chat. The profile and the map carry what the next step needs.
8. The document is uploaded to the chat that needs it. It never goes into the Project's knowledge.
9. No chat preview repeats what the Word file already shows. Empty lists are left out.
10. Writers install only the skills they use. A business writer skips notation-check.
11. On the web, the uploaded text is already in the context. Skills get paragraph numbers from `docx_tool.py outline`, and never read the whole file a second time.

### 10.2 Output caps

| Skill | Cap |
|---|---|
| doc-setup | three question rounds; the profile on one page (about 450 words) |
| human-write | one section; one line per list item; at most 100 words of other chat text |
| doc-flow | report at most 600 words (lean) or 1,200 words (standard); map on one page |
| doc-check quick | 10 issues, about 40 words each |
| doc-check full | in the chat: the summary and the blocking findings; the rest in the file |
| notation-check | report on one page in the chat; the full symbol table in a file |

### 10.3 Models

1. Sonnet by default, for every skill.
2. Opus for important documents (a final version, a board report, a thesis introduction or conclusion) and for doc-check full mode.
3. Extended thinking only for doc-flow on important documents and for full checks. Thinking is billed as output, the most expensive kind of token.
4. In full mode, the extraction subagents run on Sonnet even when the session runs on Opus.

### 10.4 Cost of one typical round

The round: doc-flow, then human-write on three sections, then doc-check quick.

Assumptions:

1. A report of 6,000 words (about 12 pages) in six sections of 1,000 words. With current models one word is about 1.7 tokens, so the report is about 10,000 tokens.
2. The web, with one new chat per step. The profile sits in the Project's instructions, the map in its knowledge. The writer uploads the current Word file to each chat, and claude.ai puts its whole text into the context (the spike confirmed this).
3. Only the toolkit's own tokens count: skill descriptions, SKILL.md, profile, map, document and output. The fixed overhead of claude.ai or Claude Code is left out.
4. Each tool call re-reads the chat so far. These re-reads come from the prompt cache, at a tenth of the normal input price or less.
5. Light thinking: about 1,000 to 2,000 tokens per step.
6. API list prices on 28 September 2026, in US dollars per million tokens. Sonnet: 2 input, 10 output. Opus: 4 input, 20 output. Cache reads: 0.20 for both.

| Step | New input | Cached re-reads | Output |
|---|---|---|---|
| doc-flow: report, moves, map | 13,000 | 75,000 | 4,000 |
| human-write, three sections | 48,000 | 165,000 | 10,500 |
| doc-check quick | 14,000 | 15,000 | 2,500 |
| Total | 75,000 | 255,000 | 17,000 |

Result: about $0.40 per round on Sonnet, and about $0.70 on Opus.

Notes:

1. Output is about half of the cost. That is why the skills cap their output and never repeat in the chat what the Word file shows.
2. The upload is the other large item. Each human-write run reads the whole report (10,000 tokens here), because claude.ai puts the upload's text into the context. For a long document, the writer can copy the section into a new Word file and upload only that. human-write then returns the tracked changes in that small file.
3. The same round on a 10,000-word thesis chapter in Claude Code, with the standard budget: about $0.60 on Sonnet and $1.10 on Opus. Claude Code's own overhead comes on top. The spike measured about $0.11 per short session on Sonnet, mostly cached reads of Claude Code's own instructions. That makes about $0.50 per round on Sonnet, and somewhat more on Opus.
4. doc-check full mode on a 70,000-word thesis: roughly $3.50 on Sonnet and $5.50 on Opus (with extraction on Sonnet).
5. On a claude.ai subscription the writer pays a fixed fee. The same tokens count against the plan's usage limits, so the same savings apply. claude.ai, the desktop app and Claude Code share one limit. Long chats, large files and file creation use it faster. Anthropic's own advice is to start a new chat when a chat gets long.

## 11. Test plan

Two invented samples, written for this repo. Never a real user document. They are short, so a full test round stays cheap. tools/build_samples.py builds their Word, Markdown and PDF files, and each sample holds the profile the tests use.

1. A report of about 1,800 words in six sections, for a fictional organization. Formats: Word (main), PDF and Markdown.
2. A thesis chapter in LaTeX, on an invented model: about 1,000 words of prose plus equations, with its PDF. A half-page stub of the chapter before it, so notation-check has a second chapter to compare.

Each sample has planted.md, which lists every planted problem, where it is and what is right.

1. Report: the main message buried at the end; two numbers that differ between sections; one concept under two names; a repeated paragraph; filler and banned words; sentences over 25 words; a recap and a signpost; a broken handoff; a result in the method section; a claim without a source; an em dash; number format slips; a voice slip; a quoted clause marked keep; a Word comment whose note goes against what doc-flow would suggest; a table and a footnote the script must leave alone.
2. Chapter: the chapter's claim only at the end; a symbol variant; a symbol clash; a symbol used before its definition; an equation, a citation and a cross-reference inside text that needs rewriting; a section from a published paper, marked keep light; voice slips; a repeated paragraph; a broken handoff; a result in the method section; an en dash range; a broken house rule; a number format slip; a claim without a source; and a false alarm: two terms that look inconsistent but name two different things.

tests/expected/ says, per skill and sample, what the skill must find, what it must change and what it must leave alone.

Pass criteria:

1. doc-setup: finishes in three rounds or fewer; the profile fits on one page; report mode leaves out thesis fields; a rerun shows a diff.
2. human-write: fixes every planted style problem in the section; check_protected.py finds no change to numbers, citations, equations, cross-references or keep passages; every new sentence has [NEW]; every list is complete against planted.md; the Word file opens in Word and LibreOffice and shows tracked changes; nothing outside the section changes; in Claude Code, nothing is written before approval.
3. doc-flow: finds the buried message, the repetition, the broken handoff and the misplaced result; follows the writer's note over its own suggestion; applies only structural moves; loses no fact; the map fits on one page and has the right key numbers.
4. doc-check quick: finds at least 80% of the issues that tests/expected lists for its checklist; shows no more than 10; changes nothing.
5. doc-check full: finds every planted problem; rejects the false alarm; compares correctly with an earlier report.
6. notation-check: finds the variant, the clash and the symbol used before its definition; changes only approved symbols and nothing outside the math; stops in report mode.

How and where:

1. Every skill runs on the web (claude.ai, Sonnet) and in Claude Code (Sonnet). Full mode also runs on Opus. Each test starts a new chat or session.
2. Tokens: measure each step in Claude Code and compare with section 10.4. A step more than 50% over its estimate is a bug to fix before release.
3. Automatic checks run on every push: dashes, SKILL.md size and frontmatter, shared copies in sync, unit tests for the scripts.
4. Results go in tests/results/<version>.md: one line per skill and place, pass or fail, with notes. A release needs every line to pass.
5. After any change to a SKILL.md or a script, rerun that skill's tests.

## 12. Docs

1. The web guide: a Word document for a non-technical reader. The text lives in docs/web-guide.md. Each release builds web-guide.docx from it and attaches it. Each screenshot place is a line of its own, like "[Screenshot 4: the Skills page, with the upload button circled]". Parts:
   1. What you need: a claude.ai account with code execution turned on. It is on by default, and skills work on every plan.
   2. Install the skills: download the zips and upload them.
   3. Make a Project for your document.
   4. Run doc-setup. Paste the profile into the Project's instructions.
   5. Fix the structure with doc-flow. Review the tracked changes in Word. Add the map to the Project.
   6. Rewrite one section at a time with human-write.
   7. Check with doc-check before you send.
   8. Save tokens: a new chat per step, Sonnet by default, one section at a time, the document never in the Project. For a long document, upload only the section you are working on.
   9. What the skills never do.
   10. When something goes wrong.
2. The Claude Code guide (docs/claude-code-guide.md): install, /doc-setup, the cycle, the files in doc-notes/, approvals and commits, models and cost, full mode, troubleshooting.
3. The profile reference (docs/profile-reference.md): every field, its defaults per mode, and which skills read it.
4. The README, five lines: what the toolkit is, who it is for, how to start on the web, how to start in Claude Code, and the license.

## 13. Distribution

1. GitHub Releases. A version tag (for example v0.1.0) starts release.yml. It builds:
   1. One zip per skill, for claude.ai. Each holds one skill folder, named exactly like the skill, with its SKILL.md inside.
   2. One zip with all five skills, for Claude Code.
   3. web-guide.docx.
2. Web install: upload each zip under Customize, Skills. A Team or Enterprise owner can upload them once in the organization settings, and they are then on for everyone.
3. Claude Code install: unzip into .claude/skills/ in the repo, or into ~/.claude/skills/ for all projects. A writer who uploaded the skills on claude.ai may already have them: Claude Code signed in with the same account syncs them, with the prefix `anthropic-skills:` (seen in the spike). The guide says to install in one place only, so there are never two copies with different names.
4. Later, a Claude Code plugin from this repo: add .claude-plugin/plugin.json and a marketplace file. Writers run `/plugin marketplace add <owner>/<repo>` and then `/plugin install`. The skills are then named like `/<plugin>:human-write`. The profile stays in the writer's repo, so the switch needs no profile change.
5. Versions: each SKILL.md carries the toolkit version in its metadata, and so does the profile. claude.ai shows that version on the skill's page. doc-setup offers to update an older profile.

## 14. Build order

1. Spike, one day at most, in spike/. Done on 28 September 2026: every check passed, and the results are in spike/RESULTS.md. Build a tiny test skill with a script. Upload it to claude.ai and install it in Claude Code. Delete the folder once the shared scripts exist. Confirm:
   1. which frontmatter fields claude.ai accepts besides name and description (we need one for the version);
   2. that a bundled script runs on claude.ai and returns a Word file to download;
   3. whether an uploaded Word file's whole text enters the context (this changes 10.4);
   4. that the uploaded Word file itself reaches the sandbox, so the script can read it and its comments;
   5. that tracked changes written by the script open cleanly in Word and LibreOffice.
2. The samples, planted.md and expected results. The profile template and the profile reference. Done on 28 September 2026.
3. doc-setup. Done on 28 September 2026: it passed in Claude Code on both samples (tests/results/0.1-dev.md). The claude.ai run waits for the release test.
4. The shared scripts and their unit tests.
5. human-write. Test it on both samples, on the web and in Claude Code.
6. doc-flow and the map. Test human-write again, now with a map.
7. doc-check quick.
8. The web guide and the README. Release v0.1 with doc-setup, human-write, doc-flow and doc-check quick. That is all the business writer needs.
9. doc-check full mode.
10. notation-check.
11. The Claude Code guide, a full release test, and release v1.0.
12. Later: the plugin.

## 15. Decisions

Decided on 28 September 2026:

1. Approval on the web: the tracked-changes Word file is the approval step. The writer accepts or rejects each change in Word, and their own file does not change until they do. No preview in the chat first, because that would cost about twice the output tokens of a human-write run.
2. The budget setting stays visible: `budget` (auto, lean, standard) in the profile. "Lean by default for reports and on the web" is one switch the writer can see and change.
3. Verifiers in full mode take up to five findings each, from one chapter. One verifier per finding would be stricter, but it would cost about twice as much for that stage.
4. The repo is renamed claude-writing-toolkit, because the toolkit serves reports as well as theses. GitHub redirects the old name.

## 16. Later

1. The Claude Code plugin.
2. Reviewer responses: turn reviewer comments into a response table, and apply approved changes under human-write's rules.
3. A citation check: every citation resolves, and every claim that needs a source has one.
4. A figure and table check: every figure is referenced in the text and has a caption that stands alone.
5. [NEW] marks as Word comments instead of text.
6. Languages other than English.
