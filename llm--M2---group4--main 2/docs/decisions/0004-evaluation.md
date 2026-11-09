# 0004: Evaluation and strategy choice

- **Status:** accepted
- **Date:** 2026-11-09
- **Author:** Lynn-Aurea Niat. Reviewed by Sereine Tawamba.
- **Lesson:** L04

## Context

The classifier returns one of seven labels, a confidence and a review flag
(`docs/decisions/0001`, `src/schema.py`). We need to know how often it is right,
what it costs, and whether it can run without a person reading every answer.
We must also choose between three prompting strategies: zero-shot, few-shot and
chain-of-thought.

## Options considered

| Option | For | Against |
|---|---|---|
| Exact label match only | No model, cheap, reproducible | Says nothing about the confidence or the review decision |
| Model judge only | Scores the review decision and format too | Costs calls; a judge can favour the first answer it sees |
| Exact match, plus a judge from another model, in both orders | Label accuracy without a model; the judge covers what exact match cannot; the swap catches position bias | Two judge calls per comparison |

## Decision

- Score labels by exact match after normalisation (`src/evaluate.py`, `src/metrics.py`), reported two ways: expected label only, and expected or second acceptable label.
- Use a judge from a different, larger model (`anthropic/claude-sonnet-4.5`) on the four criteria in `evals/rubric.md`. Judge each pair in both orders; a preference counts only when both orders agree.
- Trust the judge as a second reading on format and correctness only; the review decision is checked by code, because the judge agreed with us on it only 5 times out of 10.
- Choose the few-shot strategy: accuracy is within noise across the three, and few-shot is the cheapest and fastest.

## Evidence

Component `anthropic/claude-haiku-4.5` through OpenRouter, max_output_tokens 300, model-default sampling, 2026-11-09, the 30 cases of `evals/test_cases.csv`. Files in `runs/`; figures from `python -m src.summarise` and `python -m src.summarise --judge`.

| Strategy | Right /30 (with second label) | Right /30 (expected only) | Cost per 1,000 calls | p90 latency | Re-prompts | Wrong and not reviewed |
|---|---:|---:|---:|---:|---:|---:|
| Zero-shot | 28 | 27 | $1.02 | 4.47 s | 17 | 1 |
| Few-shot | 27 | 26 | $0.74 | 1.16 s | 0 | 2 |
| Chain-of-thought | 27 | 25 | $1.03 | 1.83 s | 0 | 2 |

- One case is 3.3 points: a one-case gap cannot separate the strategies.
- Judge calibration on 10 cases we scored by hand first: same score on 31 of 40 (78%); correct 8/10, grounded 8/10, review 5/10, format 10/10.
- Swap: the order changed the verdict in 15 of 90 comparisons (17%); 71 of 90 are ties. The judge prefers no strategy.
- Zero-shot's 17 re-prompts and one give-up come from its prompt (JSON in a code block followed by reasoning), not from the model.
- Failure analysis (`docs/evaluation.md`): the errors come from the prompt (no label definitions, no marketplace scope), from confident wrong answers that skip review, and from one ambiguous test case; none from missing company text.

## Consequences

- **Cost:** few-shot saves about 27% per call against zero-shot and chain-of-thought; the judge costs about $0.12 per 30 cases and runs only during evaluation.
- **Limit:** 30 cases separate strategies only when they differ by more than about one ticket.
- **Limit:** the judge is calibrated on ten few-shot answers only, scored by two people who agreed beforehand.
- **Limit:** confident errors (L04-26, L04-27) reach no person; the confidence threshold does not catch them.
- **Revisit if:** the prompt with label definitions does not remove the two unreviewed errors when the 30 cases are run again, the judge disagrees with us on more than a few new calibration cases, or a strategy pulls ahead by more than two cases.