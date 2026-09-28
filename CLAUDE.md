# CLAUDE.md

## Purpose

This repo is a generic toolkit for writing a thesis or a long paper with Claude Code.
It holds slash commands, templates, a setup prompt and a tutorial.
Any writer can install it into their own repo and use it on their own document.

PLAN.md holds the design. Change the plan before you change the design.

A CLAUDE.md in a parent folder may belong to another project. Its setup steps and project rules do not apply here. This file governs this repo.

## Rules

1. Nothing project-specific in the tools. Commands, templates and docs name no real chapter, file path, person, result, funder, institution or field-specific claim.
2. Everything specific to one writer's work lives in their project_profile.md. The writer fills it in, or the setup prompt writes it from an interview. The commands read it.
3. If a command needs a value that differs between projects, add a field to the profile template. Do not hard-code the value in the command.
4. Examples in commands, templates and docs are invented and generic. Never copy text from a real thesis or paper into this repo.
5. No em dashes anywhere in this repo. Use commas, colons, full stops or parentheses. Avoid en dashes in prose too. Check with `grep -rnP '\x{2014}|\x{2013}' .` before you finish.
6. Docs use plain, short sentences. One idea per sentence. Numbered lists where order matters.
7. Every command that edits a user's file shows a diff first and waits for approval. Read-only commands say so at the top.

## Layout

1. commands/: the slash commands, as Markdown files a user copies into .claude/commands/.
2. templates/: files the setup prompt copies into a user's repo, including project_profile.md.
3. docs/: the tutorial and reference docs.
4. setup/: the paste-in setup prompt for a new user.
