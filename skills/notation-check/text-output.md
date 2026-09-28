# Text output

How to change a LaTeX, Markdown or text file. The writer sees every change before their own file changes. The scripts are in this skill's scripts/ folder.

## In Claude Code

1. Copy the file into drafts/ in the notes folder (doc-notes/ unless the profile says otherwise). Edit the copy, never the file. Keep any other files you need for checks in drafts/ too.
2. Run the skill's checks on the file and the draft.
3. Run `python3 scripts/word_diff.py FILE DRAFT`, so that the writer sees each change. If the diff is long, also give the draft's path, so that the writer can read it in their editor.
4. Give the skill's lists. Then wait for "approve", "approve except ...", or edits.
5. On "approve except ...", undo those changes in the draft. On edits, make them in the draft and show the diff again.
6. After approval, copy the draft over the file. Then delete the draft with `rm DRAFT`, as a command on its own.
7. Unless the profile says commit: no, commit only the changed files, with the message the skill gives. Never commit drafts/. Never push.
8. If the writer rejects the change, delete the draft the same way. The file stays as it was.
9. Before you say a file is written or deleted, check that the command worked.

## On claude.ai

1. Uploads are usually in /mnt/user-data/uploads/. Copy the file into your working folder, and edit the copy there.
2. Run the skill's checks on the file and the copy.
3. Run `python3 scripts/word_diff.py FILE COPY`. Give its output in the chat as it is, in a code block, then the skill's lists.
4. Save the copy with the outputs, usually /mnt/user-data/outputs/, under the file's own name. The writer's own file stays as it is until they replace it.
5. Tell the writer, in one line, to read the changes, then download the file and replace their own copy with it, or ask for edits.
