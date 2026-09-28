# Planted problems: sample report

The sample is an invented report to the board of a fictional grocer, about a pilot of reusable delivery crates. It has about 1,800 words in six sections.

Files:

1. source.md: the text. Planted dashes are written as {emdash}, so the repo holds no dash characters.
2. built/report.md, built/report.docx and built/report.pdf: made by `python3 tools/build_samples.py`.
3. doc-profile.md: the profile the tests use.

Places are given as section, subsection and paragraph number. Paragraphs are counted from 1 in each section or subsection. Headings and the table do not count.
In the Word file, the keep mark and the note are Word comments. In the Markdown file, they are HTML comments. The PDF shows neither.

## The problems

| ID | Problem | Where | The truth |
|---|---|---|---|
| RP01 | The main message is buried at the end. The summary never gives the recommendation. | Recommendation and next steps, paragraph 1 | The report's message: roll out reusable crates to all four depots from April. |
| RP02 | A number differs between two sections: 18,400 orders against 18,900. | Summary, paragraph 2; Results > Cost per order, paragraph 1 | 18,900 is right. |
| RP03 | A number differs between two sections: 84% preferred crates against 81%. | Summary, paragraph 3; Results > Customer response, paragraph 1 | 81% is right. |
| RP04 | One concept under two names: "totes" and "crates". | Background, paragraph 5; Results > Customer response, paragraph 1 | "crates" everywhere. The Customer response case is a plain error. The Background case describes competitors, but it should still say "crates". |
| RP05 | A repeated paragraph, word for word. | How the pilot worked, paragraph 5; Results > Returns and losses, paragraph 2 | Keep the first. Cut the second. |
| RP06 | Filler and banned words: "It is very clear that", "very", "going forward"; "In order to"; "It is important to note that", "basically"; "leverage". | Background, paragraphs 3 and 6; Results > Cost per order, paragraph 3; Results > Driver time, paragraph 1 | Cut them. |
| RP07 | Three sentences far over 25 words: 59, 54 and 51 words. | Background, paragraph 1; Results > Cost per order, paragraph 3; Results > Driver time, paragraph 1 | Split them. |
| RP08 | A signpost. | How the pilot worked, paragraph 1 ("In this section we will describe...") | Cut it. |
| RP09 | A recap. | Results > Driver time, paragraph 3, first sentence ("In summary, as we have seen above, ...") | Cut it. |
| RP10 | A broken handoff. | Results > Driver time, paragraph 3, second sentence ("The next section looks at what customers said about the crates.") | The next section is about risks and costs. Customer response is already covered in Results. |
| RP11 | A claim without a source. | Background, paragraph 3 ("Most shoppers now say they would switch to a grocer that uses less packaging.") | Needs a source, or a softer claim. |
| RP12 | An em dash. | Risks and costs of a full rollout, paragraph 2 ("loss" followed by an em dash) | Use a colon or a new sentence. |
| RP13 | A keep passage: the quoted contract clause. It says "twenty-four months", which breaks the number rule, but it is a quotation. | How the pilot worked, paragraph 4 | Nothing in it may change. |
| RP14 | A writer's note against the obvious suggestion: keep "Options we rejected" in place, because the board asked for it. | Risks and costs of a full rollout > Options we rejected (the note sits on the heading) | doc-flow would otherwise suggest cutting the subsection or moving it to an appendix. The note wins. |
| RP15 | Number format slips: "twelve weeks" should be "12 weeks"; "3 staff" should be "three staff". | How the pilot worked, paragraphs 2 and 6 | Fix the format. The values stay. |
| RP16 | A voice slip: "I think" in a report written as "we". | Results > Customer response, paragraph 2 | Use "we". |
| RP17 | A result in the method section: 2% of crates damaged by week six. | How the pilot worked, paragraph 7 | It belongs in Results. |
| RP18 | A table and a footnote that the Word script must leave alone. | The table in Results > Cost per order; the footnote on "deposit" in How the pilot worked, paragraph 3 | No change to either. |
| RP19 | A bold first sentence in the recommendation. Not a problem: a formatting check. | Recommendation and next steps, paragraph 1 | A rewrite keeps the bold. |

## Sentences just over 25 words

These are not planted, but a check will find them. A rewrite may keep each one with a short reason, or split it.

| Words | Where |
|---|---|
| 28 | How the pilot worked, paragraph 7 |
| 26 | Results > Cost per order, paragraph 1 |
| 26 | Results > Returns and losses, paragraph 3 |
| 28 | Results > Driver time, paragraph 3 (the recap sentence, RP09) |
| 29 | Risks and costs of a full rollout, paragraph 3 |

## Numbers that must never change

18,400 and 18,900 orders (report both, fix neither), 84% and 81% (the same), 1,500 orders a day, four depots, $1.9 million, 22%, 2030, $61,000, 225 orders a day, 4,200 crates, $9.50, $5, Clause 7.2, 30 days, 2%, 3%, $1.42, $0.98, 31%, $0.10, $0.52, $0.36, $1.05, $0.97, $0.93, 200 uses, 96%, 4%, 1,140 customers, 12%, 7%, 40 seconds, 28 stops, 19 minutes, 28,000 crates, 70%, 1.2 liters, $304,000, $266,000, $30,000, $8,000, $0.44, $19,800, 15 months, 8%.

Only their format may change, and only to meet the number rule. Numbers inside the keep passage never change.

## Slips found later

These were not planted. The full check found them in the invented numbers. A check that reports them is right, and a test counts them as correct findings.

| Where | Slip |
|---|---|
| Background, paragraph 2 | $1.9 million a year on boxes does not fit 1,500 orders a day at $1.42 per order. That gives about $777,000. |
| Risks and costs of a full rollout, paragraph 1; Recommendation and next steps, paragraph 3 | 28,000 crates is enough for all four depots (4,200 / 225 x 1,500), yet Eastside keeps its crates from the pilot. |
| Recommendation and next steps, paragraphs 2 and 3 | The crates are ordered in February, before the board approves the money in March. |
| Results > Cost per order, paragraph 3 | The 200-use life that the 31% rests on has no named source. |
