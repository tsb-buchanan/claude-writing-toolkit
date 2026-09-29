# The writing toolkit on claude.ai

This guide takes you from nothing to a clearer version of your own document, step by step, on claude.ai. You need no technical knowledge. The setup takes about 20 minutes, once.

The toolkit is a set of skills for Claude. They help you turn a rough draft of a long document into a clear one: a report, a paper or a thesis. You decide what the document says. The skills fix structure and style, and they catch what a tired eye misses.

Every change comes back to you as tracked changes in a copy of your Word file. You accept or reject each change in Word, as you would with a colleague's edits. Your own file never changes unless you save over it.

## The five skills

1. **doc-setup** asks you a few questions and writes your profile: one page with your settings and style rules. You run it once.
2. **doc-flow** checks the structure of the whole document, moves sections after you agree, and writes a one-page document map.
3. **human-write** rewrites one section at a time in your style.
4. **doc-check** lists the top 10 issues before you send the document. It never changes anything.
5. **notation-check** keeps the math symbols the same across the chapters of a thesis.

The order you will follow: doc-setup once, then doc-flow, then human-write on each section that needs it, then doc-check.

## What you need

1. A claude.ai account. Skills work on every plan: Free, Pro, Max, Team and Enterprise. Every plan has usage limits (see "Save usage" below).
2. A computer, with a web browser or the Claude desktop app. The phone app is fine for reading replies, but use a computer to upload skills and files.
3. Microsoft Word, or another program that shows tracked changes, such as LibreOffice.
4. Your document as a Word file (.docx). A thesis in LaTeX or Markdown also works. A PDF works too, but you then get back a plain Word file without your own formatting.
5. Nothing else to download. Part 1 adds the skills straight from the toolkit's page on GitHub. If that does not work for you, Part 1 also shows how to upload the skill files instead.

## Part 1: Install the skills (once)

First, open claude.ai. Open **Settings**, then **Capabilities**, and check that **Code execution and file creation** is switched on. It is on by default. On a Team or Enterprise plan, your organization's owner controls this setting.

Then pick one of two routes. Route A is quicker, and it keeps the skills up to date on its own. Use Route B only if Route A does not work for you.

### Route A: add the toolkit from GitHub

