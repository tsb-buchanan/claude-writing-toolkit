# Text output

How to change a LaTeX, Markdown or text file in Claude Code. The writer sees every change before the file changes.

1. Copy the file into drafts/ in the notes folder (doc-notes/ unless the profile says otherwise). Edit the copy, never the file. Keep any other files you need for checks in drafts/ too.
2. Run the skill's checks on the file and the draft.
3. Run `git diff --no-index --word-diff FILE DRAFT`, so that the writer sees each change. If the diff is long, also give the draft's path, so that the writer can read it in their editor.
4. Give the skill's lists. Then wait for "approve", "approve except ...", or edits.
5. On "approve except ...", undo those changes in the draft. On edits, make them in the draft and show the diff again.
6. After approval, copy the draft over the file. Then delete the draft with `rm DRAFT`, as a command on its own.
7. Unless the profile says commit: no, commit only the changed files, with the message the skill gives. Never commit drafts/. Never push.
8. If the writer rejects the change, delete the draft the same way. The file stays as it was.
9. Say that a file is written or deleted only after the command worked.
