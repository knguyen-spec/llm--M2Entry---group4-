# 0004: Evaluation and strategy choice

- **Status:** proposed. Figures pending a model run.
- **Date:** 2026-11-09
- **Author:** [the member who will defend this record; the README assigns it to Sereine Tawamba]
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

- Score labels by exact match after normalisation (`src/evaluate.py`, `src/metrics.py`).
- Use a judge from a different model than the component's, on the four criteria in
  `evals/rubric.md` (`prompts/judge.md`). Judge each pair in both orders; a
  preference counts only when both orders agree.
- Choose the strategy from the 30-case results: the one with the fewest errors
  on the checked cases, unless a cheaper one is within noise, in which case the
  cheaper one.

## Evidence

Pending. For each figure, record the model, date, parameters and test file:

- Right answers out of 30, per strategy: pending run.
- Judge agreement with our own scores on ten cases: pending run.
- Verdicts changed by the swap: pending run.
- Cost per 1,000 calls from `runs/`: pending run.
- Median and p90 latency: pending run.

A local run on `llama3.2:3b` (2026-11-09) is not used as evidence: 20 of its 30
cases had not been checked by a person (`docs/evaluation.md`).

## Consequences

- **Cost:** two judge calls per comparison, on top of the component's calls.
- **Limit:** 30 cases separate strategies only when they differ by more than
  about one ticket (3.3 points per ticket).
- **Limit:** the judge is calibrated only on the ten cases we score ourselves.
- **Revisit if:** the chosen strategy misses the target on the failure
  categories we read, or the judge disagrees with our own scores on more than a
  few of the ten calibration cases.