1. Open **Customize**: the left sidebar in the desktop app, or claude.ai/customize in the browser.
2. Open **Plugins**, then **Add**, then **Add marketplace**, then **Add from a repository**.
3. Type **tsb-buchanan/claude-writing-toolkit**, and click **Sync**.
4. Open the plugin **writing-toolkit**, and check that it is switched on. It holds all five skills.
5. Start a new chat, and type **/** in the message box. The five skills are listed, each with the plugin's name, writing-toolkit.

[Screenshot 1: Customize, Plugins, Add marketplace, with the repository name typed in]

On a Team or Enterprise plan, your organization's owner decides whether members can add a marketplace. If you cannot, use Route B.

### Route B: upload the skill files

1. Download the skill files from the toolkit's Releases page: https://github.com/tsb-buchanan/claude-writing-toolkit/releases. You need doc-setup.zip, doc-flow.zip, human-write.zip and doc-check.zip, and notation-check.zip for a thesis with math.
2. Open **Customize**, then **Skills**.
3. Click the upload button, and pick **doc-setup.zip**. Do not unzip the file first.
4. Repeat for **doc-flow.zip**, **human-write.zip** and **doc-check.zip**. For a thesis with math, also upload **notation-check.zip**.
5. Check that each skill is switched on.

[Screenshot 2: Customize, Skills, with the upload button circled]

On a Team or Enterprise plan, an owner can upload the skills once for everyone, under Organization settings, then Plugins & skills.

Use one route only. If you uploaded the skills before and now add the toolkit from GitHub, delete the uploaded skills under Customize, then Skills. With two copies of a skill, it is unclear which one runs.

## Part 2: Get your document ready (about 10 minutes, once)

A few small changes in Word make the skills work much better.

1. **Save a backup copy** of your document, and keep it somewhere safe.
2. **Use real headings.** Give each chapter and section title a heading style: select the title, then pick **Heading 1** (for chapters or main sections) or **Heading 2** (for subsections) on the Home tab. The skills find your sections by these styles. A title that is only bold text is not a section to them.
3. **Clear old tracked changes.** On the Review tab, accept or reject every change that is still there, then switch **Track Changes** off. The skills cannot edit a paragraph that already holds tracked changes.
4. **Mark what must never change.** Select the passage, add a comment (Review, New Comment), and start the comment with **keep**. For example: "keep: quoted from the contract". Use this for quotations, legal text and anything that is not yours to reword.
5. **Mark what may get small fixes only.** Start the comment with **keep light** instead. For example: "keep light: from my published paper". The skills then fix only voice, spelling, dashes, number format and the words your profile says to cut.
6. **Leave notes for the skills.** A comment that starts with **Note:** tells the skills something they must respect. For example, on a heading: "Note: keep this section here. The board asked for it." Your notes win over the skills' suggestions.
7. Save the file as .docx.

[Screenshot 3: a Word comment that starts with "keep"]

## Part 3: Make a Project for your document (once)

A Project holds two short things that every chat needs: your profile and the document map. It never holds the document itself.

1. Open **Projects**, and click **New project**. Name it after your document.
2. Leave its instructions and knowledge empty for now.

[Screenshot 4: a new Project, with the instructions box circled]

Why not put the document in the Project? It goes out of date after each round of changes. And Claude reads everything in a Project in every chat, which uses up your limits faster. Instead, you upload the latest version to each chat that needs it.

## Part 4: Write your profile with doc-setup (once, about 5 minutes)

1. Start a **new chat inside the Project**. The Project's name shows at the top of the chat.
2. Attach your Word file, and type: **Use doc-setup.**
3. Answer its questions. There are at most three rounds:
   1. The document: who reads it and what they need, the key message in one sentence (for a report, also the decision you ask for), and its parts.
   2. Your style: voice ("I" or "we"), spelling, the longest sentence you allow, words to cut, dashes and how to write numbers.
   3. Limits: passages that must never change, your house rules, and a length target. For a thesis, also the chapters based on papers, the chapter that sets your notation, and your next milestone.
4. Every question comes with a suggested answer, taken from your document where it can. Reply **OK** to accept all the suggestions in a round, or say only what differs.
5. Claude shows your profile. Ask for changes until it is right, then approve it.
6. Copy the profile. Open the Project, open its **Instructions**, paste the profile, and save.

[Screenshot 5: the profile pasted into the Project's instructions]

Take care with the key message: the other skills check your document against it. If your plan has no Project instructions, add the profile as a file to the Project's knowledge instead.

To change a rule later, start a new chat in the Project and type, for example: **Use doc-setup. Change my sentence limit to 20 words.** Then paste the new profile over the old one.

## Part 5: Fix the structure with doc-flow (once per document, or per chapter)

1. Start a new chat in the Project. Attach the current Word file, and type: **Use doc-flow.**
2. Read the report. It says where the main message sits, what each section does, what is repeated or in the wrong place, which numbers differ between sections, and which sections have the most long sentences. It ends with a numbered list of proposed moves.
3. Reply with the moves you want, such as **1, 3**, or **all**, or **none**. You can also change a move, for example: **all, but keep section 4 where it is.**
4. Claude gives you two files: a copy of your document named like yours with "-tracked" at the end, and **doc-map.md**, the document map. If the map does not come, type: **Now write the document map.**
5. Open the tracked copy in Word. On the Review tab, go through the changes one by one and accept or reject each. A moved paragraph shows as deleted in one place and inserted in the other.
6. Save it as your new version, for example "report v2.docx".
7. Add **doc-map.md** to the Project's knowledge. If an older map is there, remove it.

[Screenshot 6: Word's Review tab, with Accept and Reject circled]

[Screenshot 7: the Project's knowledge, with doc-map.md added]

doc-flow never rewrites your sentences. It only moves them, cuts duplicates and adds headings, and only the changes you approve. When two sections give different numbers, it tells you and fixes neither: you decide which one is right.

If you only want the map, type: **Use doc-flow, map only.**

## Part 6: Rewrite one section at a time with human-write

1. Start a new chat in the Project. Attach the latest version of your document, and type: **Use human-write on the section "Results".** Write the section's heading exactly as it appears in your document.
2. Claude gives you a tracked copy, and short lists:
   1. numbers whose format changed, such as "twelve" to "12";
   2. sentences it removed, and where their content went;
   3. sentences whose meaning could have shifted, old and new;
   4. long sentences it kept, and why;
   5. flags: things only you can fix, such as a paragraph that names nothing specific, and notes for the other skills.
3. Read the lists first, especially the sentences whose meaning could have shifted.
4. Open the tracked copy in Word, and accept or reject each change.
5. A sentence that starts with **[NEW]** is new. It only restates what your document or map already says. Check it, then delete the "[NEW] " mark, or reject the sentence.
6. Tables, footnotes, equations, fields and links stay as they are. When Claude would change one, it puts its proposed text in the chat instead. Paste it in by hand if you want it.
7. Save the result as your next version. For the next section, start a new chat and upload that version.

[Screenshot 8: a tracked copy in Word, with a [NEW] sentence]

For a light touch, type: **Use human-write on the section "Results", light.** It then fixes only voice, spelling, dashes, the way numbers are written, and the words your profile says to cut.

For a long document, copy the section you are working on into a new Word file, and upload only that. human-write then returns the tracked changes in that small file, and uses much less of your limits. Copy the result back into your document.

## Part 7: Check before you send with doc-check

1. Start a new chat in the Project. Attach the latest version, and type: **Use doc-check.**
2. You get the top 10 issues, most important first. Each gives its place, a short quote, why it matters, and the next step: a skill to run, or a decision for you.
3. Work through the list, then run doc-check again on the new version.

[Screenshot 9: a doc-check list in the chat]

doc-check never changes your document. Its full mode, a deeper check, runs only in Claude Code, the version of Claude for the command line.

## Part 8: For a thesis

1. Work one chapter at a time: doc-flow on one chapter, then human-write on its sections.
2. The map holds one block per chapter. Each doc-flow run replaces the block of its own chapter. Keep only the latest doc-map.md in the Project's knowledge.
3. A chapter based on a published paper should get small fixes only. Mark it with a "keep light" comment, or say so when doc-setup asks about papers.
4. To keep the math symbols consistent, use notation-check. It works on LaTeX or Markdown files:
   1. Start a new chat in the Project. Attach the chapter files, including the chapter that sets your notation. Type: **Use notation-check.**
   2. Read the report: one quantity with two symbols, one symbol with two meanings, and symbols used before they are defined. It ends with a numbered list of fixes.
   3. Reply with the fixes you want, such as **1, 2**, or **all**.
   4. Download the corrected files and **notation.md**, the symbol table. Add notation.md to the Project's knowledge.
5. notation-check changes symbols only, and only inside math. A missing definition needs words, so it leaves that to you or to human-write. It cannot change a symbol inside an equation in a Word file: it lists those for you to change by hand.

## Keep things up to date

1. After big changes, refresh the map: **Use doc-flow, map only.** Then replace the old doc-map.md in the Project's knowledge.
2. When your style rules change, rerun doc-setup (Part 4), and paste the new profile into the Project's instructions.
3. New versions of the toolkit: with Route A, they arrive on their own. To get one at once, open the plugin under Customize, then Plugins, and select **Check for updates**. With Route B, delete each old skill under Customize, then Skills, and upload the new zip. doc-setup offers to update an older profile.

## Save usage

Every plan has usage limits. Long chats, large files and file creation use them faster.

1. Start a new chat for each step. The profile and the map carry what the next step needs.
2. Use Sonnet, the default model. Switch to Opus only for an important document, such as a final board report.
3. Rewrite one section per chat.
4. Keep the document out of the Project. Upload it only to the chat that needs it.
5. For a long document, upload only the section you are working on (Part 6).
6. Install only the skills you use.

## Your document and privacy

Your document goes to claude.ai like any other upload. Before you upload confidential or unpublished work, check the rules of your organization or university.

## What the skills never do

1. They never change the value of a number, a fact, a citation, an equation, a cross-reference or a quotation. Only the way a number is written may change, such as "twelve" to "12", and every such change is listed.
2. They never add a claim, a result or a citation. A new sentence only restates what your document already says, and it starts with [NEW].
3. They never rewrite a passage you marked keep.
4. They never change your own file. You always get a copy with tracked changes, and you decide.
5. They never move material into another document or chapter.
6. They never cut or soften a limit you stated, such as a risk or a case where something did not work.
7. They never change your words just to sound more human, or to get past an AI detector. Every change follows a rule in the skill or in your profile.

## When something goes wrong

1. **The skill does not start.** Name it in your message, such as "Use human-write". Check that it is switched on: under Customize, then Plugins, for Route A, or under Customize, then Skills, for Route B. Check that code execution is on under Settings, then Capabilities.
2. **The toolkit will not sync.** Check that you typed tsb-buchanan/claude-writing-toolkit exactly. If it still fails, use Route B.
3. **A skill will not upload.** Use the zip file as it came. Do not unzip it and zip it again. If an older skill with the same name is there, delete it first.
4. **Claude does not know your settings.** Check that the profile is in the Project's instructions, and that you started the chat inside the Project.
5. **Claude cannot find a section.** Type the heading exactly as it appears, and check that it has a Heading style (Part 2).
6. **A paragraph was skipped.** Tables, footnotes, equations, fields and links in a Word file stay as they are. The proposed text is in the chat.
7. **No map after doc-flow.** Type: "Now write the document map."
8. **Claude says a check failed, or the copy does not open.** Do not use that copy. Start a new chat and try again.
9. **Claude changed something it should not have.** Reject that change in Word, and tell Claude in the chat.
10. **The chat is long or slow.** Start a new chat. The profile and the map are still there.
