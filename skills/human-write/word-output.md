# Word output

How to return changes to a Word file as tracked changes. The scripts are in this skill's scripts/ folder.

## 1. Find the file

1. claude.ai: uploads are usually in /mnt/user-data/uploads/. Save files for the writer in /mnt/user-data/outputs/.
2. Claude Code: use the file in the repo. Save the copy next to it.

## 2. Get the paragraph numbers

1. One section: `python3 scripts/docx_tool.py read FILE --section "NAME"`. A section number such as "4.2" also works, and so does `--paras 12-18`.
2. The whole document (doc-flow): `python3 scripts/docx_tool.py outline FILE`. It gives one short line per paragraph.
3. On claude.ai the uploaded text is already in the chat. Never run read on the whole file there.

## 3. Write the changes file

Write the changes as JSON in a file named changes.json. In Claude Code, put it in drafts/ in the notes folder (doc-notes/ unless the profile says otherwise). On claude.ai, keep it out of the outputs folder.

```
{"author": "Claude", "changes": [
  {"op": "replace", "para": 17, "expect": "first few words", "text": "the whole new paragraph"},
  {"op": "delete", "para": 48, "expect": "first few words"},
  {"op": "insert_after", "para": 3, "text": "a new paragraph", "style": "Heading2"},
  {"op": "move", "paras": [68, 69], "after": 3, "expect": "first few words of 68"}]}
```

1. Give the whole new text of each changed paragraph.
2. Make "expect" the first three to six words of the paragraph as it is now.
3. Make one change per paragraph. Leave unchanged paragraphs out.
4. "style" is optional. Use it only for headings, with a style the outline shows.
5. "after": 0 means before the first paragraph. After a table cell means after the whole table.
6. "move" takes a block of paragraphs: "paras": [first, last]. The block goes after the paragraph "after" names.

## 4. Apply the changes

Run `python3 scripts/docx_tool.py apply FILE changes.json OUT`. Name OUT like the file, with "-tracked" before ".docx". The tool never overwrites a file. If OUT is left from an earlier run, add a number: NAME-tracked-2.docx. To redo your own OUT in this run, add `--replace`.

Then read the tool's report:

1. "skipped": the tool could not make that change safely. Tables, keep passages, equations, footnotes, fields and links stay as they are. Give the proposed text in the chat, so the writer can paste it by hand.
2. "protected content": a number, citation or quotation changed. Fix the change and apply again, or list it for the writer.
3. The three checks must each say yes. If one says NO, do not give the file to the writer. Say what went wrong.

## 5. Deliver

Give the writer OUT. Tell them, in one line: open it in Word, then accept or reject each change under Review, and save it as the new version.

Do not repeat the new text in the chat. The writer reads it in Word. Say that a file is written or deleted only after the command worked.

In Claude Code, do not commit the tracked copy or changes.json. The writer commits the file after deciding in Word.

## PDF or pasted text

1. Save the original text of the section in a text file. Start each heading line with "# " or "## ".
2. Run `python3 scripts/docx_tool.py from-text TEXT BASE.docx`.
3. Use BASE.docx as FILE above.
4. Tell the writer that the file holds only that text, without their own formatting.
