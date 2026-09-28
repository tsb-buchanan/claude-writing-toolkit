# The claude.ai part of a release test

CLAUDE.md asks for a test of every skill on the web and in Claude Code before a release. This is the web part. It takes about an hour. Record each run as pass or fail in tests/results/, with a line of notes.

What each run must find, change and leave alone is in tests/expected/report.md and tests/expected/thesis.md.

## Before you start

1. Get the test build: the zips and web-guide.docx. Download them from the latest run of the "checks" workflow on GitHub (Actions, the run, Artifacts), or build them with `python3 tools/build_release.py`.
2. In claude.ai, open Customize, then Skills. Remove older copies of the toolkit's skills, and any test skill such as docx-spike.
3. Upload the five skill zips. Check that each one is switched on.
4. Make a Project named "Toolkit test: report". Paste samples/report/doc-profile.md into its instructions.
5. Make a Project named "Toolkit test: thesis". Paste samples/thesis/doc-profile.md into its instructions.
6. Use Sonnet. Start a new chat for every run.

## The runs

In the report Project, upload samples/report/built/report.docx in each chat:

1. "Use doc-setup." Run it in a third Project with empty instructions. Answer with the key message from samples/report/doc-profile.md, and accept the rest.
2. "Use doc-flow." Approve all moves. Open the tracked copy in Word: accept all, then undo, then reject all. Add doc-map.md to the Project's knowledge.
3. "Use human-write on the section How the pilot worked." Open the tracked copy in Word, and check that the keep clause and the footnote did not change.
4. "Use human-write on the section Results." Check that "totes" became "crates", because the map is now in the Project.
5. "Use doc-check." Count how many of the ten expected issues appear.
6. "Use doc-check full." It must say that full mode needs Claude Code, and offer quick mode.
7. "Use notation-check." It must say that it is for theses, and stop.

In the thesis Project, upload samples/thesis/ch2-background.tex and samples/thesis/ch3-desks.tex in each chat:

1. "Use human-write on section 3.3 of ch3-desks.tex." It must keep every equation, citation and reference. On the web, it returns a Word file built from the section, so check the lists and the tracked copy.
2. "Use notation-check." Approve fixes for $\Lambda$ and for $N$. Check the corrected ch3-desks.tex: only the three math places changed.
3. "Use doc-check on ch3-desks.tex." Count how many of the seven expected issues appear.

## What to note in each run

1. Pass or fail against tests/expected/.
2. Any em dash in the chat or in a file.
3. Anything written before you approved.
4. The usage the run took, if your plan shows it.
