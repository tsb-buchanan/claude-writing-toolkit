# PLAN

Status: draft for approval. Nothing is built yet.

## 1. Goal

A toolkit that helps one writer take a long document from a rough draft to a clean draft with Claude Code.
The writer decides what the document says. The tools apply the writer's decisions and catch what a human eye misses across many pages: a symbol that drifts, a paragraph said twice, a broken handoff, a pronoun that breaks the voice rule.
Every tool shows its changes before it writes them.

The toolkit has four parts:

1. Commands: four slash commands, plus a setup command.
2. A profile: project_profile.md, the one file that holds everything specific to one project.
3. Templates: the working notes the commands read and write.
4. Docs: a tutorial that walks a writer through a full editing cycle.

## 2. Repo layout

```
claude-thesis-toolkit/
  CLAUDE.md
  PLAN.md
  README.md                  what this is, install in five steps, link to the tutorial
  LICENSE
  commands/
    doc_check.md             whole-document read-only check (generic thesis_check)
    notation_check.md        notation table, report, approved replacements
    chapter_flow.md          one unit: flow report, plan, structural moves
    human_write.md           one section: strict rewrite pass
    setup_profile.md         interview that writes or updates the profile
  templates/
    project_profile.md       the profile, every field with a one-line comment
    writing_style.md         default style guide, with three voice variants
    reading_notes.md         one heading per unit, one note per line
    message_map.md           the document's claim and each unit's job
    notation_table.md        one row per quantity
    decisions_log.md         dated decisions the commands must respect
    session_log.md           one entry per command run that writes a file
    claude_md_snippet.md     lines to add to the user's own CLAUDE.md
  setup/
    SETUP_PROMPT.md          paste-in prompt: install files, then run the interview
  docs/
    tutorial.md              the full editing cycle, step by step
    install.md               manual install and update
    profile_reference.md     every profile field, its effect, and which commands read it
    customizing.md           how to add a mark, a rule or a check without editing commands
  examples/
    sample_doc/              a short invented document for testing the commands
```

What goes into the user's repo after setup (default paths, all set in the profile):

```
<user repo>/
  project_profile.md         fixed path, so every command can find it
  CLAUDE.md                  gets the snippet appended
  .claude/commands/*.md      the five commands
  notes/
    writing_style.md
    reading_notes.md
    message_map.md
    notation_table.md
    decisions_log.md
    session_log.md
    plans/                   approved chapter_flow plans
    checks/                  doc_check reports
```

The profile sits at a fixed path (the repo root) because commands load it with `@project_profile.md`, and that reference cannot depend on a setting. All other paths come from the profile.

## 3. Principles shared by all commands

These stay in the commands. No profile setting turns them off.

1. Read the profile first. If it is missing or a required field is empty, stop and tell the user to run /setup_profile.
2. The writer's notes win over the tool's own suggestions.
3. Report first, then stop and wait. Write files only after approval.
4. Never drop a number, result, citation or limitation. Merge it into the surviving text and list where it went.
5. Protected tokens stay byte-identical: math, citation commands, cross-references, labels, units, citation keys and numbers. The profile lists the token types per source format.
6. Never add a claim, result or citation that is in neither the source text nor the writer's notes. Mark new sentences with [NEW].
7. Flag material that belongs in another unit. Never move it across units.
8. Frozen text gets only the passes the profile allows.
9. Before showing output, search it for em dashes, en dashes and dash-written numeric ranges.
10. After a write, append one entry to the session log.

## 4. The four commands

The word "unit" below means the top-level part of the document: a chapter in a thesis, a section in a paper. The profile sets the word the commands use in their output.

### 4.1 /doc_check (generic thesis_check)

Whole-document, read-only check with verified findings. Expensive.
Argument: optional focus, for example "units 1 and 6" or "notation only".

Stays in the command:

1. Read-only guarantee: it never edits the document. It writes one report and one log entry.
2. Orchestration: a Workflow if the session offers one, otherwise parallel subagents.
3. Stage 1, extract: one agent per unit. Each returns the unit's claim with line number, one line per section, key results with numbers, symbols and first use, acronyms, cross-unit references, opening and closing paragraphs, voice counts, long-sentence share per section.
4. Stage 2, review: one agent per dimension. The dimensions are message, handoffs, repetition, notation, terminology and cross-references, claims against evidence, voice, requirements, and style.
5. Stage 3, verify: each finding goes to a separate agent that reads the cited lines and tries to disprove it. Only CONFIRMED findings reach the main report.
6. Stage 4, report: summary in five lines or fewer, findings by severity, known issues from the message map, rejected findings, comparison with the last report, model used. Each finding carries a ready-to-run command line for the fix.

