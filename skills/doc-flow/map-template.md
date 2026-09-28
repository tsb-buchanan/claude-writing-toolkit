# Document map

How doc-flow writes the document map. human-write and doc-check read the map instead of the whole document. No other skill changes it.

## Rules

1. One page for a report. For a thesis, one block of at most one page per chapter.
2. A thesis map holds one block per chapter. doc-flow replaces the block of the chapter it ran on, and leaves the other blocks alone.
3. Write what the document says now, after the moves the writer approved. Quote the main message or claim closely.
4. Key numbers: the numbers a reader must get right, such as results, totals, costs and targets. Give each place where one appears. When two places disagree, write both values and mark the conflict. Do not decide which one is right.
5. Key terms: the term the document should use, and the variants to avoid. Two terms for two different things are both key terms, each with a line on what it means.
6. No other content: no advice, no findings and no text copied beyond the main message.

## The format for a report

```
# Document map
toolkit: 1.0
written: YYYY-MM-DD
document: FILE NAME OR TITLE

## Main message
The message, in one or two sentences, and the decision it asks for.
Stated in: SECTION, paragraph N.

## Sections
1. HEADING: its job, in one line.

## Key numbers
| Value | What it is | Where |
|---|---|---|
| VALUE | WHAT | SECTION, paragraph N |

## Key terms
| Use | Avoid | Meaning |
|---|---|---|
| TERM | VARIANTS | one line |
```

## The format for a thesis

```
# Document map
toolkit: 1.0
document: THESIS TITLE

## Chapter N: TITLE
written: YYYY-MM-DD
file: FILE
claim: the chapter's claim, in one or two sentences. Stated in: SECTION.

### Sections
1. N.1 HEADING: its job, in one line.

### Key numbers
| Value | What it is | Where |
|---|---|---|

### Key terms
| Use | Avoid | Meaning |
|---|---|---|
```

## An invented example

Every name and number below is made up.

```
# Document map
toolkit: 1.0
written: 2026-03-02
document: pool-hours-review.docx

## Main message
Open the Northgate pool until 21:00 on weekdays from May, because evening swims now fill 90% of their slots. The council is asked to approve $48,000 a year for staff.
Stated in: Summary, paragraph 1.

## Sections
1. Summary: gives the proposal, the cost and the decision needed.
2. Demand: shows that evening slots are full and that people are turned away.
3. Options: compares a later close, a second evening lane and no change.
4. Costs: sets out the staff cost and the extra income.
5. Recommendation: asks for approval and names the start date.

## Key numbers
| Value | What it is | Where |
|---|---|---|
| 90% | evening slots filled | Summary, paragraph 1; Demand, paragraph 2 |
| 340 | swimmers turned away each month | Demand, paragraph 3 (Summary, paragraph 2 says 430: conflict) |
| $48,000 | staff cost a year | Summary, paragraph 1; Costs, paragraph 1 |
| $31,000 | extra income a year | Costs, paragraph 2 |

## Key terms
| Use | Avoid | Meaning |
|---|---|---|
| evening slot | late session, night swim | a 45-minute booking after 18:00 |
| lane hire | lane rental | a club's booking of a whole lane |
```
