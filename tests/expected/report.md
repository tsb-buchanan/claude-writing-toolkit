# Expected results: sample report

What each skill must do on the sample report. The IDs (RP01 and so on) come from samples/report/planted.md.
Record each run in tests/results/<version>.md as pass or fail, with notes.

## Setup

1. Web: a claude.ai Project with samples/report/doc-profile.md pasted into its instructions. Upload samples/report/built/report.docx in each chat. One new chat per run.
2. Claude Code: a scratch git repo with samples/report/built/report.md and samples/report/doc-profile.md at its root. One new session per run.
3. Model: Sonnet, unless a run says otherwise.
4. The map: runs before doc-flow exists use no map. Once doc-flow exists, repeat the human-write runs with its map.

## doc-setup

Run it without a profile. Web: upload report.docx and say "Use doc-setup." Claude Code: `/doc-setup` in the scratch repo, with doc-profile.md removed.
When asked for the key message, give the one in samples/report/doc-profile.md. Accept the defaults for everything else.

Must:

1. Finish in three rounds of questions or fewer.
2. Propose mode report, the six sections, US spelling and the voice "we".
3. Propose the quoted clause (RP13) as a keep passage.
4. Write a profile of at most about 450 words that matches samples/report/doc-profile.md in mode, parts, spelling, voice and keep.
5. Leave out the Thesis part. On the web, leave out the Claude Code part too.
6. On a rerun that asks for a 20-word sentence limit, show a diff and change only that rule.

Must not: copy document text into the profile, other than the headings and the key message.

## human-write

### Run 1: "How the pilot worked"

Must change:

1. Cut the signpost (RP08).
2. Write "12 weeks" for "twelve weeks" and "three staff" for "3 staff" (RP15), and list both as number format changes.
3. Lead each paragraph with its claim, and cut filler.

Must flag, not change: the result in paragraph 7 (RP17), for doc-flow.

Must leave alone:

1. The keep passage (RP13), byte for byte, including "twenty-four months".
2. The footnote and its reference (RP18). On the web, the script refuses that paragraph, and its proposed text goes into the chat.
3. The value of every number in the section.

Must list: the number changes, the removed sentences and where their content went, any sentence whose meaning could have shifted, and any sentence over 25 words that it keeps, with a reason.

### Run 2: "Results"

Must change:

1. Cut "It is important to note that", "basically" and "leverage" (RP06).
2. Split the 54-word and 51-word sentences (RP07), or keep them with a reason.
3. Cut the recap (RP09).
4. Write "we" for "I think" (RP16).
5. With a map: write "crates" for "totes" (RP04). Without a map: flag it.

Must flag, not change:

1. The repeated paragraph (RP05), for doc-flow.
2. The broken handoff (RP10). It must not invent a new handoff sentence.

Must leave alone: the table (RP18) and the value of every number in the section.

### Both runs

1. Every new sentence starts with [NEW].
2. On the web: a Word file comes back with tracked changes by "Claude". It opens in Word and LibreOffice. Nothing outside the section changes. The bold words keep their bold.
3. In Claude Code: nothing is written before approval. After approval, the file changes and one commit follows.
4. The chat text besides the lists stays under 100 words.

## doc-flow

Must find, in its report:

1. The buried main message (RP01). It proposes a structural fix: move the recommendation's first paragraph to the start of the Summary, or move the whole Recommendation section to follow the Summary.
2. The repeated paragraph (RP05). It proposes to cut the copy in Results.
3. The broken handoff (RP10).
4. The result in the method section (RP17).
5. The two number conflicts (RP02, RP03). It reports them and fixes neither.
6. The long-sentence rate per section, and condensing options with word savings.

Must follow the writer's note (RP14): "Options we rejected" stays where it is. The report says what the skill would otherwise have suggested.

Must not: rewrite any sentence; change the keep passage (RP13); move material into another document.

After approval of the moves:

1. Only structural moves happen: reorder, cut the duplicate, add headings if proposed.
2. check_protected.py confirms that no number or fact is lost.
3. Every removed passage is listed with where its content went.

The map:

1. Fits on one page.
2. States the recommendation as the main message.
3. Has one line per section.
4. Lists the key numbers with their places: 18,900 orders (with the 18,400 conflict), $1.42 and $0.98 per order (31%), 96% returned, 81% preferred (with the 84% conflict), $304,000 up front, payback in about 15 months.
5. Lists "crates" as the key term, with "totes" as the variant to avoid.

## doc-check quick

The ten issues its checklist should find, in any order:

1. RP01: the main message is not up front.
2. RP02: 18,400 against 18,900 orders.
3. RP03: 84% against 81%.
4. RP11: the claim without a source.
5. RP04: "totes" and "crates".
6. RP07: the long sentences.
7. RP06: the banned words.
8. RP08 and RP09: the signpost and the recap, as one style issue or two.
9. RP12: the em dash.
10. RP15: the number format slips.

RP16 (the voice slip) may appear in place of one of them.

Pass: at least 8 of the 10 appear, and no more than 10 issues are shown. Each issue gives its section, a short quote, why it matters and a next step. Nothing is written to the document. In Claude Code, the report is saved in doc-notes/checks/.

## doc-check full (Claude Code only)

Opus. Run it twice: first on the sample as it is, then after fixing RP02 and RP12 by hand.

1. The first report finds every problem in planted.md, grouped by severity.
2. The second report lists RP02 and RP12 as fixed and the rest as still open.
3. Only findings that survive the verify step reach the report.
4. It states its cost estimate and asks before it starts.

## notation-check

Report mode: it says that it is for theses, and stops.
