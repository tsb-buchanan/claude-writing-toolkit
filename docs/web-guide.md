# The writing toolkit on claude.ai

This guide shows you how to use the writing toolkit on claude.ai, in the browser or the desktop app. You need no technical knowledge.

The toolkit is a set of skills for Claude. They help you turn a rough draft of a long document into a clear one. It can be a report, a paper or a thesis. You decide what the document says. The skills fix structure and style, and they catch what a tired eye misses.

Every change comes back to you as tracked changes in a copy of your Word file. You accept or reject each change in Word, as you would with a colleague's edits.

## The skills

1. doc-setup asks you a few questions and writes your profile: one page with your settings and style rules. You run it once.
2. doc-flow checks the structure of the whole document, moves sections after you agree, and writes a one-page document map.
3. human-write rewrites one section at a time in your style.
4. doc-check lists the top 10 issues before you send the document. It never changes anything.
5. notation-check, for a thesis only, keeps the math symbols the same across chapters.

The usual order: doc-setup once, then doc-flow, then human-write on each section that needs it, then doc-check. A thesis also gets notation-check before each milestone.

## What you need

1. A claude.ai account. Skills work on every plan: Free, Pro, Max, Team and Enterprise.
2. Code execution turned on. It is on by default. To check, open Settings, then Capabilities, and look for "Code execution and file creation". On a Team or Enterprise plan, your organization's owner controls this setting.
3. Microsoft Word, or another program that shows tracked changes, such as LibreOffice.
4. Your document as a Word file (.docx). A PDF or pasted text also works. You then get back a plain Word file without your own formatting.

## Step 1: install the skills

1. Open the toolkit's Releases page: https://github.com/tsb-buchanan/claude-writing-toolkit/releases
2. Under the latest version, download doc-setup.zip, doc-flow.zip, human-write.zip and doc-check.zip. For a thesis with math, also download notation-check.zip.
3. In claude.ai, open Customize, then Skills.
4. Upload each zip file, one at a time. Do not unzip them first.
5. Check that each skill is switched on.

[Screenshot 1: Customize, Skills, with the upload button circled]

On a Team or Enterprise plan, an owner can upload the skills once for everyone, under Organization settings, then Plugins & skills.

## Step 2: make a Project for your document

Make one Project per document. The Project holds two short things that every chat needs: your profile and the document map. It never holds the document itself.

1. Open Projects, and create a new Project. Name it after your document.
2. Leave its instructions and knowledge empty for now.

[Screenshot 2: a new Project, with the instructions box circled]

Why not put the document in the Project? It goes out of date after each round of changes. And Claude reads everything in a Project in every chat, which uses up your limits faster.

## Step 3: write your profile with doc-setup

The profile says who reads the document, what its key message is, what its parts are, and how you like to write.

1. Start a new chat in the Project.
2. Upload your document, and type: Use doc-setup.
3. Answer the questions. There are at most three rounds. Each question comes with a suggested answer. Reply "OK" to accept all the suggestions in a round.
4. Claude shows you the profile. Ask for changes until it is right. Then approve it.
5. Copy the profile. Open the Project, open its instructions, paste the profile, and save.