Becomes a profile setting:

1. Unit list with file paths, and the main file to cross-check against.
2. Paths to the style guide, message map, reading notes, notation table and decisions log.
3. Summary units that must agree (for example the introduction and the conclusion, or the abstract and the results).
4. Message risks: framings to flag, written by the writer.
5. Requirements checklist from the institution or venue. The requirements dimension is skipped if the list is empty.
6. Milestone name for the top severity label ("Blocking before <milestone>").
7. Extra check prompts the writer wants included.
8. Reports directory.

### 4.2 /notation_check

Builds the notation table, reports problems, applies approved replacements.
Argument: optional unit file to limit the scope.

Stays in the command:

1. Stage 1: build or update the notation table. One subagent per unit when the scope covers more than one unit.
2. Stage 2 report: variants, collisions, symbols used before definition, conventions (sign, index placement, tensor or vector style, nondimensionalization), inconsistent words for one symbol, numbered proposed replacements. Then stop.
3. Where the authority unit is silent or inconsistent, propose a convention and mark it as needing the writer's decision.
4. Propose a macro when many replacements of one symbol would be simpler. Never edit macro files unless asked.
5. Stage 3: apply only approved replacements, all or a numbered subset. This is the one command allowed to change symbols inside math. It changes nothing else there.

Becomes a profile setting:

1. The notation authority: the unit that sets the convention, or "the notation table" if the writer has one already.
2. Macro files (read-only unless the writer asks).
3. Definition rule: define at first use in each unit (usual for a thesis, since units are read alone) or once per document (usual for a paper).
4. Frozen entries: replacements inside frozen text are listed separately.
5. Paths to the notation table and decisions log.

### 4.3 /chapter_flow

Whole-unit flow and condensing pass.
Argument: a unit file and optional extra instructions.

Stays in the command:

1. Stage 1, a report in ten parts, then stop:
   1. The unit's claim, quoted from its opening. Say so if there is none.
   2. The funnel: one line per section on what it argues and whether it serves the claim.
   3. Repetitions, and which place should keep the material.
   4. Broken handoffs between sections.
   5. Misplaced material, flagged and never moved.
   6. Condensing options with word savings, current word count, estimated total, long-sentence rate per section.
   7. Message risks and overclaims.
   8. Voice counts per section, and the contribution statement check.
   9. How the plan handles each of the writer's notes for this unit: applied (where) or not applied (why). Unreadable notes become questions.
   10. A proposed plan, with one line per section for /human_write.
2. Stage 2: save the approved plan with the date.
3. Stage 3: apply only approved structural moves (reorder, merge, cut duplicates). A new section gets only a heading and a comment stating its planned content. No sentence rewrites. Show the diff and every removed passage with where its content went.
4. Include open findings for this unit from the latest doc_check report.

Becomes a profile setting:

1. Unit rules, for example "no equations in the introduction" or "every acronym explained in plain words".
2. Frozen entries and their allowed passes.
3. Voice rule and whether the unit needs a contribution statement.
4. Long-sentence threshold, per unit if the audience differs.
5. Word count command and length target per unit.
6. Plans directory, reading notes path, reports directory.

### 4.4 /human_write

Section-level strict rewrite pass.
Argument: a file with a section name, a file with a line range, or pasted text. Optional extra instructions, including "voice only".

Stays in the command:

1. Read the whole unit for context and its approved plan. Rewrite only the target. If the target is a whole unit, send the writer to /chapter_flow first, unless the mode is voice only.
2. Voice-only mode: change only pronouns and self-references, per the profile's voice rule. Works on any target up to a whole unit.
3. Section funnel: the first sentence states what the section argues. Each paragraph leads with its claim. The last sentence states the finding and sets up the next section. No recaps or signposting in between.
4. Sentence-by-sentence pass against the style guide. Condense repetition without losing content.
5. Long sentences: each kept sentence over the threshold needs a reason. Propose splits where they cluster.
6. Protected tokens byte-identical. The only number change allowed is the style guide's spelled-out small counts, and each one is listed. Symbols that differ from the notation table are flagged for /notation_check, not changed.
7. Output: a diff with [NEW] marks, then seven lists: (a) flags, (b) number changes, (c) removed sentences and where their content went, (d) possible meaning shifts, old and new side by side, (e) the writer's notes applied, (f) long sentences kept with word count and reason, (g) voice questions where it is unclear who did the work.

Becomes a profile setting:

1. Voice choice and its rules (see section 5.4).
2. Frozen entries, allowed passes and the override phrase.
3. Reading-note marks and their meanings.
4. Protected token list for the source format.
5. Audience per unit, and the long-sentence threshold.
6. Paths to the style guide, notation table, plans and session log.

