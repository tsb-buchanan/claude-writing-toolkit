# Spike results

Build step 1 of PLAN.md, run on 28 September 2026.
The claude.ai column waits for the test in README.md.

## The five questions

| Question | Claude Code | claude.ai |
|---|---|---|
| 1. Which frontmatter fields are accepted besides name and description? | all we tried: license, metadata (version) and argument-hint | waiting |
| 2. Does a bundled script run and return a Word file? | yes | waiting |
| 3. Does an uploaded Word file's whole text enter the context? | no: files stay in the repo and are read with tools | waiting |
| 4. Does the Word file itself reach the script, with its comments? | yes | waiting |
| 5. Do the tracked changes open cleanly? | yes in LibreOffice 24.2; Word waits for the claude.ai test | waiting |

## Claude Code

1. A fresh Claude Code session (version 2.1.283) on Sonnet, with the skill in .claude/skills/. The prompt: "Run the docx spike on spike/dist/spike-sample.docx."
2. It found the skill, and found the script through `${CLAUDE_SKILL_DIR}`. It read the file, wrote the changes file and applied three changes. All three self-checks passed.
3. Sonnet's rewrite cut the filler, kept every fact, and kept the bold and italic words.
4. Cost: 8 model calls in 22 seconds, $0.13 at API list prices. Output was 2,090 tokens, or $0.02. The rest was Claude Code's own instructions, about 40,000 tokens per call, mostly read from the cache.

## The script on its own

1. It ran on the sample, and on a copy saved by LibreOffice, which writes its Word files differently. Both times it applied 3 of 3 changes and refused 2 bad ones with a reason: a paragraph that holds a comment, and a paragraph that did not start with the expected words.
2. Self-checks: rejecting all changes gives the original text; accepting all changes gives the requested text; every other part of the file stays the same.
3. LibreOffice 24.2 opens both results. It finds 13 tracked changes by "Claude" (8 deletions, 5 insertions) and keeps all 3 comments. Bold and italic words keep their formatting.

## Lessons for the real script

1. Numbering table cells as paragraphs is correct but noisy. The real read command should group the cells under their table.
2. LibreOffice writes an explicit "Normal" style. The real read command should show it as body text.
3. Inserted text takes the paragraph's most common formatting. Check this on more documents.
4. A paragraph that holds a comment cannot be rewritten yet. The real script should keep the comment on the rewritten paragraph.
5. This container had LibreOffice without its Writer part. Test machines need libreoffice-writer and poppler-utils.
6. Claude Code's own overhead (about $0.11 per short session on Sonnet) costs more than the skill's output. Section 10.4 of PLAN.md now uses this number.
