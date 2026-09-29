# The writing toolkit in Claude Code

This guide is for writers who keep their document in a git repository: a thesis in LaTeX or Markdown, or a report in Markdown, text or Word. The skills are the same as on claude.ai. In Claude Code they also save their notes in your repository, show changes as a diff, and commit after you approve.

## Install

Pick one of three ways.

1. On claude.ai, if you use Claude Code on the web. Add the toolkit on claude.ai, as docs/web-guide.md shows in Part 1, Route A. A cloud session has no `/plugin` command, and it does not install plugins from a repository's settings. It loads the skills you turned on at claude.ai, so every cloud session has the toolkit. A terminal signed in with the same claude.ai account gets it too, as a synced plugin.
2. As a plugin, in a terminal, straight from GitHub. In Claude Code, type `/plugin marketplace add tsb-buchanan/claude-writing-toolkit`, then `/plugin install writing-toolkit@writing-toolkit`, then `/reload-plugins`. Each skill then has the plugin's name in front, such as /writing-toolkit:human-write. This guide leaves the name out. New versions arrive when you run `/plugin marketplace update writing-toolkit`, or on their own once you turn on auto-update for the marketplace under Marketplaces in `/plugin`.
3. From the zip. Download writing-toolkit-skills.zip from the toolkit's Releases page: https://github.com/tsb-buchanan/claude-writing-toolkit/releases. Unzip it into .claude/skills/ in your repository, for this document only: `unzip writing-toolkit-skills.zip -d .claude/skills/`. Or unzip it into ~/.claude/skills/, for all your projects. For cloud sessions, commit the skill folders in .claude/skills/, because a cloud session starts from a fresh clone.

Then:

1. Start Claude Code in the repository, and type `/`. You should see doc-setup, doc-flow, human-write, doc-check and notation-check.
2. Install in one place only. If you added the toolkit on claude.ai with the same account, Claude Code already has it, as a synced plugin. Skills you uploaded on claude.ai show up with names such as anthropic-skills:human-write. Two copies of a skill make it unclear which one runs. Keep one of them.
3. The scripts need Python 3 and nothing else.

### Switch from an older copy

If a repository holds an older copy of the toolkit, or your own commands for the same jobs:

1. Add the new version first, in one of the ways above.
2. Delete the old skill folders from .claude/skills/: doc-setup, doc-flow, human-write, doc-check and notation-check. On claude.ai, delete the skills you uploaded, under Customize, then Skills.
3. Look at your own commands in .claude/commands/. Delete each one that does the same job as a toolkit skill, so that one tool does each job. Keep the rest.
4. Keep doc-profile.md. Version 1.1 reads it unchanged. If your own style notes hold rules that the skills should follow, add them to the profile's house rules with /doc-setup.
5. Check CLAUDE.md for lines that point to deleted commands, and update them.
6. Start a new session, type `/`, and check that each skill appears once.

## Set up once with /doc-setup

1. Type /doc-setup. It looks at your repository first: the main file, the chapter files and the format.
2. Answer at most three rounds of questions. Each question has a suggested answer, and "OK" accepts all the suggestions in a round.
3. It shows the profile. After you approve it, it writes doc-profile.md at the root of your repository.
4. It offers two lines for your CLAUDE.md, so that every session finds the profile. It adds them after you approve, and commits.

docs/profile-reference.md explains every field of the profile.

## The cycle

1. `/doc-flow chapters/ch3.tex`: a report on the structure, saved in doc-notes/plans/. Reply with the moves you approve. It shows the moves as a diff, and changes the file after your second approval. Then it writes the map, doc-notes/doc-map.md. `/doc-flow map only chapters/ch3.tex` writes just the map.
2. `/human-write chapters/ch3.tex "3.2"`: rewrites one section. Name the section by its heading or its number. Add "light" for small fixes only. It changes only what a rule in the skill or your profile asks for, never just to sound more human. docs/sources.md says where the rules come from.
3. `/notation-check`, for a thesis: the symbol table in doc-notes/notation.md, a report, and fixes to symbols in math after you approve.
4. `/doc-check chapters/ch3.tex`: the top 10 issues, saved in doc-notes/checks/. `/doc-check full` runs full mode (below).

