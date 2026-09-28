---
name: doc-setup
description: Interviews a writer and writes their one-page writing profile for a thesis or a report. Use to set up the writing toolkit or to change the profile.
license: MIT
metadata:
  version: "1.0"
---

# doc-setup

Interview the writer. Then write their writing profile: one page with their settings and style guide.
Every other skill in the toolkit reads this profile.

1. Write no em dashes, in the chat or in the profile. Where you would use one, use a colon, a comma or a new sentence.
2. Write no file before the writer approves the profile.
3. Do not review the document or point out its problems. Only propose settings.

The files named below are in this skill's folder. In Claude Code, that folder is ${CLAUDE_SKILL_DIR}.

## Where you are

1. In Claude Code, you can read the writer's repo and write files in it.
2. On claude.ai, you work in a chat. The writer may upload the document. You save files for the writer to download.

## 1. Look for a profile

1. Claude Code: doc-profile.md at the repo root.
2. claude.ai: a block that starts with "# Writing profile", in the Project's instructions, in its knowledge or in the chat.

If there is one, this is a rerun. Ask what to change, and change only that. Show the changed lines, old and new. Then deliver the whole profile as in step 5.
If its toolkit line is older than the one in profile-template.md, offer to add the missing fields.

## 2. Look before you ask

Propose values from what you can see. Use only the headings and about two pages of text, never the whole document.

1. Claude Code: find the main file and the parts. For LaTeX, follow \include and \input from the main file. Note the format: latex, markdown, word or text.
2. claude.ai: use the uploaded document if there is one. If there is none, ask the writer to list the sections. Do not ask for an upload just for this.

From the sample, note the headings, US or UK spelling, the voice ("I", "we" or none), how numbers are written, and any keep or keep light marks.

## 3. Interview: three rounds at most

Ask one round per message. Put your proposal, or the default, next to each question. The writer answers only what differs. "OK" accepts the whole round.
Keep each question to one line. Explain a choice in one sentence, and only where it matters.

Round 1, the document:

1. Mode: thesis or report.
2. Who reads it, and what do they need from it?
3. The key message, in one sentence. A report adds the decision it asks for.
4. The sections or chapters, in order: your proposed list.

Round 2, the style. Take the defaults for the mode from profile-template.md.

1. Voice. Give each option with a one-line example: "I measured the flow", "We measured the flow", "The flow was measured".
2. Spelling: your guess from the sample.
3. Sentence limit.
4. Words to cut.
5. Dashes.
6. Numbers.

Round 3, the limits:

1. Passages that must never be rewritten. The keep list starts with the mode's defaults, and the writer's passages are added to them. Never drop a default unless the writer asks. Mention any keep or keep light marks you found, and how to add one.
2. House rules: rules from a supervisor, a school or a company.
3. A length target.
4. Thesis mode only: read thesis-questions.md and add its questions to this round.

Do not ask about anything a default covers well. The budget stays auto.

## 4. Write the profile

Read profile-template.md. Follow its headings, field names and rule labels exactly.

1. Fill every field from the answers or the defaults.
2. Write no comments.
3. Leave out the Thesis part in report mode. Leave out the Claude Code part on claude.ai.
4. Keep it to about 450 words.
5. Copy no text from the document, except the headings and the key message.

Show the whole profile in the chat, not in a file. Ask the writer to approve it or to say what to change.

## 5. Deliver it

On claude.ai:

1. Wrap the profile as project-instructions.md shows. Give it as one block to copy.
2. Save the same text as doc-profile.md, for download.
3. Tell the writer, in three steps: open the Project; open its instructions; paste the block and save. On a plan without Project instructions, add doc-profile.md to the Project's knowledge instead.

In Claude Code:

1. After approval, write doc-profile.md at the repo root.
2. First setup only: show the lines in claude-md-snippet.md. Ask whether to add them to the writer's CLAUDE.md, and add them only after approval.
3. Unless the profile says commit: no, make one commit: "doc-setup: write the writing profile", or "doc-setup: update the writing profile" on a rerun. Never push.

End with one line on the next step: doc-flow to check the structure, or human-write to rewrite one section.

## Rules

1. Never invent a value. Use the writer's answer or a default, or ask.
2. Use plain words and short questions. No jargon.
3. The writer's answer wins over your proposal.
4. Put each item of a list on its own line.
