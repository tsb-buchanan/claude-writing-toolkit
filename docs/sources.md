# Sources

This page says where the toolkit's rules come from.

## Where the rules come from

1. Most rules began as one writer's style notes for a PhD thesis, and the Claude Code commands that applied them. The toolkit keeps the general rules. Every value that differs between writers moved into the profile. Nothing from that thesis is in this repo.
2. Three research papers on text written by language models add seven rules, and rule out four ideas. They are listed below.

None of the three papers studies how to write a report or a thesis. They study detectors, chat templates and fiction. So each rule below is our reading of a finding. It is not a finding of the paper.

## 1. Human texts are outliers

Cong Zeng, Shengkun Tang, Yuanzhou Chen, Zhiqiang Shen, Wenchao Yu, Xujiang Zhao, Haifeng Chen, Wei Cheng and Zhiqiang Xu (2025). Human Texts Are Outliers: Detecting LLM-generated Texts via Out-of-distribution Detection. NeurIPS 2025. https://arxiv.org/abs/2510.08602

What it found:

1. Text from language models clusters tightly, because it comes from a few models with shared habits. Human text is far more varied.
2. So the authors build detectors that model the machine side, and treat human text as the outlier.
3. The paper names no feature that makes a text read as human. There is no single human style to aim at.

What the toolkit takes from it:

1. Every change follows a rule in the skill or in the writer's profile. "Sounds more human" is never a reason. (human-write)
2. Prefer the specific to the generic. Each paragraph should name a case, a number, a name or a source, because generic sentences are the ones any model would write. human-write flags a paragraph that names nothing specific. It cannot add the fact, because only the writer knows it.

What the toolkit does not take: varying sentence length or word choice on purpose, so that text looks less like a machine's. The paper finds no human profile to copy, and the idea goes against the sentence limit.

## 2. The price of format

Longfei Yun, Chenyang An, Zilong Wang, Letian Peng and Jingbo Shang (2025). The Price of Format: Diversity Collapse in LLMs. Findings of the Association for Computational Linguistics: EMNLP 2025, pages 15454 to 15468. https://aclanthology.org/2025.findings-emnlp.836/ (also https://arxiv.org/abs/2505.18949)

What it found:

1. The chat template of an instruction-tuned model narrows what it writes. Given different open-ended prompts, the model gives answers with similar content.
2. The same prompts without the template get more varied answers. A higher sampling temperature does not remove the effect.

What the toolkit takes from it: one rewrite prompt, run over many sections, can make them sound alike. doc_stats.py lists each paragraph opening used three times or more, and doc-check reports a repeated linking phrase, such as "In addition,". The fix is human-write on those sections, where each paragraph leads with its own claim.

What the toolkit does not take:

1. Varying paragraph length on purpose. The paper says nothing about paragraph length.
2. Irregular structure on purpose. The paper measures the content of answers, not the shape of text. Irregular structure also goes against the order that doc-flow checks.

## 3. StoryScope

Jenna Russell, Rishanth Rajendhran, Chau Minh Pham, Mohit Iyyer and John Wieting (2026). StoryScope: Investigating idiosyncrasies in AI fiction. https://arxiv.org/abs/2604.03136

What it found:

1. About 10,000 writing prompts were each answered by a person and by five language models. Narrative choices alone, without surface style, tell most of the human stories from the model ones.
2. Model stories state their theme outright more often, and they tie up loose ends. They show a feeling through bodily sensations, where people more often name it. People refer to specific outside works about twice as often.
3. The study covers fiction only. The rules below carry its findings over to reports and theses by analogy.

What the toolkit takes from it:

1. Say what a result means once, where the section concludes, not at the end of each paragraph. (human-write)
2. Keep limits and exceptions in view. A rewrite never cuts or softens a stated limitation. (human-write)
3. Name the work you build on: its authors, its year and its result, not "previous studies". doc-check reports a pointer that names no work. human-write never adds a citation, so the writer fills it in.
4. Say what a method or a model does in literal words, not in a metaphor such as "the model struggles". (human-write)

What the toolkit does not take: nonlinear order, moral ambiguity and the other devices of fiction. They go against leading with the claim, and against a clear order.

## What this means for a writer

1. The skills never edit to fool an AI detector. The aim is a clear document that says what you mean.
2. These rules are defaults. Your profile's house rules and your own notes win over them.
