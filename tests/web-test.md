# The claude.ai part of a release test

CLAUDE.md asks for a test of every skill on the web and in Claude Code before a release. This is the web part. It takes about an hour. Record each run as pass or fail in tests/results/, with a line of notes.

What each run must find, change and leave alone is in tests/expected/report.md and tests/expected/thesis.md.

## Before you start

1. In claude.ai, open Customize, then Skills, and Customize, then Plugins. Remove older copies of the toolkit's skills, and any test skill such as docx-spike.
2. Install the version under test. Once it is on main, add the marketplace: Customize, Plugins, Add, Add marketplace, Add from a repository, `tsb-buchanan/claude-writing-toolkit` (docs/web-guide.md, Part 1, Route A). Before that, use the zips: download them from the latest run of the "checks" workflow on GitHub (Actions, the run, Artifacts), or build them with `python3 tools/build_release.py`, and upload them.
3. Check that the five skills are switched on.
4. Make a Project named "Toolkit test: report". Paste samples/report/doc-profile.md into its instructions.
5. Make a Project named "Toolkit test: thesis". Paste samples/thesis/doc-profile.md into its instructions.
6. Use Sonnet. Start a new chat for every run.

## The runs

In the report Project, upload samples/report/built/report.docx in each chat:

1. "Use doc-setup." Run it in a third Project with empty instructions. Answer with the key message from samples/report/doc-profile.md, and accept the rest.
2. "Use doc-flow." Approve all moves. Open the tracked copy in Word: accept all, then undo, then reject all. Add doc-map.md to the Project's knowledge.
3. "Use human-write on the section How the pilot worked." Open the tracked copy in Word, and check that the keep clause and the footnote did not change.
4. "Use human-write on the section Results." Check that "totes" became "crates", because the map is now in the Project.
5. "Use doc-check." Count how many of the eleven expected issues appear.
6. "Use doc-check full." It must say that full mode needs Claude Code, and offer quick mode.
7. "Use notation-check." It must say that it is for theses, and stop.

In the thesis Project, upload samples/thesis/ch2-background.tex and samples/thesis/ch3-desks.tex in each chat:

1. "Use human-write on section 3.3 of ch3-desks.tex." It must keep every equation, citation and reference. On the web, it returns a Word file built from the section, so check the lists and the tracked copy.
2. "Use notation-check." Approve fixes for $\Lambda$ and for $N$. Check the corrected ch3-desks.tex: only the three math places changed.
3. "Use doc-check on ch3-desks.tex." Count how many of the seven expected issues appear.

## The short test for version 1.1

Version 1.1 changed human-write and doc-check only, so three runs cover it. Set up as above, with the 1.1 zips. No map is needed.

1. Report Project, report.docx: "Use human-write on the section Results." Check three things. "choked" (RP22) became literal words, or is flagged. The comment "This result shows the wider promise of reuse" (RP23) is cut, and listed as removed. The limit in Cost per order, paragraph 3 (the crates may wear out before 200 uses) is still there.
2. Report Project, report.docx: "Use doc-check." "In addition," opening three paragraphs (RP20) and "Earlier studies" (RP21) appear. Count how many of the eleven expected issues appear.
3. Thesis Project, ch2-background.tex and ch3-desks.tex: "Use human-write on section 3.3 of ch3-desks.tex." "half asleep" (TH18) became literal words from the paragraph, or is flagged, with no new number. The comment "This result shows the wider value of queueing models" (TH20) is cut. No citation was invented for "Earlier studies" (TH19).

## What to note in each run

1. Pass or fail against tests/expected/.
2. Any em dash in the chat or in a file.
3. Anything written before you approved.
4. The usage the run took, if your plan shows it.
