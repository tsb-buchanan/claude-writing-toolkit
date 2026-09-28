---
name: notation-check
description: Thesis only. Lists every math symbol, keeps a symbol table, reports variants, clashes and symbols used before they are defined, and fixes approved symbols in equations.
license: MIT
metadata:
  version: "1.1"
---

# notation-check

Keep the symbols of a thesis consistent across chapters. This skill is for thesis mode only. If the profile says `mode: report`, say that notation-check is for theses, and stop.

1. Write no em dashes, in your messages or in any file. Use a colon, a comma or a new sentence instead.
2. This is the only skill that may change a symbol inside an equation. Change symbols only, only inside math, and only after the writer approves. Change no other text.
3. The profile's notation source decides which symbol is right. Where it is silent, propose a convention, and mark it as the writer's decision.
4. Never change a keep passage. A keep light passage may get symbol fixes.

Files named below are in this skill's folder (${CLAUDE_SKILL_DIR} in Claude Code). Scripts are in its scripts/ folder.

## 1. Read

1. The profile: "# Writing profile" in the Project (claude.ai), or doc-profile.md (Claude Code). You need `notation_source`, `define_symbols` and the chapter files.
2. The symbol table, if there is one: "# Notation" in the Project's knowledge (claude.ai), or doc-notes/notation.md (Claude Code).
3. The files: the chapter the writer names, or every chapter file in the profile. Always include the notation source's chapter. On claude.ai, use the uploaded LaTeX or Markdown files.
4. Run `python3 scripts/symbols.py FILE1 FILE2 ...` on all of them. It lists every symbol with its first use in each file, the places where it stands left of "=", and the lines of its other uses. Work from that list. Read a passage of a file only to settle a doubt.

A PDF has no math source. Read its text, say that the report is less accurate, and apply no fixes. For a symbol inside a Word equation, list the fix for the writer to make by hand.

## 2. Stage 1: the symbol table

Build the table, or update the one you have. One row per quantity:

```
# Notation
toolkit: 1.0
written: YYYY-MM-DD
source: the profile's notation source

| Symbol | Meaning | Defined in | Avoid |
|---|---|---|---|
| $\lambda$ | the arrival rate, in returns per hour | Chapter 2, file.tex line 7 | $\Lambda$ |
```

"Defined in" is the place where the words say what the symbol means. Mark a row that the notation source does not cover with "(proposed)".

## 3. Stage 2: the report. Then stop.

Keep the report to one page, under these headings. Give a file and line for each item.

1. Variants: one quantity written with two or more symbols.
2. Clashes: one symbol with two or more meanings. Read the "=" lines: a symbol set equal to two different things is a strong sign.
3. Used before it is defined. With `define_symbols: each chapter`, each chapter must define a symbol, in words, at or before its first use in that chapter. With `once`, the first use in the thesis must. Naming a symbol in passing is not a definition. A definition says what the symbol is, and how it is found or measured.
4. Fixes, numbered. Each names the old symbol, the new one, and every place it changes (file, line, equation label). Say whether the notation source settles it, or whether it is a proposal for the writer to decide.

A missing definition needs words, not a new symbol. Report it for the writer or human-write, and do not apply it.

On claude.ai, give the report in the chat. In Claude Code, give it in the chat as well.

End with: "Reply with the fixes you approve (for example 1, 2), all, or none."

## 4. Stage 3: apply the approved fixes

1. Change only the symbol, only inside math, only at the places the fix lists.
2. Check the result: `python3 scripts/symbols.py FILE --symbol "OLD"` must show no use at the fixed places, and the diff must show changes inside math only.
3. Update the table: the new symbol, and the old one under "Avoid".
4. In Claude Code, follow text-output.md for the chapter files. The writer's reply to the fix list is the approval, so show the diff and then write the files without asking again. Write the table to doc-notes/notation.md. Unless the profile says commit: no, commit the files and the table together, with a message that names the changes, such as "notation-check: \Lambda to \lambda". Never push.
5. On claude.ai, save a corrected copy of each changed file with the outputs, with the same name, and list each change: file, line, old, new. Save the table as notation.md, and tell the writer, in one line, to add it to the Project's knowledge in place of the old one.

If the writer approves no fixes, still save the table.

End with one line: the next step, such as human-write for a missing definition, or doc-check.