## 5. project_profile.md, field by field

Format: plain Markdown with fixed headings. Short fields are `key: value` lines. Lists are numbered. Each field in the template has a one-line comment saying what it does and which commands read it. Required fields are marked (required).

### 5.1 Document

1. document_type (required): thesis, paper, book or report. Sets defaults for other fields.
2. unit_name: what the top-level part is called. Default "chapter" for a thesis or book, "section" for a paper.
3. source_format (required): latex, markdown, quarto, typst or other. Sets the default protected tokens and the dash search.
4. main_file (required): the file that includes the units, for example main.tex.
5. spelling: US or UK English, plus any fixed spellings.
6. next_milestone: the next draft the writer is working toward, for example "committee draft". Used in severity labels.

### 5.2 Units (required)

One row per unit, in reading order:

1. number: the built number the reader sees.
2. short_name: a few words.
3. file: path to the source file.
4. role: introduction, background, method, results, discussion, conclusion or appendix.
5. based_on: none, a published paper, or a submitted manuscript. If set, the unit needs a contribution statement.
6. collaborators: names to credit for work in this unit. Used by the voice rule.
7. audience: overrides the document audience for this unit, for example "non-specialist".
8. length_target: words or printed pages.
9. rules: free-text rules for this unit, one per line.

### 5.3 Frozen text

One entry per frozen passage:

1. unit and location: section numbers or a line range.
2. reason: published, submitted, legally fixed, or other.
3. allowed passes: voice, notation, or none.
4. external copy: where the matching version lives, if any, so the writer knows to update both.

Plus one field for the whole document:

5. override_phrase: the words the writer types to allow a full edit of frozen text, for example "edit frozen too".

### 5.4 Voice

1. person (required): one of "I" (first person singular), "we" (first person plural), third person, or impersonal.
2. banned self-references: derived from the choice, with room to add more.
3. credit rule: name collaborators and predecessors instead of using a pronoun for their work. On by default.
4. contribution_statement: required for units with based_on set. Yes or no.
5. self_citation_form: how the writer cites their own published work.

### 5.5 Audience and sentences

1. audience: the primary reader, in one line.
2. long_sentence_words: the threshold. Default 25.
3. strict_units: units with a stricter threshold, and the threshold for them.

### 5.6 Message

1. message_map: path.
2. summary_units: the units that must tell the same story.
3. message_risks: framings to flag, one per line. Example: "a side study presented as a main contribution".

### 5.7 Notation

1. notation_authority: a unit number, or "table".
2. notation_table: path.
3. macro_files: paths, read-only.
4. define_at_first_use: per unit or per document.

### 5.8 Reading notes

1. reading_notes: path.
2. marks: the standard marks and their meanings (keep, cut, move to unit N, too strong, too weak), plus any custom marks the writer adds.
3. unclear_marker: default [?].

### 5.9 Length and build

1. word_count_command: for example `texcount -sum -q {file}` or `wc -w {file}`.
2. build_command and build_dir.
3. build_log and a check command for undefined references.
4. build_fallback: manual steps if the build command fails.

### 5.10 Requirements

1. requirements: a numbered checklist from the institution or venue. Free text. Checked by /doc_check.

### 5.11 Paths

1. notes_dir: default notes/.
2. style_guide, decisions_log, session_log, plans_dir, checks_dir.
3. extra_check_prompts: files /doc_check should also read.

### 5.12 Protected tokens

1. Defaults per source_format. For LaTeX: commands, inline and display math, citation commands, cross-reference commands, labels, units, citation keys, numbers.
2. extra_protected: the writer's own macros.

## 6. Setup prompt

Two pieces with one source of truth:

1. setup/SETUP_PROMPT.md: a short prompt the user pastes into Claude Code in their own repo. It copies the commands and templates from the toolkit, then reads and follows commands/setup_profile.md.
2. commands/setup_profile.md: the interview itself. The user can rerun it later as /setup_profile to update the profile.

The interview:

1. Look before asking. Find the main file, the unit files, the build files, macro files and any word count tool. Propose values from what it finds.
2. Ask in small batches, in this order: document type and format; units (confirm the detected list); voice; audience; frozen text; notation authority; build and length; requirements; milestone. Offer a sensible default for every question.
3. Explain each choice in one sentence when it matters. The voice question explains the four options with a one-line example each.
4. Show the full profile and wait for approval before writing.
5. Write project_profile.md. Copy the templates into notes_dir, skipping files that already exist. Fill the voice section of writing_style.md from the voice choice.
6. Append the snippet to the user's CLAUDE.md, after showing it.
7. Validate: every path in the profile exists, the build command runs, the word count command runs. Report what failed.
8. Tell the user the first step of the tutorial.

