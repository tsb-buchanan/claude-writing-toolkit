---
name: doc-check
description: Read-only. Checks a report or a thesis chapter against a fixed checklist and lists the top 10 issues, each with a next step. Run it before the document goes out.
license: MIT
metadata:
  version: "0.1"
---

# doc-check

Read-only: this skill never changes the document.

1. Write no em dashes, in your messages or in any file. Use a colon, a comma or a new sentence instead.
2. Report issues. Never fix them. Each issue names the skill or the decision that fixes it.
3. Leave out style issues inside a keep passage. Inside a keep light passage, report only what a light pass fixes: voice, spelling, dashes, number format and banned words.
4. Before you report something as missing or broken, look for it in every file you have. A label, for example, may be defined in another chapter. If you cannot look, leave it out.
5. The flags that docx_tool.py prints, such as "mixed formatting" or "comment", tell the editing skills what they can change. They are not issues.

Files named below are in this skill's folder (${CLAUDE_SKILL_DIR} in Claude Code). Scripts are in its scripts/ folder.

## 1. Mode

Quick mode is the default, on claude.ai and in Claude Code. It reads once and uses no subagents.

Full mode checks a whole thesis or a long report in depth, with subagents. Run it only when the writer asks for it.

1. On claude.ai: say in one line that full mode needs Claude Code, and offer quick mode.
2. In Claude Code: follow full-mode.md, and skip the rest of this file.
3. In thesis mode, when the profile names a milestone, end a quick check by suggesting full mode before it.

## 2. Read

1. The profile: "# Writing profile" in the Project (claude.ai), or doc-profile.md (Claude Code). If there is none, offer doc-setup, or use the defaults for the mode the writer names.
2. The map, if any: "# Document map" in the Project's knowledge (claude.ai), or doc-notes/doc-map.md (Claude Code).
3. The document: a report whole, or one thesis chapter.
   1. A Word file on claude.ai: its text is already in the chat. Do not read it again.
   2. A Word file in Claude Code: `python3 scripts/docx_tool.py read FILE`.
   3. LaTeX, Markdown or text: read the file.
4. `python3 scripts/doc_stats.py FILE --limit N --banned "WORDS"`, with the profile's sentence limit and words to cut. It counts long sentences, banned words, dashes and [NEW] marks per section.

## 3. The checklist

Check each item across the whole document or chapter.

1. Main message: clear, and as early as the profile's opening rule asks. In a thesis chapter, the chapter's claim.
2. Numbers: one quantity has one value everywhere, and the value the map gives.
3. Terms: one thing has one name, as the map's key terms say. Before you report two names, check that they mean the same thing. Two defined measures with their own names are not an issue.
4. Claims that need a source and have none: a claim about the world beyond the document's own work, with no citation or source.
5. Length: suits the audience and the profile's length target.
6. The profile's style guide: sentence limit, words to cut, dash rule, number format, voice, house rules, and [NEW] marks left in the text. doc_stats.py lists all but the house rules. Judge its first-person words and numbers against the voice and number rules: a unit after a digit, such as "3 minutes", may be fine.
7. Thesis mode, with `contribution: yes`: a chapter or section based on a co-authored paper says who did what.

## 4. The list

Give the top 10 issues only, most important first: message, then numbers, sources, terms, length, and style last. Give all 10 when there are that many. Merge issues of one kind into one line, such as all the banned words. Put the small style slips (voice, dashes, number format, words to cut) in one or two lines, with an example of each, so that they never crowd out the rest.

Each issue, in about 40 words:

1. The section, and a short quote of the words it is about.
2. Why it matters, in one line.
3. The next step. Name the skill that fixes it: doc-flow for structure, order and repetition; human-write on the section for sentences, voice and style ("light" for small fixes); notation-check for symbols. Leave only facts to the writer, such as which number is right or whether a source exists.

Then one line: the number of smaller issues not shown.

On claude.ai, the list goes in the chat.

In Claude Code, save the list as doc-notes/checks/DATE-quick.md, with the date as YYYY-MM-DD. If that file exists, add a number, such as DATE-quick-2.md. If the profile gives another notes folder, use it in place of doc-notes/. Unless the profile says commit: no, commit only that file, with the message "doc-check: quick check". Never push. In the chat, give one line per issue, in the form "1. Section: the issue. Next: the skill.", and the file's path. Before you say the file is saved, check that the command worked.

End with one line: the first step to take.
