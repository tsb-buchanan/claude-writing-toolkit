---
name: doc-flow
description: Reviews the structure of a report or one thesis chapter, applies the moves the writer approves, and writes a one-page document map. "doc-flow map only" writes just the map.
license: MIT
metadata:
  version: "1.1"
---

# doc-flow

Review the structure of one report or one thesis chapter. Apply only the moves the writer approves. Then write the document map.

1. Write no em dashes, in your messages or in any file. Use a colon, a comma or a new sentence instead.
2. Never change the words of a sentence. Moves work on whole sentences, paragraphs, sections and headings: reorder, cut a duplicate, merge sections, add a heading. Work inside a sentence is for human-write.
3. The writer's notes win. If a note blocks a suggestion, follow the note, and say what you would have suggested.
4. Change the document only after the writer approves.

Files named below, and the scripts/ folder, are in this skill's folder (${CLAUDE_SKILL_DIR} in Claude Code).

## 1. Read

1. The profile: "# Writing profile" in the Project (claude.ai), or doc-profile.md (Claude Code). If there is none, offer doc-setup, or use the defaults for the mode the writer names.
2. The writer's notes: the message, Word comments, doc-notes/notes.md, and comments in the source. Keep marks too.
3. The current map, if any: "# Document map" in the Project's knowledge (claude.ai), or doc-notes/doc-map.md (Claude Code).
4. The document: a report whole, a thesis one chapter at a time.
   1. A Word file on claude.ai: its text is already in the chat. Run `python3 scripts/docx_tool.py outline FILE` for paragraph numbers and comments.
   2. A Word file in Claude Code: `python3 scripts/docx_tool.py read FILE`.
   3. LaTeX, Markdown or text: read the file.
5. `python3 scripts/doc_stats.py FILE --limit N --banned "WORDS"`, with the profile's sentence limit and words to cut.

"doc-flow map only": skip to section 4.

## 2. Stage 1: the report. Then stop.

The cap is 600 words, or 1,200 with `budget: standard`. `budget: auto` is standard for a thesis in Claude Code, and lean otherwise. Give one line per finding. Leave out a heading with nothing to report.

1. Main message (a thesis chapter: its claim): quote it, with its place. If it comes later than the profile's opening rule asks, propose moving its paragraph or its whole section forward. If neither can move, flag it for human-write.
2. Sections that do not move toward the main message: one line each, with the section's job.
3. Repetition: where, and which place should keep it, and why.
4. Handoffs: each opening or closing line that points to another section. Is it right?
5. Material in the wrong place. Check each paragraph of a method or background section for a result: a figure the work produced. Material that belongs in another chapter is flagged, never moved there.
6. House rules: check each one against every paragraph. Report a borderline case, and say what it turns on.
7. Numbers that differ between sections. Report them, and fix neither.
8. Length: the sections over their target, and cuts with the words each saves.
9. Long sentences: the rate per section, from doc_stats.py, and the worst sections for human-write.
10. The writer's notes: applied, or why not.
11. Proposed moves, numbered, each naming what moves and where to. Before you move a paragraph, read the next one. If it points back, as with "this budget", move both. If the moves change the order, add the new outline.

Never move, cut or split a keep or keep light passage.

On claude.ai, the report goes in the chat. In Claude Code, save it as doc-notes/plans/DATE-flow.md (or in the profile's notes folder), with the date as YYYY-MM-DD. Then give in the chat only the main message finding, the proposed moves and the report's path.

End with: "Reply with the moves you approve (for example 1, 3), all, or none. Then I apply them and write the document map."

## 3. Stage 2: apply the approved moves

1. Apply only the moves the writer approved. A new heading gets no body text.
2. Before you cut a duplicate, check that each fact in it survives elsewhere: `python3 scripts/check_protected.py FILE DRAFT` must list no number as "no longer anywhere in the text".
3. List each removed passage, and where its content now is.
4. A Word file, a PDF or pasted text, in either place: follow word-output.md. Use "move", "delete", and "insert_after" with a heading style.
5. LaTeX, Markdown or text, in either place: follow text-output.md. In Claude Code, stop after the diff and wait for a second approval. Then write the file, but commit only after the map.
6. Every run ends with the map (section 4). With a Word file, write the map before you deliver, so that the writer gets the tracked copy and the map in one message.

If the writer approves no moves, go to section 4.

## 4. Stage 3: write the map

Follow map-template.md. Write what the document says after the approved moves.

1. A report: one page. A thesis: one block of one page for this chapter. Replace only this chapter's block.

On claude.ai: save doc-map.md with the outputs. Tell the writer to add it to the Project's knowledge in place of the old map.

In Claude Code: write doc-notes/doc-map.md. Unless the profile says commit: no, commit the report, the map and any changed text file together, with the message "doc-flow: FILE". Never push.

Before you say a file is written, check that the command worked.

End with one line: human-write on the section with the most long sentences, or doc-check.
