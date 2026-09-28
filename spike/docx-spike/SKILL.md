---
name: docx-spike
description: Test skill for the writing toolkit spike. Use only when the user asks to run the docx spike.
license: MIT
metadata:
  version: "0.0.1"
argument-hint: "[path to a .docx file]"
---

# docx spike

This is a test, not a writing tool. It checks how Word files and scripts behave here.
Follow the steps in order. Keep every answer short.
Use only this skill's script. Do not load any other skill.

## Step 1: what you can see (use no tool)

Before you read any file or run anything, answer:

1. Can you see the text of the uploaded Word document in this conversation already? Answer yes or no.
2. If yes, quote the document's title and the line that starts with "Canary:". If you cannot see them, write "not visible". Do not guess.

## Step 2: find the script and the file

1. The script is scripts/docx_probe.py in this skill's folder. In Claude Code that folder is ${CLAUDE_SKILL_DIR}. Elsewhere, use the folder you read this SKILL.md from.
2. Run `python3 <script> env`. It prints the Python version, the folders it can see and the .docx files it finds.
3. Choose the uploaded file, or the file the user named.

## Step 3: read the file

Run `python3 <script> read <file>`.
Then say, in three lines at most: how many paragraphs, which headings, and which comments sit on which paragraphs. Do not paste the output.

## Step 4: write three tracked changes into a copy

Write a JSON file with three changes. Use the paragraph numbers from step 3.

1. replace: the paragraph under "Background" that has bold words. Cut the filler words. Keep every fact, and keep the bold and italic words exactly as they are.
2. insert_after: the "Summary" heading. Text: "[NEW] This paragraph was added by the spike test."
3. delete: the paragraph whose comment starts with "spike: delete".

If the file is not the spike sample, use any body paragraph for 1 and the first heading for 2, and leave out 3.

The JSON file looks like this:

```
{"author": "Claude", "changes": [
  {"op": "replace", "para": 6, "expect": "first few words", "text": "the whole new paragraph"},
  {"op": "insert_after", "para": 3, "text": "[NEW] ..."},
  {"op": "delete", "para": 23, "expect": "first few words"}]}
```

Then run `python3 <script> apply <file> <json file> <output file>`.
Name the output like the input, with "-tracked" before ".docx". Save it where you save files for the user to download. In Claude Code, save it next to the input file.
Give the output file to the user.

## Step 5: report

End your answer with this block, filled in:

```
SPIKE REPORT
place: claude.ai web, claude.ai desktop app, or Claude Code
text visible before any tool: yes or no
canary line: (quote it, or "not visible")
python: (version from step 2)
skill folder: (path)
uploaded file: (path)
paragraphs and comments: (numbers from step 3)
apply result: (the script's check lines)
output file: (path)
problems: (none, or what went wrong)
```