Run doc-flow on one chapter at a time. Start a new session, or type /clear, between steps. The profile and the map carry what the next step needs.

## The files in doc-notes/

1. doc-map.md: the document map, written by doc-flow and read by the other skills.
2. notes.md: your own notes, one heading per part. The skills follow them.
3. notation.md: the symbol table, written by notation-check.
4. plans/: doc-flow reports.
5. checks/: doc-check reports.
6. drafts/: temporary copies while you decide. They are deleted after each decision and never committed. You can add doc-notes/drafts/ to your .gitignore.

The profile's `notes_dir` can move this folder.

## Approvals and commits

1. Nothing in your document changes before you approve. Reply "approve", "approve except 2 and 5", or describe the edits you want.
2. Each run that writes files makes one commit, with a message that names the skill. The skills never push. Set `commit: no` in the profile to commit yourself.
3. A Word file in the repository gets a copy next to it, with the changes tracked, named like yours with "-tracked" at the end. Open it in Word, accept or reject each change, save it as your file, and commit it yourself.

Your notes and keep marks steer the skills:

1. LaTeX: `% keep` or `% keep light` on its own line, then `% end keep` after the passage. A note: `% Note: keep this section here.`
2. Markdown: `<!-- keep -->` or `<!-- keep light -->`, then `<!-- end keep -->`. A note: `<!-- note: ... -->`.
3. Word: a comment that starts with "keep", "keep light" or "Note:".

A keep passage is never rewritten. A keep light passage gets only small fixes: voice, spelling, dashes, number format and words to cut.

## Models and cost

1. Use Sonnet by default (`/model sonnet`). Use Opus for an important chapter or report, and for full mode.
2. The profile's `budget` is `auto`, `lean` or `standard`. `auto` is standard for a thesis in Claude Code, and lean otherwise. Standard lets human-write read the whole chapter and doc-flow write a longer report.
3. The costs measured in the tests, on Sonnet at API list prices: human-write $0.20 to $0.45 per section, doc-flow $0.25 to $0.40 for the report and about as much again for the moves, doc-check quick $0.25 to $0.40, notation-check about $0.20. Each reply you send costs a little more. On a subscription, the same work counts against your plan's limits instead.

## Full mode

`/doc-check full` checks a whole thesis or a long report in depth. It is meant for Opus.

1. It gives an estimate of the cost and asks before it starts. In the tests, a short sample cost about $2.50 to $3 on Opus.
2. One subagent per chapter extracts the claim, the sections, the numbers, the terms, the symbols, the sources and the handoffs, on Sonnet.
3. One subagent per kind of check reviews the whole document: message, structure, repetition, numbers, terms, notation, sources, style and house rules.
4. Other subagents try to disprove each finding by reading the places it cites. Only the findings that survive reach the report, and the rejected ones are listed.
5. The report, in doc-notes/checks/, groups findings as blocking before your milestone, major and minor. It compares them with the previous full report: new, fixed and still open.

It never changes your document.

## When something goes wrong

1. A skill does not appear. Check that the folder is .claude/skills/NAME/SKILL.md, and restart Claude Code.
2. Claude Code asks for permission to run python3, git, cp or rm. The skills run their own scripts and git. Allow them, or add them under /permissions.
3. There is no profile, or the skill does not follow it. Run /doc-setup, and check that doc-profile.md is at the root of the repository.
4. The map no longer matches the headings. Run `/doc-flow map only FILE`.
5. A draft is left in doc-notes/drafts/. Nothing was applied. Delete it.
6. Claude says a check failed. Your file did not change. Ask it to show what the check reported.
