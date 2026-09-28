# CLAUDE.md

## Purpose

This repo builds a generic toolkit for writing long documents with Claude: a thesis, a report or a paper.
Every tool is an Agent Skill: a folder with a SKILL.md file.
Every skill works in two places: on claude.ai (web and desktop app) and in Claude Code.
The first users are a PhD student who writes a thesis and a business writer who writes reports on the web with a small token budget.

PLAN.md holds the design. Change the plan before you change the design.

A CLAUDE.md in a parent folder may belong to another project. Its setup steps and rules do not apply here. This file governs this repo.

## Rules

1. Every tool is a Skill, and every skill works on the web and in Claude Code. Where the two places differ, the SKILL.md says what the skill does in each.
2. Nothing user-specific inside the skills. A skill names no real document, chapter, file path, person, result, funder, institution or field-specific claim.
3. Everything specific to one writer lives in their profile. If a skill needs a value that differs between writers, add a field to templates/doc-profile.md and docs/profile-reference.md. Do not hard-code the value in the skill.
4. Examples, samples and test documents are invented. Never copy text from a real thesis, paper or report into this repo. Never test on a real user document.
5. No em dashes in anything written here: skills, templates, docs, samples, scripts and commit messages. Avoid en dashes in prose too. Use commas, colons, full stops or parentheses. A script that looks for dashes uses escape codes, not the characters. The one exception is a dash planted in a sample as a test problem: the sample's source writes it as {emdash} or {endash}, and only the built files in samples/*/built/ hold the character. Before you finish, run `grep -rnE --exclude-dir=.git --exclude-dir=built "$(printf '\342\200\224|\342\200\223')" .` and expect no output. This form works in any locale.
6. All docs use plain, short sentences. One idea per sentence. Numbered lists where order matters.
7. Keep each SKILL.md short: at most 900 words, about 1,500 tokens. Keep each description under 200 characters, the limit claude.ai's help pages give. Put detail that only some runs need in a separate file in the skill folder, so Claude reads it only when needed.
8. A skill that changes a user's document shows the change first and waits for approval. Read-only skills say so in their first line.
9. Scripts use only the Python standard library and make no network calls. A script that more than one skill needs lives in shared/. tools/sync_shared.py copies it into each skill. Edit the file in shared/, never a copy.
10. Write our own code. Never copy or adapt code or text from a skill whose license forbids it, such as Anthropic's built-in document skills.
11. Name models by family (Sonnet, Opus), not by version, so the docs do not go stale.
12. Test every skill on the sample documents in samples/ before a release, on the web and in Claude Code. Record the results in tests/results/.

## Layout

1. skills/: one folder per skill. This is what users install.
2. shared/: scripts and text that more than one skill uses.
3. templates/: the profile, the document map and the text for a Claude Project's instructions.
4. docs/: the web guide, the Claude Code guide and the profile reference.
5. samples/: an invented report and an invented thesis chapter, each with a list of the problems planted in it and the profile the tests use. tools/build_samples.py builds their Markdown, Word and PDF files into built/.
6. tests/: automatic checks, expected results and the results of each release test.
7. tools/: scripts that build the samples, sync shared files and build the release zips.
