# doc-check full mode

Claude Code only. It checks a whole thesis or a long report with subagents, so it costs more than quick mode. It is meant for Opus. The extract step runs on Sonnet.

It stays read-only: no subagent changes a file. The only file written is the report.

## 1. Before you start

1. Read the profile and the map. List the files: for a thesis, the chapter files in the profile's parts; for a report, its one file.
2. Run `python3 scripts/doc_stats.py FILE --limit N --banned "WORDS"` on each file. Keep the output: the style reviewer needs it, and it gives the word count.
3. Estimate the cost at API list prices: on Opus, $3 plus $0.10 per 1,000 words; on Sonnet, $1.50 plus $0.06 per 1,000 words. Most of the fixed part is the subagents' own start-up.
4. Tell the writer the files, the words, the estimate, and that it takes several minutes. Ask: "Start the full check?" Wait for yes.
5. Find the previous full report: the newest doc-notes/checks/*-full.md, if there is one.

## 2. Extract

Launch one subagent per file, all at once, with model sonnet. For a report of one file, launch one. Give each this prompt, filled in:

> Read FILE, one part of a DOCUMENT KIND. Change no file. Reply in plain text, in at most 600 words, with these headings. Give a place (section and paragraph, or line) for every item.
> 1. CLAIM: the main message or the chapter's claim, quoted.
> 2. SECTIONS: one line per section: its heading and its job.
> 3. NUMBERS: each number a reader must get right: the value, what it is, where.
> 4. TERMS: each key term, and any other name used for the same thing.
> 5. SYMBOLS: each math symbol, what it stands for, and where it is first used.
> 6. SOURCES: claims about the world beyond this work that have no citation, and pointers such as "previous studies" that name no work.
> 7. HANDOFFS: lines that point to another section or chapter, and what they say is there.

## 3. Review

Launch one subagent per dimension, all at once, with the session's model:

1. Message: the main message or each chapter's claim, and the profile's opening rule.
2. Structure and handoffs.
3. Repetition.
4. Numbers: across sections and chapters, and against the map.
5. Terms: against the map's key terms.
6. Notation, in thesis mode only: symbols across chapters, against the notation source.
7. Claims and sources, including pointers such as "previous studies" that name no work.
8. Style and voice: the profile's style guide, with the doc_stats.py output, including the openings that start three or more paragraphs.
9. House rules, and in thesis mode with `contribution: yes`, who did what in a chapter based on a paper.

Give each this prompt, filled in:

> You check one thing in a DOCUMENT KIND: DIMENSION. The writer's profile: PROFILE. The document map: MAP, or "none". What each file holds: EXTRACTS. The files: FILES. Read the files wherever you need evidence. Change no file.
> Report at most 8 findings, most important first. For each give: PLACE (file, section, and paragraph or line), QUOTE (the exact words, at most 15), PROBLEM (one line), SEVERITY (blocking, major or minor), NEXT (the skill or the writer's decision that fixes it).
> Leave out: anything inside a keep passage; in a keep light passage, anything a light pass cannot fix; a term or symbol that the text defines as a separate thing; anything you have not seen in the text. Report nothing rather than guess.

Severity:

1. Blocking: the document should not reach the milestone with it: a number that differs between places, a missing or buried main message, a claim the argument rests on with no source, a reference that points to the wrong place.
2. Major: it hurts the reader: structure, repetition, handoffs, terms, notation, voice.
3. Minor: style: long sentences, words to cut, dashes, number format.

## 4. Verify

Merge findings that name the same place and problem. Group the rest by file, in batches of at most five. Launch one subagent per batch, all at once, with the session's model. Give each this prompt, filled in:

> Try to disprove each finding below. Read the cited place in FILE and what is around it, and search the other files where that helps. Change no file.
> For each finding, answer CONFIRMED, REJECTED or CHANGED, with one line of reason. REJECTED: the quote is not in the file, or the text settles it, for example a term defined as a separate measure, or a label defined in another file. CHANGED: the finding holds, but its place, quote or severity needs a correction; give the correction.
> FINDINGS

Only confirmed and changed findings reach the report.

## 5. The report

Save it as doc-notes/checks/DATE-full.md, with the date as YYYY-MM-DD, or in the profile's notes folder. If that file exists, add a number, such as DATE-full-2.md. Never overwrite an earlier report. Use these headings:

1. Summary: at most five lines.
2. Blocking before MILESTONE (the profile's milestone; for a report without one, "before it goes out"). Each finding: its place, the quote, the problem, and the next step.
3. Major.
4. Minor. Merge findings of one kind into one line.
5. Compared with DATE: the previous full report. Three lists: new, fixed (in the old report, not found now), and still open. Leave this out if there is no previous report.
6. Rejected by the verify step: one line each.

Unless the profile says commit: no, commit only that file, with the message "doc-check: full check". Never push. Before you say the file is saved, check that the command worked.

In the chat, give the summary, the blocking findings, the file's path, and the actual cost if you know it.
