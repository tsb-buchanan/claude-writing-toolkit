# Planted problems: sample thesis chapter

The sample is an invented thesis chapter about the number of return desks at a fictional tool library. It uses a standard textbook queueing model. Chapter 3 has about 1,000 words of prose plus equations. Chapter 2 is a half-page stub that sets the notation.

Files:

1. main.tex, ch2-background.tex, ch3-desks.tex and refs.bib: the LaTeX source. All references are invented.
2. built/thesis.pdf: made by `python3 tools/build_samples.py`.
3. doc-profile.md: the profile the tests use.

Places are given as section number and paragraph number in Chapter 3. Paragraphs are counted from 1 in each section. Display equations belong to the paragraph around them. Headings and tables do not count.
LaTeX writes an en dash as two hyphens, so the planted en dash (TH11) is plain ASCII in the source.

## The problems

| ID | Problem | Where | The truth |
|---|---|---|---|
| TH01 | The chapter's claim appears only at the end. The introduction never states it. | 3.6, paragraph 1 | The claim: one desk keeps the mean wait under 3 minutes below 10 returns an hour, and two desks up to about 28. |
| TH02 | A symbol variant: $\Lambda$ for the arrival rate. | 3.5, paragraph 3 (Equation eq:saturday) | It is $\lambda$ everywhere else. |
| TH03 | A symbol clash: $N$ is the number of desks, but also the mean number of borrowers. | 3.3, paragraph 3 (Equation eq:little and "$N = 0.67$") | Chapter 2 is the notation source, so $N$ stays the number of desks. The mean number of borrowers needs its own symbol ($L$ is usual). That choice is the writer's. |
| TH04 | A symbol used before its definition: $W$, the time in system. | Used in 3.2, paragraph 4; defined in 3.3, paragraph 1 | The profile asks for a definition at first use in each chapter. |
| TH05 | An equation, a citation and cross-references inside text that needs rewriting. | 3.3, paragraph 2 (eq:wq, \cite{example2021}, \eqref{eq:erlang2}, \ref{sec:logs}) | The prose may change. The equation, citation and references may not. |
| TH06 | A section adapted from a published paper, marked keep light. It holds a voice slip ("We propose"), a banned word ("clearly") and a 45-word sentence. | 3.4, all of it | Light passes only: fix the voice (and credit the supervisor) and cut "clearly". The long sentence stays. |
| TH07 | Voice slips in a thesis written as "I". | 3.1, paragraph 2 ("we will"); 3.2, paragraph 1 ("We assume"); 3.5, paragraph 1 ("our model") | Use "I". |
| TH08 | A repeated paragraph, word for word. | 3.1, paragraph 4; 3.5, paragraph 2 | Keep the first. Cut the second. |
| TH09 | A broken handoff. | 3.2, paragraph 4, last sentence ("Section 3.3 compares the model with the desk logs.") | Section 3.3 derives the waiting times. The comparison is in 3.5. |
| TH10 | A result in the method section: the 2.0-minute mean wait that "matched the desk logs closely". | 3.2, paragraph 4 | It belongs in 3.5. |
| TH11 | An en dash range: "16--22 per hour". | 3.5, paragraph 1 | Write "16 to 22 per hour". |
| TH12 | A false alarm. "Waiting time" ($W_q$) and "time in system" ($W$) look like two names for one thing, but they are two defined measures. | Defined in 3.3, paragraph 1; both used correctly in 3.5, paragraph 4 | Not a problem. A check must not report it, and a rewrite must not merge the terms. |
| TH13 | A broken house rule: an equation in the chapter's first section. | 3.1, paragraph 3 ("$\rho = \lambda/(N\mu)$") | House rule: no equations in a chapter's first section. |
| TH14 | A number format slip: "2 desks" should be "two desks". | 3.2, paragraph 2 | Fix the format. |
| TH15 | Filler and banned words: "It is worth noting", "clearly", "very"; and "clearly" inside the keep light section. | 3.3, paragraph 2; 3.4, paragraph 2 | Cut them. In 3.4, only by a light pass. |
| TH16 | A sentence far over 25 words (65 words, around Equation eq:wq). | 3.3, paragraph 2 | Split it without touching the equation. |
| TH17 | A claim without a source. | 3.1, paragraph 1 ("Most tool libraries in the region report the same problem.") | Needs a source, or a softer claim. |

## Also in the chapter, and not a problem

1. The contribution statement for the adapted section is present (3.4, paragraph 1). A check must not report it missing.
2. Equations eq:util (3.2) and eq:rho (Chapter 2) are the same formula. That is deliberate.

## Sentences over 25 words

| Words | Where | Note |
|---|---|---|
| 31 | 3.1, paragraph 1 | "Members borrow drills, ..." |
| 29 | 3.1, paragraph 2 | the roadmap sentence, with the voice slip |
| 31 | 3.2, paragraph 1 | "We assume that returns arrive ..." |
| 30 | 3.2, paragraph 1 | "Exponential service times suit this setting, ..." |
| 65 | 3.3, paragraph 2 | planted (TH16) |
| 45 | 3.4, paragraph 2 | inside keep light: must stay |
| 29 | 3.5, paragraph 1 | "Each log records ..." |
| 27 | 3.5, paragraph 5 | "If a check took 4 minutes ..." |

## The numbers are consistent

The model's numbers follow from the equations with $\mu = 20$ returns per hour:

1. One desk, $\lambda = 8$: $W_q = 0.4/12$ hours, or 2.0 minutes. Little's law gives 0.67 borrowers.
2. One desk meets the 3-minute target while $\lambda < 10$.
3. Two desks, $\lambda = 18$: $P_w = 0.279$ and $W_q = 0.76$ minutes. At $\lambda = 22$: 1.3 minutes. Two desks meet the target up to about 28 returns per hour.
4. With $\mu = 15$, one desk meets the target only below about 6 returns per hour.

A check that reports one of these as wrong has made a mistake.