On a rerun, it reads the current profile, asks only what the user wants to change, and shows a diff.

## 7. Templates

Every template is short, generic and has comments that explain each part. Setup copies them. The writer owns them after that.

1. writing_style.md: a default style guide the writer is expected to edit. Sections: voice (one of three variants, chosen at setup), punctuation, structure, numbers and equations, hedging, words to avoid, limitations, citations, editing existing text. Each rule is one line with a short example. Invented examples only.
2. reading_notes.md: a legend of marks at the top, then one heading per unit. One note per line: location (section or printed page), mark, note. Guidance: one idea per note, and write the fix if you know it.
3. message_map.md: the document's claim in one sentence. Per unit: its claim, what it adds, what it hands to the next unit. A "does not claim" list. A "known issues" list that /doc_check reports against.
4. notation_table.md: columns for quantity, meaning, canonical symbol, source code, macro, variants by unit with file:line, and status (agreed or needs decision).
5. decisions_log.md: dated entries with the decision, the reason, the scope, who decided, and what it supersedes. Commands read the entries whose scope matches their task.
6. session_log.md: one line per write: timestamp, command, target, one-sentence summary.
7. claude_md_snippet.md: a few lines for the user's CLAUDE.md: read project_profile.md before editing the document, follow the style guide, show diffs before writing.

## 8. Docs

1. tutorial.md: the editing cycle, adapted from the design of the original guide, written with an invented example document. Parts:
   1. The big picture: the writer's reading decides the message; the tools apply it and check it.
   2. Baseline: run /doc_check and /notation_check before reading. How to read the report.
   3. Reading and marking on paper or on screen. The marks and what each one tells the tools.
   4. Getting notes into the repo: a transcription prompt, and checking it line by line.
   5. Editing one unit: /chapter_flow report, plan approval, structural diff, /human_write section by section, voice-only passes on frozen text, rebuild, checks before moving on.
   6. After all units: apply notation, run the second /doc_check, compare with the baseline.
   7. The final read before the milestone.
   8. Quick reference: task, command, suggested model and effort.
   9. What the tools cannot do, and troubleshooting.
2. install.md: manual install, updating to a new toolkit version without losing the profile, uninstall.
3. profile_reference.md: every field, its default, and which commands read it.
4. customizing.md: add a mark, a unit rule, a message risk or a requirement. When to edit the style guide versus the profile.

## 9. Distribution

1. Now: a plain repo. The user clones it next to their project and pastes the setup prompt. Commands are copied into the project's .claude/commands/, so they work offline and the user can edit them.
2. Later: a Claude Code plugin with the same commands and templates, installable from a marketplace. Commands would be namespaced (for example `/thesis-toolkit:human_write`). The plugin reads templates from its own install folder. The profile stays in the user's repo, so switching from the plain repo to the plugin needs no profile change.
3. Versioning: a version line in each command and in the profile template. /setup_profile warns when the profile is older than the commands and offers to add new fields.

## 10. Later additions

1. /respond_reviewers: takes reviewer comments and the document. Stage 1 splits the comments into numbered points and maps each to locations in the text. Stage 2 drafts a response table (point, response, change made, location) in the writer's voice. Stage 3 applies approved text changes through the same rules as /human_write. Never promises an experiment the writer has not confirmed.
2. /cite_check: read-only. Every citation key resolves in the bibliography. No unused entries. Flags claims that need a citation and have none, and bibliography entries with missing fields. Does not judge whether a source supports a claim unless the writer supplies the source.
3. /figure_check: read-only. Every figure and table is referenced in the text before it appears. Captions are self-contained. Symbols in captions match the notation table. Units on axes are named in the caption or text. Reports figures never discussed.

## 11. Build order and open decisions

Build order, after approval:

1. templates/project_profile.md and docs/profile_reference.md, since every command depends on them.
2. The other templates.
3. commands/setup_profile.md and setup/SETUP_PROMPT.md.
4. The four commands.
5. examples/sample_doc: a short invented LaTeX document, about three units, with planted problems (a symbol variant, a repeated paragraph, a voice slip, a dash range) so each command has something to find.
6. Dry runs of every command on the sample document. Fix the commands.
7. docs/tutorial.md and docs/install.md, written against the sample document.
8. README.md.

Decided:

1. The whole-document check is `/doc_check`. "thesis_check" reads oddly for a paper.
2. The profile lives at the repo root, where the writer can find it.
3. The toolkit ships examples/sample_doc. It doubles as the test fixture.
