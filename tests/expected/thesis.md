# Expected results: sample thesis chapter

What each skill must do on the sample chapter. The IDs (TH01 and so on) come from samples/thesis/planted.md.
Record each run in tests/results/<version>.md as pass or fail, with notes.

## Setup

1. Claude Code (the main place for this sample): a scratch git repo with the files of samples/thesis/ (main.tex, ch2-background.tex, ch3-desks.tex, refs.bib, doc-profile.md). One new session per run.
2. Web: a claude.ai Project with samples/thesis/doc-profile.md in its instructions, without its Claude Code part. Upload ch3-desks.tex (and ch2-background.tex for notation-check), or built/thesis.pdf where a run says so. One new chat per run.
3. Model: Sonnet, unless a run says otherwise.
4. The map: runs before doc-flow exists use no map. Once doc-flow exists, repeat the human-write runs with its map.

## doc-setup

Claude Code: `/doc-setup` in the scratch repo, with doc-profile.md removed.
When asked, give the key message, notation source, milestone and house rule from samples/thesis/doc-profile.md. Accept the defaults for everything else.

Must:

1. Finish in three rounds of questions or fewer.
2. Find the chapters from main.tex, with their files, and detect LaTeX, UK spelling and the voice "I".
3. Find the keep light passage in 3.4 (TH06) and mention it.
4. Write a profile of at most about 450 words that matches samples/thesis/doc-profile.md in mode, parts, spelling, voice, house rule and the Thesis part.

## human-write

### Run 1: section 3.3, "Waiting times"

Must change:

1. Cut "It is worth noting", "clearly" and "very" (TH15).
2. Split the 63-word sentence (TH16) without touching Equation eq:wq.
3. Cut the closing comment on what the result means (TH20), and list it as removed.
4. Replace "half asleep" (TH18) with literal words from what the paragraph reports, or flag it. Add no new number.

Must flag, not change: $N$ in Equation eq:little and in "$N = 0.67$" (TH03), for notation-check.

Must not: invent a citation for "Earlier studies" (TH19). Flagging it for the writer is right.

Must leave alone:

1. Equations eq:w, eq:wq and eq:little, byte for byte.
2. \cite{example2021}, \eqref{eq:erlang2}, \ref{sec:logs} and every \label.
3. The two terms "waiting time" and "time in system" (TH12). They stay distinct.
4. The values 0.4/12, 2.0, 0.67 and 3 minutes.

### Run 2: section 3.4, "A staffing rule" (keep light)

Must change, by light passes only:

1. "We propose" becomes a sentence in the thesis voice that credits the supervisor, for example "My supervisor and I propose" (TH06).
2. Cut "clearly" (TH15).

Must leave alone:

1. Every other word.
2. The 44-word sentence, listed as kept, with the reason: the passage is marked keep light.
3. \cite{writer2025}, \eqref{eq:wq}, $\lambda < 10$, and the lines % keep light and % end keep.

### Both runs

1. Every new sentence starts with [NEW].
2. check_protected.py finds no change to math, citations, references or number values.
3. In Claude Code: nothing is written before approval. After approval, the file changes and one commit follows.

## doc-flow (on ch3-desks.tex)

Must find, in its report:

1. The claim only at the end (TH01). It proposes a fix: a structural move, or sentence work for human-write, which can restate the claim from 3.6 in 3.1 as a [NEW] sentence. Moving the whole paragraph out of 3.6 would leave the conclusion without its claim, so the second fix is the better one.
2. The repeated paragraph (TH08). It proposes to cut one copy, and says which place keeps it and why. planted.md keeps the first, but keeping the copy in 3.5, next to the table that uses it, is also sound.
3. The broken handoff (TH09).
4. The result in the method section (TH10).
5. The equation in the first section (TH13), against the house rule.
6. The long-sentence rate per section.

Must not:

1. Restructure anything inside the keep light section 3.4.
2. Move material into another chapter.
3. Rewrite any sentence.

The map:

1. Has one block for Chapter 3, at most one page.
2. States the chapter's claim and has one line per section.
3. Lists the key numbers: 20 returns per hour per desk, one desk up to 10 returns per hour, two desks up to about 28, and 2.0, 0.76 and 1.3 minutes predicted against 2.1, 0.9 and 1.7 observed.
4. Lists "waiting time" and "time in system" as two different key terms.

## doc-check quick (on ch3-desks.tex)

The seven issues its checklist should find, in any order:

1. TH01: the claim is not up front.
2. TH17 and TH19: the claim without a source, and the pointer to "earlier studies". One line for both is fine. The item counts only if TH19 is there.
3. TH07: the voice slips.
4. TH15: the banned words.
5. TH16: the long sentences.
6. TH11: the en dash range.
7. TH14: "2 desks".

Pass: at least 6 of the 7 appear. It must not report TH12 (the two terms) or a missing contribution statement. It must not ask to rewrite the long sentence in the keep light passage. Nothing is written to the document.

## doc-check full (Claude Code only)

Opus. Run it on the whole sample (Chapters 2 and 3), twice: first as it is, then after fixing TH02 and TH11 by hand.

1. The first report finds every problem in planted.md, grouped by severity, with "committee draft" in the blocking label.
2. The verify step rejects the false alarm (TH12), and the report lists it as rejected.
3. No finding claims that one of the model's numbers is wrong. planted.md shows that they are consistent.
4. The second report lists TH02 and TH11 as fixed.

## notation-check

Run it on Chapters 2 and 3. Chapter 2 is the notation source.

Must report:

1. The variant $\Lambda$ for $\lambda$ (TH02).
2. The clash: $N$ as the number of desks and as the mean number of borrowers (TH03). It proposes a new symbol for the second meaning, such as $L$, and marks the choice as the writer's decision.
3. $W$ used before its definition in Chapter 3 (TH04). The fix is text, so it is reported, not applied.

The symbol table has rows for $\lambda$, $\mu$, $N$, $\rho$, $P_w$, $W_q$ and $W$, with meanings and the places they are defined.

After approval of the fixes for TH02 and TH03:

1. $\Lambda$ becomes $\lambda$ in Equation eq:saturday.
2. $N$ becomes the approved symbol in Equation eq:little and in "$N = 0.67$".
3. Nothing else changes: no text outside math, nothing in Chapter 2, no other symbol.
