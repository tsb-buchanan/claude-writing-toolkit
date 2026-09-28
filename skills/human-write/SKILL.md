---
name: human-write
description: Rewrites one section of a thesis or report in the writer's style, and shows every change for approval. Numbers, facts, citations and equations never change.
license: MIT
metadata:
  version: "1.1"
---

# human-write

Rewrite one section in the writer's style. Change only what a rule below or the profile asks for, never just to sound more human or to fool an AI detector.

1. Write no em dashes, in your messages or in the text. Use a colon, a comma or a new sentence instead.
2. Change nothing outside the target section.
3. Write no file before the writer approves, except a tracked-changes copy of a Word file: the writer approves each change in Word.

Files named below are in this skill's folder (${CLAUDE_SKILL_DIR} in Claude Code). Scripts are in its scripts/ folder.

## 1. Read only what you need

1. The profile. On claude.ai: the block "# Writing profile" in the Project's instructions or knowledge. In Claude Code: doc-profile.md. If there is none, offer doc-setup, or use the defaults for the mode the writer names.
2. The document map, if there is one. On claude.ai: "# Document map" in the Project's knowledge. In Claude Code: doc-notes/doc-map.md. Without a map, work from the section alone, and suggest "doc-flow map only".
3. The target section, and the paragraph before and after it. With `budget: standard`, also read the rest of the chapter. Never read the whole document with a tool.
   1. A Word file: `python3 scripts/docx_tool.py read FILE --section "NAME"`.
   2. LaTeX, Markdown or text: read the section's lines from the file.
   3. Pasted text: that is the section.
4. One section per run. If the writer asks for more, do the first, and suggest a new chat for the next.
5. If the request says "light", fix only voice, spelling, dashes, number format and banned words.

## 2. Rewrite

The rules, most important first:

1. Never change a keep passage: one marked keep in the text, or one on the profile's keep list. A keep light passage, or a chapter whose passes are light, gets light fixes only.
2. Never change the value of a number, or a fact, citation, cross-reference or quotation. The format of a number may change to meet the profile's number rule. Never cut or soften a limitation.
3. Never change anything inside an equation, not even its final comma or full stop, and add no new math. A display equation is part of a sentence, so make the words around it fit it. If it ends with a comma, the same sentence goes on after it.
4. Never add a claim, result or citation. A new sentence may only restate what the section or the map already says. Start every new sentence with [NEW].
5. Lead each paragraph with its claim.
6. Keep sentences short. A sentence over the profile's limit needs a reason, and you list it.
7. Cut filler, the profile's banned words, recaps (sentences that sum up what the reader has just read), and signposts that say what the section will do. Keep a closing line that leads to the next section, even a wrong one. Say what a result means once, where the section concludes.
8. Say what a method, model, machine or process does in literal words, not in a metaphor such as "the model struggles". If the section does not say, flag it.
9. Follow the profile's voice, spelling, dash rule, number rule and house rules. Credit others by name for their work. If the voice is "I" and the work was shared, write "my supervisor and I" or name the people.
10. Use the map's key terms. Without a map, leave a thing that has two names as it is, and flag it for doc-flow. Flag a symbol that stands for two things, or differs from the notation table, for notation-check.
11. Flag, but do not fix: material that belongs in, or repeats, another section; a wrong or missing handoff; and a number that differs from the map. These are for doc-flow.

## 3. Check before you show

The draft is the copy that text-output.md or word-output.md makes. For a tracked copy, the apply step runs the first check.

1. `python3 scripts/check_protected.py FILE DRAFT`
2. `python3 scripts/doc_stats.py DRAFT --section "NAME" --limit N --banned "WORDS"`, with the profile's sentence limit and words to cut. Judge its first-person words and numbers against the profile's voice and number rules.
3. In LaTeX, note what each symbol in the section stands for. A symbol that stands for two things is a flag for notation-check.
4. Ask of each paragraph: does it do this section's job (a method or background section reports no results), and does it name a case, a number or a source? Flag each paragraph that fails.
5. Fix everything the scripts report, or list it.

## 4. The lists

Give these lists, one line per item, with no em dashes. Leave out empty lists. Add at most 100 words of other text.

1. Number changes: the old and new form, and where.
2. Removed sentences, and where their content went.
3. Sentences whose meaning could have shifted: old and new.
4. Long sentences kept: word count and reason.
5. Flags, for the writer or another skill.

## 5. Show the change, then write after approval

1. A Word file, a PDF or pasted text, in either place: follow word-output.md.
2. LaTeX, Markdown or text, in either place: follow text-output.md. In Claude Code, the commit message is "human-write: SECTION".

End with one line: the next section to rewrite, or doc-check.