[Screenshot 3: the profile pasted into the Project's instructions]

If your plan has no Project instructions, add the profile file to the Project's knowledge instead.

## Step 4: fix the structure with doc-flow

doc-flow reads the whole document. It checks that the main message comes early, that each section does its job, and that nothing is repeated or in the wrong place.

1. Start a new chat in the Project. Upload the current Word file, and type: Use doc-flow.
2. Read the report. It ends with a numbered list of proposed moves.
3. Reply with the moves you want, such as "1, 3", or "all", or "none".
4. Claude gives you a copy of your file, named like yours with "-tracked" at the end. Download it.
5. Open it in Word. On the Review tab, accept or reject each change. Save it as your new version.
6. Claude also gives you doc-map.md, the document map. Add it to the Project's knowledge. If an older map is there, remove it.

[Screenshot 4: Word's Review tab, with Accept and Reject circled]

[Screenshot 5: the Project's knowledge, with doc-map.md added]

doc-flow never rewrites your sentences. It only moves, cuts or adds headings, and only the moves you choose.

If you only want the map, type: Use doc-flow, map only. That is the cheap way to give the other skills a map.

## Step 5: rewrite one section at a time with human-write

1. Start a new chat in the Project. Upload the current Word file, and type: Use human-write on the section "Results". Use the section's heading.
2. Claude gives you a tracked copy, and short lists: numbers whose format changed, sentences it removed, sentences whose meaning could have shifted, long sentences it kept, and notes for the other skills.
3. Read the lists first. Then open the copy in Word, and accept or reject each change.
4. A sentence that starts with [NEW] is new. It only restates what your document or map already says. Check it. Then delete the [NEW] mark, or reject the sentence.
5. Repeat in a new chat for the next section.

[Screenshot 6: a tracked copy in Word, with a [NEW] sentence]

For a light touch, type: Use human-write on "Results", light. It then fixes only voice, spelling, dashes, the way numbers are written, and the words your profile says to cut.

Some paragraphs cannot be changed safely in a Word file: tables, footnotes, equations and fields. Claude leaves them as they are, and puts its proposed text in the chat. Paste it in by hand if you want it.

## Step 6: check before you send with doc-check

1. Start a new chat in the Project. Upload the current Word file, and type: Use doc-check.
2. You get the top 10 issues, most important first. Each one gives its place, a short quote, why it matters, and the next step: a skill to run, or a decision for you.
3. doc-check never changes your document.

[Screenshot 7: a doc-check list in the chat]

doc-check also has a full mode, a deeper check with many parallel steps. It runs only in Claude Code, the version of Claude for the command line. On claude.ai, doc-check offers its quick check instead.

## For a thesis: keep the symbols consistent with notation-check

notation-check works on LaTeX or Markdown files. It lists every symbol, keeps a table of what each one means, and finds a quantity with two symbols, a symbol with two meanings, and a symbol used before it is defined.

1. Start a new chat in the Project. Upload the chapter files, including the chapter your profile names as the notation source. Type: Use notation-check.
2. Read the report. It ends with a numbered list of fixes.
3. Reply with the fixes you want, such as "1, 2", or "all", or "none".
4. Claude gives you corrected copies of the changed files, a list of each change, and notation.md, the symbol table. Add notation.md to the Project's knowledge. If an older one is there, remove it.

notation-check changes symbols only, and only inside math. A missing definition needs words, so it leaves that to you or to human-write. It cannot change a symbol inside an equation in a Word file: it lists those for you to change by hand. From a PDF it can give a report, but no fixes.

## Your notes and keep marks

You can steer the skills with comments in your Word file.

1. A comment that starts with "Note:" tells the skills something they must respect. For example, on a heading: "Note: keep this section here. The board asked for it." Your notes win over the skills' suggestions.
2. A comment that starts with "keep" marks a passage that must never be rewritten, such as a quotation from a contract.
3. A comment that starts with "keep light" marks a passage that may get small fixes only: voice, spelling, dashes, number format and words to cut.

[Screenshot 8: a Word comment that starts with "keep"]

## Save tokens and usage

Every plan has usage limits. Long chats, large files and file creation use them faster. These habits keep your use low.

1. Start a new chat for each step. The profile and the map carry what the next step needs.
2. Use Sonnet, the default model. Switch to Opus only for an important document, such as a final board report.
3. Rewrite one section per chat.
4. Keep the document out of the Project. Upload it only to the chat that needs it.
5. For a long document, copy the section you are working on into a new Word file, and upload only that. human-write then returns the tracked changes in that small file. Copy the result back into your document.
6. Install only the skills you use.

As a guide: one round of doc-flow, three sections of human-write and doc-check, on a 12-page report, costs about $0.40 on Sonnet at API prices. On a subscription, the same work counts against your plan's limits instead.

## What the skills never do

1. They never change the value of a number, a fact, a citation, an equation, a cross-reference or a quotation. Only the way a number is written may change, such as "twelve" to "12", and every such change is listed.
2. They never add a claim, a result or a citation. A new sentence only restates what your document already says, and it starts with [NEW].
3. They never rewrite a passage you marked keep.
4. They never change your file. You always get a copy with tracked changes, and you decide.
5. They never move material into another document.

## When something goes wrong

1. The skill does not start. Name it in your message, such as "Use human-write". Check that it is switched on under Customize, then Skills. Check that code execution is on under Settings, then Capabilities.
2. The upload fails. Use the zip file from the Releases page as it is. Do not unzip it and zip it again.
3. Claude does not know your settings. Check that the profile is in the Project's instructions, and that you started the chat inside the Project.
4. A paragraph was skipped. The tables, footnotes, equations and fields in a Word file stay as they are. The proposed text is in the chat.
5. Claude says a check failed, or the copy does not open. Do not use that copy. Start a new chat and try again.
6. Claude changed something it should not have. Reject that change in Word, and tell Claude in the chat.
7. The chat is long or slow. Start a new chat. The profile and the map are still there.
